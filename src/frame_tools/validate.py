"""Pre-cut design checks. Run this before you put a blade in the wood."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .geometry import Layout
from .mass import MassReport
from .thrust import ThrustReport

OK, WARN, FAIL = "OK", "WARN", "FAIL"


@dataclass
class Check:
    status: str
    name: str
    detail: str


def run(p: dict[str, Any], layout: Layout, mass: MassReport, thrust: ThrustReport) -> list[Check]:
    checks: list[Check] = []

    def add(cond_ok: bool, cond_warn: bool, name: str, detail: str) -> None:
        checks.append(Check(OK if cond_ok else (WARN if cond_warn else FAIL), name, detail))

    # --- geometry -------------------------------------------------------
    add(
        layout.motor_radius_mm >= layout.min_radius_props_mm,
        False,
        "prop clearance",
        f"arm radius {layout.motor_radius_mm}mm vs {layout.min_radius_props_mm}mm minimum "
        f"(tip gap {layout.prop_tip_gap_mm}mm) - below the minimum, adjacent props strike",
    )
    add(
        layout.motor_radius_mm <= layout.max_radius_mm,
        False,
        "fits the stock",
        f"needs {layout.motor_radius_mm}mm reach, stock allows {layout.max_radius_mm}mm "
        f"({p['arm']['orientation']} orientation)",
    )

    # Props must clear the centre plate corners, not just each other. The arms
    # leave at 45 degrees, which is exactly where a rectangular plate's corners
    # are - so the corner, not the edge, is the thing a prop hits.
    plate_w, plate_h = p["center_plate"]["size_mm"]
    add(
        layout.plate_prop_gap_mm > 0,
        layout.plate_prop_gap_mm > -3,
        "props clear centre plate",
        f"prop inner edge at r={layout.prop_inner_r_mm}mm, plate corner at "
        f"r={layout.plate_corner_r_mm}mm on the {plate_w}x{plate_h}mm plate "
        f"(gap {layout.plate_prop_gap_mm:+.1f}mm) - a negative gap means the props chop it",
    )

    # --- wood strength --------------------------------------------------
    edge = float(p["limits"]["min_screw_edge_distance_mm"])
    bolt_r = float(p["motors"]["bolt_circle_mm"]) / 2
    needed_w = 2 * (bolt_r + edge)
    add(
        p["arm"]["width_mm"] >= needed_w,
        p["arm"]["width_mm"] >= needed_w - 2,
        "arm wide enough for motor screws",
        f"arm is {p['arm']['width_mm']}mm, motor bolts need >= {needed_w:.1f}mm to avoid splitting",
    )
    # The FC bolts through the plate; its holes need the same edge distance as
    # any other hole, measured from the plate edge, or the plate splits there.
    fc_pitch = float(p["center_plate"]["fc_hole_pattern_mm"])
    fc_edge = min(plate_w, plate_h) / 2 - fc_pitch / 2
    add(
        fc_edge >= edge,
        fc_edge >= edge / 2,
        "FC pattern fits the plate",
        f"{fc_pitch}mm hole pattern on a {plate_w}x{plate_h}mm plate leaves "
        f"{fc_edge:.1f}mm to the edge; {edge}mm is the minimum before wood splits",
    )

    t = float(p["stock"]["thickness_mm"])
    add(t >= 3.0, t >= 2.0, "stock thickness",
        f"{t}mm - thin plywood arms flex and cause gyro noise; 3mm+ recommended")

    # --- fit ------------------------------------------------------------
    bw, bl = p["battery"]["size_mm"][0], p["battery"]["size_mm"][1]
    add(
        bw <= plate_w and bl <= plate_h,
        bw <= plate_w * 1.3 and bl <= plate_h * 1.3,
        "battery fits centre plate",
        f"battery {bw}x{bl}mm on a {plate_w}x{plate_h}mm plate",
    )

    # --- flight dynamics ------------------------------------------------
    add(
        thrust.twr >= float(p["limits"]["target_twr"]),
        thrust.twr >= float(p["limits"]["min_twr"]),
        "thrust-to-weight",
        f"TWR {thrust.twr:.2f} ({thrust.verdict}), hover at ~{thrust.hover_throttle_pct:.0f}% throttle",
    )
    max_cg = float(p["limits"]["max_cg_offset_mm"])
    add(
        mass.cg_offset_mm <= max_cg,
        mass.cg_offset_mm <= max_cg * 2,
        "centre of gravity",
        f"CG is {mass.cg_offset_mm:.1f}mm from thrust centre "
        f"(x{mass.cg_x_mm:+.1f}, y{mass.cg_y_mm:+.1f}); limit {max_cg}mm",
    )
    frame_pct = 100 * mass.frame_mass_g / mass.total_mass_g
    add(
        frame_pct <= 25,
        frame_pct <= 40,
        "frame mass fraction",
        f"wood is {frame_pct:.0f}% of AUW ({mass.frame_mass_g:.1f}g of {mass.total_mass_g:.1f}g)",
    )

    return checks
