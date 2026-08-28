"""Command line entry point.

    frame report | geometry | mass | check | fields | set | fusion | kerf-test | ui
"""
from __future__ import annotations

import argparse
import importlib
import json
import socket
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path
from typing import Any

from fcc.errors import FccError
from fcc.fields import FieldSpec, coerce_value, current_value, field_by_id, is_todo_guess, load_fields
from fcc.writer import locate, write_value
from . import dxf_out, fusion, geometry, mass, params, thrust, validate

BAR = "-" * 62
DEFAULT_FUSION_JSON = "fusion_scripts/frame_params.json"
UI_HOST = "127.0.0.1"
DEFAULT_UI_PORT = 8765
WEB_BUILD_COMMAND = "npm.cmd --prefix web install; npm.cmd --prefix web run build"


def _build_all():
    p = params.load_params()
    lay = geometry.solve(p)
    m = mass.build(p, lay, params.load_loadout())
    t = thrust.build(p, m.total_mass_g)
    return p, lay, m, t


def cmd_geometry(_args) -> int:
    p, lay, _, _ = _build_all()
    print(BAR)
    print(f"LAYOUT  ({p['motors']['count']} motors, {p['motors']['layout'].upper()} config)")
    print(BAR)
    src = "auto-solved (shortest arms that clear everything)" if lay.auto_solved else "set in params.yaml"
    binds = "prop-to-prop" if lay.min_radius_props_mm >= lay.min_radius_plate_mm else "plate corner"
    print(f"  arm radius          {lay.motor_radius_mm:>8.1f} mm   [{src}]")
    print(f"    allowed range     {lay.min_radius_mm:>8.1f} .. {lay.max_radius_mm:.1f} mm")
    print(f"    minimum set by    {binds:>8} (props {lay.min_radius_props_mm:.1f}, "
          f"plate {lay.min_radius_plate_mm:.1f})")
    print(f"  motor-to-motor diag {lay.diagonal_mm:>8.1f} mm   <- your frame class")
    print(f"  adjacent spacing    {lay.adjacent_spacing_mm:>8.1f} mm")
    print(f"  prop tip gap        {lay.prop_tip_gap_mm:>8.1f} mm")
    print(f"  prop-to-plate gap   {lay.plate_prop_gap_mm:>8.1f} mm")
    print(f"  exposed arm length  {lay.arm_length_mm:>8.1f} mm")
    print("\n  motor positions (x right, y forward, mm):")
    for name, x, y in lay.motors:
        print(f"    {name:<12} ({x:>7.2f}, {y:>7.2f})")
    return 0


def cmd_mass(_args) -> int:
    _, lay, m, _ = _build_all()
    print(BAR)
    print("MASS BUDGET")
    print(BAR)
    for it in sorted(m.items, key=lambda i: -i.mass_g):
        pct = 100 * it.mass_g / m.total_mass_g
        print(f"  {it.name:<20} {it.mass_g:>7.1f} g  {pct:>5.1f}%   "
              f"@ ({it.x:>7.1f},{it.y:>7.1f},{it.z:>5.1f})")
    print(BAR)
    print(f"  {'ALL-UP WEIGHT':<20} {m.total_mass_g:>7.1f} g")
    print(f"  wood cut area        {m.frame_area_mm2:>7.0f} mm^2")
    print(f"  CG offset from centre {m.cg_offset_mm:>6.2f} mm  "
          f"(x{m.cg_x_mm:+.2f}, y{m.cg_y_mm:+.2f}, z{m.cg_z_mm:+.2f})")
    return 0


def cmd_check(_args) -> int:
    p, lay, m, t = _build_all()
    checks = validate.run(p, lay, m, t)
    fails, _ = _print_checks(checks)
    return 1 if fails else 0


def _print_checks(checks: list[validate.Check]) -> tuple[int, int]:
    print(BAR)
    print("PRE-CUT CHECKS")
    print(BAR)
    icons = {"OK": "[ ok ]", "WARN": "[warn]", "FAIL": "[FAIL]"}
    for c in checks:
        print(f"  {icons[c.status]} {c.name}")
        print(f"         {c.detail}")
    fails = sum(1 for c in checks if c.status == "FAIL")
    warns = sum(1 for c in checks if c.status == "WARN")
    print(BAR)
    print(f"  {len(checks) - fails - warns} passed, {warns} warnings, {fails} failures")
    if fails:
        print("  >> Do not cut yet. Fix the failures in params.yaml first.")
    return fails, warns


