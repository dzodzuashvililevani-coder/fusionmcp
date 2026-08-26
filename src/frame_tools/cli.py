"""Command line entry point.

    frame report | geometry | mass | check | fusion | kerf-test
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import dxf_out, fusion, geometry, mass, params, thrust, validate

BAR = "-" * 62
DEFAULT_FUSION_JSON = "fusion_scripts/frame_params.json"


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
    return 1 if fails else 0


def cmd_report(args) -> int:
    cmd_geometry(args); print()
    cmd_mass(args); print()
    return cmd_check(args)


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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="frame", description=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    for name, fn, help_ in [
        ("report", cmd_report, "everything (default)"),
        ("geometry", cmd_geometry, "arm length and motor positions"),
        ("mass", cmd_mass, "mass budget and centre of gravity"),
        ("check", cmd_check, "pre-cut design validation"),
        ("fusion", cmd_fusion, "resolved parameters as JSON for Fusion"),
        ("kerf-test", cmd_kerf_test, "write dxf/kerf_test.dxf to calibrate your cutter"),
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
    args = ap.parse_args(argv)
    try:
        return (args.func if args.cmd else cmd_report)(args)
    except (FileNotFoundError, ImportError, KeyError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
