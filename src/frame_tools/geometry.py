"""Solve the frame layout: how long the arms must be, where the motors sit.

Convention: vehicle frame, +y = nose, +x = right, origin = geometric centre.
A true X quad puts all four motors at 45/135/225/315 degrees, radius R.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any

from .params import stock_half_extents

MOTOR_ANGLES_DEG = (45.0, 135.0, 225.0, 315.0)
MOTOR_NAMES = ("front_right", "front_left", "rear_left", "rear_right")


@dataclass
class Layout:
    motor_radius_mm: float          # centre -> motor shaft
    min_radius_mm: float            # smallest R that satisfies every constraint
    min_radius_props_mm: float      # smallest R where adjacent props miss each other
    min_radius_plate_mm: float      # smallest R where the props miss the plate corners
    max_radius_mm: float            # largest R that fits the stock
    diagonal_mm: float              # motor-to-motor across, the "frame class"
    adjacent_spacing_mm: float      # motor-to-motor along a side
    prop_tip_gap_mm: float          # gap between adjacent prop tips
    plate_corner_r_mm: float        # centre -> plate corner (arms leave at 45 deg)
    prop_inner_r_mm: float          # centre -> nearest edge of a prop disc
    plate_prop_gap_mm: float        # prop inner edge - plate corner. Must stay > 0
    arm_length_mm: float            # exposed arm, plate edge -> motor
    auto_solved: bool
    motors: list[tuple[str, float, float]] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        """JSON-native types only - this goes straight out through `frame fusion`,
        so a tuple here would survive json.dumps but not a round trip."""
        d = {k: v for k, v in self.__dict__.items() if k != "motors"}
        d["motors"] = {n: [round(x, 2), round(y, 2)] for n, x, y in self.motors}
        return d


def solve(p: dict[str, Any]) -> Layout:
    d_prop = float(p["props"]["diameter_mm"])
    gap = float(p["props"]["tip_clearance_mm"])
    base_r = float(p["motors"]["base_diameter_mm"]) / 2.0

    plate_w, plate_h = p["center_plate"]["size_mm"]
    plate_inscribed_r = min(plate_w, plate_h) / 2.0
    plate_corner_r = math.hypot(plate_w / 2.0, plate_h / 2.0)

    # Two independent lower bounds on the arm radius:
    #
    # 1. Adjacent motors on an X quad are R*sqrt(2) apart. They need a full prop
    #    diameter plus the clearance gap between them.
    # 2. The arms leave the plate at 45 degrees, which on a rectangular plate is
    #    exactly where the corners are - so the prop disc has to clear the plate
    #    corner, not the plate edge. Short arms fail this long before they fail
    #    prop-to-prop, which is why it is solved for and not just checked.
    r_min_props = (d_prop + gap) / math.sqrt(2.0)
    r_min_plate = plate_corner_r + d_prop / 2.0
    r_min = max(r_min_props, r_min_plate)

    half_w, half_diag = stock_half_extents(p)
    orientation = p["arm"].get("orientation", "diagonal")
    reach = half_diag if orientation == "diagonal" else half_w
    r_max = reach - base_r

    requested = p["arm"].get("motor_radius_mm")
    auto = requested is None
    if auto:
        # Shortest arms that satisfy every constraint (+5% margin) = lightest,
        # stiffest frame. Only grow beyond that if you deliberately want a
        # bigger quad. Clamped to r_max so the solver never proposes something
        # the stock cannot hold - validate.py reports it if the clamp bites.
        r = min(r_min * 1.05, r_max)
    else:
        r = float(requested)

    # Round once, here, so the reported radius and the motor coordinates that
    # go into Fusion are derived from the exact same number.
    r = round(r, 2)
    prop_inner_r = r - d_prop / 2.0

    return Layout(
        motor_radius_mm=r,
        min_radius_mm=round(r_min, 2),
        min_radius_props_mm=round(r_min_props, 2),
        min_radius_plate_mm=round(r_min_plate, 2),
        max_radius_mm=round(r_max, 2),
        diagonal_mm=round(2 * r, 2),
        adjacent_spacing_mm=round(r * math.sqrt(2.0), 2),
        prop_tip_gap_mm=round(r * math.sqrt(2.0) - d_prop, 2),
        plate_corner_r_mm=round(plate_corner_r, 2),
        prop_inner_r_mm=round(prop_inner_r, 2),
        plate_prop_gap_mm=round(prop_inner_r - plate_corner_r, 2),
        arm_length_mm=round(r - plate_inscribed_r, 2),
        auto_solved=auto,
        motors=[
            (name, r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))
            for name, a in zip(MOTOR_NAMES, MOTOR_ANGLES_DEG)
        ],
    )
