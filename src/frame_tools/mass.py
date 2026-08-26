"""Mass budget and centre of gravity.

On a multirotor the CG must sit at the thrust centre (the geometric centre of
the four motors). Every millimetre of offset is trim the flight controller has
to hold with differential thrust, which costs authority and flight time.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .geometry import Layout
from .params import material_density


@dataclass
class Item:
    name: str
    mass_g: float
    x: float
    y: float
    z: float


@dataclass
class MassReport:
    items: list[Item]
    frame_mass_g: float
    frame_area_mm2: float
    total_mass_g: float          # AUW, all-up weight
    cg_x_mm: float
    cg_y_mm: float
    cg_z_mm: float
    cg_offset_mm: float          # horizontal distance from the thrust centre


def estimate_frame_mass(p: dict[str, Any], layout: Layout) -> tuple[float, float]:
    """(mass_g, cut_area_mm2) for the wooden parts.

    Modelled as one centre plate plus four tapered arms. Approximate - it
    ignores lightening holes and the plate/arm overlap, so it errs heavy.
    """
    plate_w, plate_h = p["center_plate"]["size_mm"]
    plate_area = plate_w * plate_h

    tip_w = float(p["arm"]["width_mm"])
    root_w = float(p["arm"]["root_width_mm"])
    arm_area = max(layout.arm_length_mm, 0.0) * (tip_w + root_w) / 2.0

    area = plate_area + 4 * arm_area
    thickness = float(p["stock"]["thickness_mm"])
    density = material_density(p["stock"]["material"])

    # mm^2 * mm = mm^3; /1000 -> cm^3; * g/cm^3 -> g
    return area * thickness / 1000.0 * density, area


def build(p: dict[str, Any], layout: Layout, loadout: list[dict]) -> MassReport:
    items: list[Item] = []

    for name, x, y in layout.motors:
        items.append(Item(name, float(p["motors"]["mass_g"]), x, y, float(p["stock"]["thickness_mm"])))

    frame_mass, frame_area = estimate_frame_mass(p, layout)
    items.append(Item("frame_wood", frame_mass, 0.0, 0.0, 0.0))

    b = p["battery"]
    items.append(Item("battery", float(b["mass_g"]), 0.0, 0.0, 20.0))

    for it in loadout:
        x, y, z = it.get("pos_mm", [0, 0, 0])
        items.append(Item(it["name"], float(it["mass_g"]), float(x), float(y), float(z)))

    total = sum(i.mass_g for i in items)
    if total <= 0:
        raise ValueError("total mass is zero - fill in the mass_g fields")

    cx = sum(i.mass_g * i.x for i in items) / total
    cy = sum(i.mass_g * i.y for i in items) / total
    cz = sum(i.mass_g * i.z for i in items) / total

    return MassReport(
        items=items,
        frame_mass_g=frame_mass,
        frame_area_mm2=frame_area,
        total_mass_g=total,
        cg_x_mm=cx,
        cg_y_mm=cy,
        cg_z_mm=cz,
        cg_offset_mm=math.hypot(cx, cy),
    )