def cmd_report(args) -> int:
    cmd_geometry(args); print()
    cmd_mass(args); print()
    return cmd_check(args)


def cmd_fields(_args) -> int:
    root = params.project_root()
    fields = load_fields(root=root)
    print(BAR)
    print("MEASUREMENT FIELDS")
    print(BAR)
    for field in fields:
        value = _display_value(current_value(field, root=root), field.unit)
        status = "TODO guess" if is_todo_guess(field, root) else "measured"
        line_number, _ = locate(field, root=root)
        print(f"  {field.id:<26} {value:<14} [{status}] {field.file}:{line_number}")
        print(f"         {field.question}")
    return 0


def cmd_set(args) -> int:
    root = params.project_root()
    field = field_by_id(args.id, root=root)
    value = coerce_value(field, args.value)
    range_warning = _range_warning(field, value)
    result = write_value(field, value, root=root)

    print(BAR)
    print("FIELD WRITE")
    print(BAR)
    print(f"  field               {field.id}")
    print(f"  value               {_display_value(value, field.unit)}")
    print(f"  changed             {result.file}:{result.line_number}")
    print(f"    - {result.old_text.rstrip()}")
    print(f"    + {result.new_text.rstrip()}")
    if field.measurement_label:
        status = "ticked" if result.checklist_ticked else "already current"
    else:
        status = "no checklist"
    print(f"  checklist           {status}")
    if range_warning:
        print(f"  [warn] {range_warning} Value saved anyway.")

    print()
    p, lay, m, t = _build_all()
    fails, _ = _print_checks(validate.run(p, lay, m, t))
    if fails:
        print("  >> This design does not currently validate. The measurement was saved; fix the design next.")
    return 0


def cmd_fusion(args) -> int:
    """Dump resolved numbers as JSON - feed the MCP, or let a Fusion script read it."""
    p, lay, m, t = _build_all()
    payload = fusion.build_payload(p, lay, m, t, validate.run(p, lay, m, t))
    text = json.dumps(payload, indent=2)

    out = getattr(args, "out", None)
    if out is not None:
        path = Path(out) if out else params.project_root() / DEFAULT_FUSION_JSON
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text + "\n", encoding="utf-8")
        print(f"wrote {path}")
    else:
        print(text)

    if payload["checks"]["failures"]:
        print("warning: this design still fails "
              f"{', '.join(payload['checks']['failures'])} - do not cut from it",
              file=sys.stderr)
    return 0


def cmd_kerf_test(args) -> int:
    """Write the kerf calibration coupon. Cut it, measure it, update params.yaml."""
    p = params.load_params()
    out = Path(args.out) if args.out else params.project_root() / "dxf" / "kerf_test.dxf"
    path, nominal = dxf_out.write_kerf_test(p, out)
    print(f"wrote {path}")
    print(f"  {len(nominal)} squares, nominal {nominal[0]}..{nominal[-1]}mm, engraved with their size")
    print(f"  current stock.kerf_mm = {p['stock']['kerf_mm']}mm ({p['stock']['cut_method']})")
    print("  Cut it, measure a square with calipers, kerf = nominal - measured.")
    return 0


def cmd_ui(args) -> int:
    root = params.project_root()
    dist = root / "web" / "dist"
    index = dist / "index.html"
    if not index.exists():
        print(
            f"error: web build not found at {index}. Run: {WEB_BUILD_COMMAND}",
            file=sys.stderr,
        )
        return 2
    if not _port_available(UI_HOST, args.port):
        print(f"error: {UI_HOST}:{args.port} is already in use", file=sys.stderr)
        return 2

    try:
        create_app, static_files, build_report, uvicorn = _load_web_stack()
    except ImportError as exc:
        print(
            f"error: install the web extra before running `frame ui`: {exc}",
            file=sys.stderr,
        )
        print('       .\\.venv\\Scripts\\python.exe -m pip install -e ".[web]"', file=sys.stderr)
        return 2

    app = create_app(report_provider=lambda: build_report(root), root=root)
    app.mount("/", static_files(directory=dist, html=True), name="web")
    url = f"http://{UI_HOST}:{args.port}/"

    print(BAR)
    print("FRAME UI")
    print(BAR)
    print(f"  serving             {url}")
    print(f"  build               {dist}")
    print("  browser             disabled" if args.no_browser else "  browser             opening")

    return _run_ui_server(uvicorn, app, args.port, open_browser=not args.no_browser, url=url)


