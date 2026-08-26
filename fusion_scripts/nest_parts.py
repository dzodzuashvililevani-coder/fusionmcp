"""Check the cut parts fit the 250x250 sheet, and draw where they go.

Shelf packing on bounding boxes: parts are sorted tallest-first and laid in
rows. That is pessimistic -- it ignores the fact that a tapered arm nests into
its neighbour's waste -- so a PASS here is trustworthy and a FAIL is worth
looking at by eye before believing.

Nothing is moved. It draws rectangles on a REFERENCE sketch showing a workable
arrangement (the dialog names them in placement order), and leaves the actual nesting to you or to the cutter's
software, which can rotate parts and nest concave shapes properly.

    Fusion: Utilities -> ADD-INS -> Scripts -> nest_parts -> Run
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _common import (  # noqa: E402
    active_design, app_ui, get_or_create_sketch, guard, load_payload, point, report,
)
from export_dxf import CUT_PREFIX, cut_sketches, sketch_extent_mm  # noqa: E402

# Space between neighbouring parts. Two kerfs plus a little, so a slip in the
# machine's origin does not weld two parts together.
def part_gap_mm(kerf_mm):
    return max(2.0 * float(kerf_mm) + 1.0, 2.0)


def shelf_pack(parts, sheet_w, sheet_h, gap):
    """parts = [(name, w, h)]. Returns (placements, leftovers).

    placements = [(name, x, y, w, h)] with the origin at the sheet's lower left.
    """
    placements, leftovers = [], []
    ordered = sorted(parts, key=lambda part: -part[2])

    cursor_x, shelf_y, shelf_h = gap, gap, 0.0
    for name, width, height in ordered:
        if width + 2 * gap > sheet_w or height + 2 * gap > sheet_h:
            leftovers.append(name)
            continue
        if cursor_x + width + gap > sheet_w:          # start a new shelf
            shelf_y += shelf_h + gap
            cursor_x, shelf_h = gap, 0.0
        if shelf_y + height + gap > sheet_h:          # ran off the sheet
            leftovers.append(name)
            continue
        placements.append((name, cursor_x, shelf_y, width, height))
        cursor_x += width + gap
        shelf_h = max(shelf_h, height)

    return placements, leftovers


def _rect(sketch, x, y, w, h):
    sketch.sketchCurves.sketchLines.addTwoPointRectangle(point(x, y), point(x + w, y + h))


def draw_nest(design, placements, sheet_w, sheet_h):
    root = design.rootComponent
    sketch = get_or_create_sketch(root, "REFERENCE_nest")
    sketch.isComputeDeferred = True
    _rect(sketch, 0.0, 0.0, sheet_w, sheet_h)
    for _name, x, y, w, h in placements:
        _rect(sketch, x, y, w, h)
    sketch.isComputeDeferred = False
    return sketch


@guard
def run(context):
    _, ui = app_ui()
    design = active_design(ui)
    if not design:
        return
    payload = load_payload(ui)
    if not payload:
        return

    sketches = cut_sketches(design)
    if not sketches:
        report(ui, "nest_parts", [
            "No {0}* sketches to nest.".format(CUT_PREFIX),
            "Name your cut parts CUT_<something> first -- see export_dxf.",
        ])
        return

    sheet_w, sheet_h = payload["stock"]["size_mm"]
    gap = part_gap_mm(payload["stock"]["kerf_mm"])

    parts = []
    for sketch in sketches:
        width, height = sketch_extent_mm(sketch)
        parts.append((sketch.name, width, height))

    placements, leftovers = shelf_pack(parts, sheet_w, sheet_h, gap)
    used = sum(w * h for _, _, _, w, h in placements)
    sketch = draw_nest(design, placements, sheet_w, sheet_h)

    lines = [
        "Sheet {0} x {1} mm, {2}mm between parts".format(sheet_w, sheet_h, gap),
        "Bounding-box utilisation: {0:.0f}%".format(100.0 * used / (sheet_w * sheet_h)),
        "",
    ]
    for name, x, y, w, h in placements:
        lines.append("{0:<24} at ({1:6.1f}, {2:6.1f})  {3:5.1f} x {4:5.1f} mm".format(
            name, x, y, w, h))

    if leftovers:
        lines += [
            "",
            "DID NOT FIT: " + ", ".join(leftovers),
            "",
            "Options, cheapest first:",
            "  - let the cutter's software nest properly (it can rotate parts)",
            "  - shorten the arms: set arm.motor_radius_mm in params.yaml",
            "  - cut the arms as separate parts and bolt them to the plate",
            "  - use a bigger sheet: stock.size_mm",
        ]
    else:
        lines += ["", "Everything fits, with room to spare for a shelf-packer that cannot rotate."]

    lines += ["", "Drawn on sketch '{0}' (delete before exporting DXF).".format(sketch.name)]
    report(ui, "nest_parts", lines)
