"""Stamp bolt patterns into a sketch.

Mostly a library: `bolt_circle()`, `square_pattern()` and `stamp()` are what the
other scripts and your own one-off snippets call. Running it as a script lays
the frame's real hole patterns onto a REFERENCE sketch so you can see where
everything lands before committing to a profile.

All coordinates and diameters are in MILLIMETRES. The helpers convert to
Fusion's internal centimetres on the way in -- do not pre-divide by ten.
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _common import (  # noqa: E402
    active_design, app_ui, get_or_create_sketch, guard, load_payload, mm, point, report,
)


def bolt_circle(cx_mm, cy_mm, pitch_dia_mm, count, start_deg=45.0):
    """`count` points evenly spaced on a circle of diameter `pitch_dia_mm`.

    Motor mounts quote the pitch *diameter* (hole to hole across the base), so
    that is what this takes -- halving it here is the mistake to avoid.
    """
    radius = pitch_dia_mm / 2.0
    return [
        (
            cx_mm + radius * math.cos(math.radians(start_deg + i * 360.0 / count)),
            cy_mm + radius * math.sin(math.radians(start_deg + i * 360.0 / count)),
        )
        for i in range(count)
    ]


def square_pattern(cx_mm, cy_mm, pitch_mm):
    """The four corners of a square hole pattern. Flight controllers quote the
    edge-to-edge pitch (16 / 20 / 25.5 / 30.5), not the diagonal."""
    half = pitch_mm / 2.0
    return [
        (cx_mm + half, cy_mm + half),
        (cx_mm - half, cy_mm + half),
        (cx_mm - half, cy_mm - half),
        (cx_mm + half, cy_mm - half),
    ]


def stamp(sketch, points_mm, diameter_mm):
    """Draw a circle at each point. Returns the created SketchCircles."""
    circles = sketch.sketchCurves.sketchCircles
    radius = mm(diameter_mm / 2.0)
    return [circles.addByCenterRadius(point(x, y), radius) for x, y in points_mm]


def slot(sketch, cx_mm, cy_mm, length_mm, width_mm, vertical=False):
    """A rounded slot, for battery straps and zipties.

    Built as two arcs joined by two lines rather than a stadium primitive,
    because Fusion has no stadium primitive.
    """
    half_len = (length_mm - width_mm) / 2.0
    radius = width_mm / 2.0
    if half_len <= 0:
        return stamp(sketch, [(cx_mm, cy_mm)], width_mm)

    if vertical:
        a = (cx_mm, cy_mm + half_len)
        b = (cx_mm, cy_mm - half_len)
        offs = [(radius, 0.0), (-radius, 0.0)]
    else:
        a = (cx_mm - half_len, cy_mm)
        b = (cx_mm + half_len, cy_mm)
        offs = [(0.0, radius), (0.0, -radius)]

    arcs = sketch.sketchCurves.sketchArcs
    lines = sketch.sketchCurves.sketchLines
    created = [
        arcs.addByCenterStartSweep(point(*a), point(a[0] + offs[0][0], a[1] + offs[0][1]), math.pi),
        arcs.addByCenterStartSweep(point(*b), point(b[0] + offs[1][0], b[1] + offs[1][1]), math.pi),
    ]
    for dx, dy in offs:
        created.append(
            lines.addByTwoPoints(point(a[0] + dx, a[1] + dy), point(b[0] + dx, b[1] + dy))
        )
    return created


def stamp_frame_patterns(design, payload):
    """Every hole this frame needs, on one REFERENCE sketch. Returns a summary."""
    root = design.rootComponent
    sketch = get_or_create_sketch(root, "REFERENCE_hole_patterns")
    sketch.isComputeDeferred = True

    up = payload["user_parameters"]
    motor_hole = up["motor_screw_hole_dia"]["value"]
    fc_hole = up["fc_screw_hole_dia"]["value"]
    bolt_pitch = up["motor_bolt_circle"]["value"]
    fc_pitch = up["fc_hole_pitch"]["value"]
    slot_l = up["ziptie_slot_length"]["value"]
    slot_w = up["ziptie_slot_width"]["value"]

    summary = []

    for name, (x, y) in payload["layout"]["motors"].items():
        stamp(sketch, bolt_circle(x, y, bolt_pitch, 4), motor_hole)
        summary.append("{0}: 4 holes dia {1}mm on a {2}mm bolt circle".format(name, motor_hole, bolt_pitch))

    stamp(sketch, square_pattern(0.0, 0.0, fc_pitch), fc_hole)
    summary.append("flight controller: 4 holes on a {0}mm square".format(fc_pitch))

    # Sit the strap slots as far outboard as the edge distance allows: the
    # further apart they are, the less the battery can rock.
    plate_w = up["plate_width"]["value"]
    edge = payload["limits"]["min_screw_edge_distance_mm"]
    slot_x = plate_w / 2.0 - edge - slot_w / 2.0
    for side in (-1, 1):
        slot(sketch, side * slot_x, 0.0, slot_l, slot_w, vertical=True)
    summary.append("battery strap: 2 slots {0}x{1}mm at x = +/-{2:.1f}mm".format(
        slot_l, slot_w, slot_x))

    sketch.isComputeDeferred = False
    return sketch, summary


@guard
def run(context):
    _, ui = app_ui()
    design = active_design(ui)
    if not design:
        return
    payload = load_payload(ui)
    if not payload:
        return

    sketch, summary = stamp_frame_patterns(design, payload)
    report(ui, "hole_pattern", [
        "Stamped into sketch '{0}'.".format(sketch.name),
        "",
    ] + summary + [
        "",
        "These are FINISHED hole sizes. Your cutter takes kerf/2 off every edge,",
        "so set kerf = {0}mm in the cutter software rather than resizing these.".format(
            payload["stock"]["kerf_mm"]
        ),
    ])