def _display_value(value: Any, unit: str) -> str:
    if isinstance(value, float):
        text = f"{value:g}"
    else:
        text = str(value)
    return f"{text} {unit}" if unit else text


def _range_warning(field: FieldSpec, value: int | float) -> str | None:
    if field.min <= value <= field.max:
        return None
    low = f"{field.min:g}"
    high = f"{field.max:g}"
    return f"{field.id} is outside the expected {low}..{high} {field.unit} range."


def _load_web_stack():
    create_app = importlib.import_module("fcc.api.app").create_app
    static_files = importlib.import_module("fastapi.staticfiles").StaticFiles
    build_report = importlib.import_module("frame_tools.report_api").build_report
    uvicorn = importlib.import_module("uvicorn")
    return create_app, static_files, build_report, uvicorn


def _run_ui_server(uvicorn_module, app, port: int, *, open_browser: bool, url: str) -> int:
    ready_url = f"http://{UI_HOST}:{port}/api/health"
    server = threading.Thread(
        target=_run_uvicorn,
        args=(uvicorn_module, app, UI_HOST, port),
        daemon=True,
    )
    server.start()
    if not _wait_for_health(ready_url):
        print(f"error: frame ui did not answer {ready_url}", file=sys.stderr)
        return 2
    if open_browser:
        webbrowser.open(url)
    try:
        while server.is_alive():
            server.join(0.5)
    except KeyboardInterrupt:
        print("\n  stopped")
        return 0
    return 0


def _run_uvicorn(uvicorn_module, app, host: str, port: int) -> None:
    uvicorn_module.run(app, host=host, port=port)


def _wait_for_health(url: str, *, timeout_s: float = 10.0) -> bool:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as response:
                if response.status == 200:
                    return True
        except OSError:
            time.sleep(0.1)
    return False


def _port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            probe.bind((host, port))
        except OSError:
            return False
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="frame", description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    for name, fn, help_ in [
        ("report", cmd_report, "everything (default)"),
        ("geometry", cmd_geometry, "arm length and motor positions"),
        ("mass", cmd_mass, "mass budget and centre of gravity"),
        ("check", cmd_check, "pre-cut design validation"),
        ("fields", cmd_fields, "measurement fields and current values"),
        ("fusion", cmd_fusion, "resolved parameters as JSON for Fusion"),
        ("kerf-test", cmd_kerf_test, "write dxf/kerf_test.dxf to calibrate your cutter"),
        ("ui", cmd_ui, "serve the browser measurement workstation"),
    ]:
        sp = sub.add_parser(name, help=help_)
        sp.set_defaults(func=fn)
        if name == "fusion":
            sp.add_argument(
                "-o", "--out", nargs="?", const="", metavar="PATH",
                help=f"write to a file instead of stdout (default {DEFAULT_FUSION_JSON})",
            )
        if name == "kerf-test":
            sp.add_argument("-o", "--out", metavar="PATH", default=None,
                            help="output path (default dxf/kerf_test.dxf)")
        if name == "ui":
            sp.add_argument("--no-browser", action="store_true", help="serve without opening a browser")
            sp.add_argument("--port", type=int, default=DEFAULT_UI_PORT, help=f"port (default {DEFAULT_UI_PORT})")
    sp = sub.add_parser("set", help="write one measurement value and run checks")
    sp.add_argument("id", help="field id from `frame fields`")
    sp.add_argument("value", help="measured value")
    sp.set_defaults(func=cmd_set)
    args = ap.parse_args(argv)
    try:
        return (args.func if args.cmd else cmd_report)(args)
    except (FccError, FileNotFoundError, ImportError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
