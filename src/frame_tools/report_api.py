"""Build the drone-specific report model for the FCC API."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from fcc.api.models import CheckModel, HeadlineItem, Report

from . import geometry, mass, params, thrust, validate

OPENAPI_JSON = "web/src/openapi.json"


def build_report(root: Path | None = None) -> Report:
    root = root or params.project_root()
    p = _load_yaml(root, "params.yaml")
    lay = geometry.solve(p)
    m = mass.build(p, lay, _load_yaml(root, "components/loadout.yaml").get("items", []))
    t = thrust.build(p, m.total_mass_g)
    checks = validate.run(p, lay, m, t)
    return Report(
        headline=[
            HeadlineItem(label="Arm radius", value=round(lay.motor_radius_mm, 1), unit="mm"),
            HeadlineItem(label="All-up weight", value=round(m.total_mass_g, 1), unit="g"),
            HeadlineItem(label="Thrust-to-weight", value=round(t.twr, 2), unit=""),
            HeadlineItem(label="CG offset", value=round(m.cg_offset_mm, 2), unit="mm"),
        ],
        checks=[
            CheckModel(status=check.status.lower(), name=check.name, detail=check.detail)
            for check in checks
        ],
    )


def openapi_schema(root: Path | None = None) -> dict[str, Any]:
    from fcc.api.app import create_app

    root = root or params.project_root()
    return create_app(report_provider=lambda: build_report(root), root=root).openapi()


def openapi_bytes(root: Path | None = None) -> bytes:
    text = json.dumps(openapi_schema(root), indent=2)
    return (text.replace("\n", "\r\n") + "\r\n").encode("utf-8")


def write_openapi(path: Path | None = None, root: Path | None = None) -> Path:
    root = root or params.project_root()
    path = path or root / OPENAPI_JSON
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(openapi_bytes(root))
    return path


def _load_yaml(root: Path, relpath: str) -> dict[str, Any]:
    with (root / relpath).open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Developer tools for the FCC API report contract.")
    parser.add_argument("--write-openapi", nargs="?", const=OPENAPI_JSON, metavar="PATH")
    args = parser.parse_args(argv)
    if args.write_openapi:
        path = write_openapi(Path(args.write_openapi))
        print(f"wrote {path}")
        return 0
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
