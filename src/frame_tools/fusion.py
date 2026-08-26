"""Build the handoff payload for Fusion.

`frame fusion` prints this; `fusion_scripts/sync_params.py` reads it from inside
Fusion. Nothing on the Fusion side recomputes geometry -- it is solved once, in
`geometry.py`, and everything downstream consumes these numbers.

The important part is `user_parameters`: a flat name -> {value, unit, comment}
table that maps one-to-one onto Fusion User Parameters. Keeping the naming
decisions here rather than in the Fusion script means a sketch dimension that
references `motor_radius` keeps working when the solver output changes.
"""
from __future__ import annotations

from typing import Any

from .geometry import Layout
from .mass import MassReport
from .params import hole_diameter_mm, material_density
from .thrust import ThrustReport
from .validate import Check

SCHEMA_VERSION = 1

# Fusion User Parameter names must be valid identifiers and unique per design.
_MOTOR_ABBREV = {
    "front_right": "fr",
    "front_left": "fl",
    "rear_left": "rl",
    "rear_right": "rr",
}


def user_parameters(p: dict[str, Any], layout: Layout) -> dict[str, dict[str, Any]]:
    """Flat table of every number the Fusion model needs, ready to become
    User Parameters. Values are floats in `unit`; Fusion parses them as expressions."""
    def mm(value: float, comment: str) -> dict[str, Any]:
        return {"value": round(float(value), 4), "unit": "mm", "comment": comment}

    def deg(value: float, comment: str) -> dict[str, Any]:
        return {"value": round(float(value), 4), "unit": "deg", "comment": comment}

    stock, arm, plate = p["stock"], p["arm"], p["center_plate"]
    motors, props, batt, cam = p["motors"], p["props"], p["battery"], p["camera"]
    holes = p.get("holes", {})

    out: dict[str, dict[str, Any]] = {
        "stock_thickness": mm(stock["thickness_mm"], "sheet thickness, extrude every wooden body by this"),
        "stock_size": mm(min(stock["size_mm"]), "shortest side of the raw sheet"),
        "kerf": mm(stock["kerf_mm"], "material the cutter removes; compensate toolpaths, not sketches"),

        "motor_radius": mm(layout.motor_radius_mm, "centre -> motor shaft; drives everything"),
        "motor_diagonal": mm(layout.diagonal_mm, "motor-to-motor across; the frame class"),
        "motor_bolt_circle": mm(motors["bolt_circle_mm"], "motor mounting hole pitch"),
        "motor_base_dia": mm(motors["base_diameter_mm"], "motor can footprint on the arm"),
        "motor_screw_hole_dia": mm(hole_diameter_mm(p, motors["screw"]),
                                   f"finished hole for a {motors['screw']} motor screw"),

        "arm_length": mm(layout.arm_length_mm, "exposed arm, plate edge -> motor"),
        "arm_width_tip": mm(arm["width_mm"], "arm width at the motor end"),
        "arm_width_root": mm(arm["root_width_mm"], "arm width at the plate; taper stiffens it"),

        "plate_width": mm(plate["size_mm"][0], "centre plate X"),
        "plate_depth": mm(plate["size_mm"][1], "centre plate Y"),
        "fc_hole_pitch": mm(plate["fc_hole_pattern_mm"], "flight controller square hole pattern"),
        "fc_screw_hole_dia": mm(hole_diameter_mm(p, plate["fc_screw"]),
                                f"finished hole for a {plate['fc_screw']} FC standoff"),

        "prop_diameter": mm(props["diameter_mm"], "for the clearance sketch; props are not modelled"),
        "prop_tip_clearance": mm(props["tip_clearance_mm"], "designed gap between adjacent prop tips"),

        "battery_length": mm(batt["size_mm"][0], "battery L"),
        "battery_width": mm(batt["size_mm"][1], "battery W"),
        "battery_height": mm(batt["size_mm"][2], "battery H"),

        "camera_width": mm(cam["width_mm"], "camera body width"),
        "camera_ear_spacing": mm(cam["mount_ear_spacing_mm"], "camera mount ear pitch"),
        "camera_tilt": deg(cam["tilt_deg"], "camera uptilt from horizontal"),

        "ziptie_slot_length": mm(holes.get("ziptie_slot_mm", [8.0, 2.5])[0], "strap / ziptie slot L"),
        "ziptie_slot_width": mm(holes.get("ziptie_slot_mm", [8.0, 2.5])[1], "strap / ziptie slot W"),
    }

    lightening = float(holes.get("lightening_hole_dia_mm", 0.0))
    if lightening > 0:
        out["lightening_hole_dia"] = mm(lightening, "round lightening holes in the arms")

    for name, x, y in layout.motors:
        abbrev = _MOTOR_ABBREV[name]
        out[f"motor_{abbrev}_x"] = mm(x, f"{name} motor shaft X")
        out[f"motor_{abbrev}_y"] = mm(y, f"{name} motor shaft Y")

    return out


def build_payload(
    p: dict[str, Any],
    layout: Layout,
    mass: MassReport,
    thrust: ThrustReport,
    checks: list[Check],
) -> dict[str, Any]:
    """Everything Fusion needs, in one JSON-serialisable dict."""
    failed = [c.name for c in checks if c.status == "FAIL"]
    warned = [c.name for c in checks if c.status == "WARN"]

    return {
        "schema": SCHEMA_VERSION,
        "generated_by": "frame fusion",
        "units": "mm, grams, degrees",
        "buildable": not failed,
        "checks": {
            "passed": len(checks) - len(failed) - len(warned),
            "warnings": warned,
            "failures": failed,
        },
        "layout": layout.as_dict(),
        "stock": p["stock"],
        "arm": p["arm"],
        "center_plate": p["center_plate"],
        "motors": p["motors"],
        "props": p["props"],
        "battery": p["battery"],
        "camera": p["camera"],
        "holes": p.get("holes", {}),
        "limits": p["limits"],
        "mass": {
            "auw_g": round(mass.total_mass_g, 1),
            "frame_wood_g": round(mass.frame_mass_g, 1),
            "cut_area_mm2": round(mass.frame_area_mm2, 0),
            "cg_offset_mm": round(mass.cg_offset_mm, 2),
            "material": p["stock"]["material"],
            "density_g_cm3": material_density(p["stock"]["material"]),
        },
        "thrust": {
            "twr": round(thrust.twr, 2),
            "hover_throttle_pct": round(thrust.hover_throttle_pct, 1),
            "verdict": thrust.verdict,
        },
        "user_parameters": user_parameters(p, layout),
    }
