"""Load and resolve the design parameter files."""
from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    """Walk up from this file until we find params.yaml."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "params.yaml").exists():
            return parent
    raise FileNotFoundError("params.yaml not found - run from inside the project")


def _load(relpath: str) -> dict[str, Any]:
    path = project_root() / relpath
    if not path.exists():
        raise FileNotFoundError(f"missing {relpath}")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_params() -> dict[str, Any]:
    return _load("params.yaml")


def load_loadout() -> list[dict[str, Any]]:
    return _load("components/loadout.yaml").get("items", [])


def material_density(name: str) -> float:
    """g/cm^3 for a named material."""
    table = _load("components/materials.yaml")["densities"]
    if name not in table:
        raise KeyError(f"unknown material {name!r}; known: {', '.join(sorted(table))}")
    return float(table[name])


def stock_half_extents(p: dict[str, Any]) -> tuple[float, float]:
    """(half_width, half_diagonal) of the raw stock, in mm."""
    w, h = p["stock"]["size_mm"]
    return min(w, h) / 2.0, math.hypot(w / 2.0, h / 2.0)


def screw_diameter_mm(designation: str) -> float:
    """Nominal shank diameter of an ISO metric screw. 'M2' -> 2.0, 'M2.5' -> 2.5."""
    text = str(designation).strip().upper()
    if not text.startswith("M"):
        raise ValueError(f"screw {designation!r} is not an ISO metric designation like 'M2'")
    try:
        dia = float(text[1:])
    except ValueError as exc:
        raise ValueError(f"cannot read a diameter out of screw {designation!r}") from exc
    if dia <= 0:
        raise ValueError(f"screw {designation!r} has a non-positive diameter")
    return dia


def hole_diameter_mm(p: dict[str, Any], designation: str) -> float:
    """Finished hole size for a screw: nominal + the clearance from params.yaml.

    This is the size you want to MEASURE in the wood afterwards. It is not the
    toolpath diameter - the cutter takes kerf/2 off every edge, so a hole cut at
    D comes out at D + kerf. Kerf compensation belongs to whatever generates the
    toolpath, not here.
    """
    clearance = float(p.get("holes", {}).get("screw_clearance_mm", 0.0))
    return round(screw_diameter_mm(designation) + clearance, 3)
