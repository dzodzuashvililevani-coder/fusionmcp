"""Export the cut sketches to `dxf/`.

Convention: **any sketch whose name starts with `CUT_` is a part to be cut.**
Everything else -- construction, reference, hole-pattern scratch -- is ignored.
Name them `CUT_center_plate`, `CUT_arm`, and so on; the file lands as
`dxf/<sketch name>.dxf`.

    Fusion: Utilities -> ADD-INS -> Scripts -> export_dxf -> Run

## About kerf

This exports NOMINAL geometry -- the shape you want to end up with. It does not
shrink the profiles. Kerf compensation belongs in the cutter's software, which
knows which side of the line the beam sits on; doing it here as well would
double-compensate and give you loose motor screws.

Your kerf is carried in the report below so you can type it into LightBurn /
Fusion CAM / whatever drives the machine. Measure it first with
`frame kerf-test`.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _common import (  # noqa: E402
    DXF_DIR, active_design, app_ui, guard, load_payload, report, to_mm, warn_if_unbuildable,
)

CUT_PREFIX = "CUT_"


def cut_sketches(design):
    """Every sketch marked for cutting, across every component."""
    found = []
    for component in design.allComponents:
        for sketch in component.sketches:
            if sketch.name.startswith(CUT_PREFIX):
                found.append(sketch)
    return found


def sketch_extent_mm(sketch):
    """(width, height) of the sketch's geometry, in millimetres."""
    box = sketch.boundingBox
    if not box:
        return 0.0, 0.0
    return (
        to_mm(box.maxPoint.x - box.minPoint.x),
        to_mm(box.maxPoint.y - box.minPoint.y),
    )


@guard
def run(context):
    _, ui = app_ui()
    design = active_design(ui)
    if not design:
        return
    payload = load_payload(ui)
    if not payload:
        return

    if not warn_if_unbuildable(ui, payload):
        report(ui, "export_dxf", [
            "Refusing to export a cut file for a design that fails validation.",
            "Fix params.yaml, re-run `frame report`, then `frame fusion -o`.",
        ])
        return

    sketches = cut_sketches(design)
    if not sketches:
        report(ui, "export_dxf", [
            "No sketches named {0}* were found.".format(CUT_PREFIX),
            "",
            "Rename each sketch that represents a part to be cut, e.g.",
            "  CUT_center_plate",
            "  CUT_arm",
        ])
        return

    if not os.path.isdir(DXF_DIR):
        os.makedirs(DXF_DIR)

    stock_w, stock_h = payload["stock"]["size_mm"]
    kerf = payload["stock"]["kerf_mm"]

    lines, oversize = [], []
    for sketch in sketches:
        width, height = sketch_extent_mm(sketch)
        path = os.path.join(DXF_DIR, sketch.name + ".dxf")
        ok = sketch.saveAsDXF(path)
        flag = ""
        if width > stock_w or height > stock_h:
            flag = "   <-- DOES NOT FIT THE STOCK"
            oversize.append(sketch.name)
        lines.append("{0:<24} {1:6.1f} x {2:6.1f} mm   {3}{4}".format(
            sketch.name, width, height, "ok" if ok else "FAILED TO WRITE", flag))

    footer = [
        "",
        "Written to dxf/",
        "Geometry is NOMINAL. Set kerf = {0} mm ({1}) in your cutter software,".format(
            kerf, payload["stock"]["cut_method"]),
        "outward on holes, inward on outer profiles. Do not offset here as well.",
        "",
        "Before sending: delete REFERENCE geometry, and confirm grain runs ALONG",
        "the arms -- across the grain a wooden arm snaps at the motor mount.",
    ]
    if oversize:
        footer += ["", "STOP: {0} exceeds the {1}x{2}mm sheet.".format(
            ", ".join(oversize), stock_w, stock_h)]

    report(ui, "export_dxf", ["Exported {0} sketch(es):".format(len(sketches)), ""] + lines + footer)
