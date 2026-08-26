"""Shared helpers for the scripts in this folder. Runs INSIDE Fusion only.

Not a Fusion script itself -- it has no run(context), so it will not appear in
the Scripts list. The other files import it.

Two things to remember about the Fusion API, because both bite silently:

1. **Every length in the API is centimetres**, no matter what the document's
   display units say. Use `mm()` on the way in and `to_mm()` on the way out.
2. Sketch geometry is created on a plane; the sketch's own XY is not the
   component's XY unless you sketched on `xYConstructionPlane`.
"""
import json
import os
import sys
import traceback

import adsk.core
import adsk.fusion

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(HERE)
PARAMS_JSON = os.path.join(HERE, "frame_params.json")
DXF_DIR = os.path.join(PROJECT_ROOT, "dxf")

# Layer names must match dxf/README.md.
LAYER_CUT = "CUT"
LAYER_HOLES = "HOLES"
LAYER_ENGRAVE = "ENGRAVE"
LAYER_REFERENCE = "REFERENCE"


def mm(value):
    """millimetres -> Fusion internal centimetres."""
    return float(value) / 10.0


def to_mm(value):
    """Fusion internal centimetres -> millimetres."""
    return float(value) * 10.0


def app_ui():
    app = adsk.core.Application.get()
    return app, app.userInterface


def active_design(ui):
    """The active Fusion design, or None with a message already shown."""
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        ui.messageBox("Open a Fusion DESIGN first (this is not a drawing/CAM script).")
    return design


def load_payload(ui):
    """Read frame_params.json. Returns None with a message if it is not there."""
    if not os.path.exists(PARAMS_JSON):
        ui.messageBox(
            "frame_params.json is missing.\n\n"
            "Generate it first, from a terminal in the project:\n\n"
            "    frame fusion -o\n\n"
            "Looked in:\n" + PARAMS_JSON
        )
        return None
    with open(PARAMS_JSON, "r", encoding="utf-8") as fh:
        payload = json.load(fh)

    if payload.get("schema") != 1:
        ui.messageBox(
            "frame_params.json is schema {0}, these scripts speak schema 1. "
            "Update the scripts or regenerate.".format(payload.get("schema"))
        )
        return None
    return payload


def warn_if_unbuildable(ui, payload):
    """Fusion is for modelling, not for deciding. But do not let a failing design
    get modelled silently -- that is how a bad number reaches the cutter."""
    failures = payload.get("checks", {}).get("failures", [])
    if failures:
        ui.messageBox(
            "This design FAILS pre-cut validation:\n\n  "
            + "\n  ".join(failures)
            + "\n\nModel it if you are exploring, but do not export a cut file. "
              "Fix params.yaml and re-run `frame report`."
        )
    return not failures


def point(x_mm, y_mm, z_mm=0.0):
    return adsk.core.Point3D.create(mm(x_mm), mm(y_mm), mm(z_mm))


def get_or_create_sketch(component, name, plane=None):
    """A sketch by name, reused if it already exists so re-running is idempotent."""
    for sketch in component.sketches:
        if sketch.name == name:
            return sketch
    sketch = component.sketches.add(plane or component.xYConstructionPlane)
    sketch.name = name
    return sketch


def report(ui, title, lines):
    ui.messageBox("\n".join(str(line) for line in lines), title)


def guard(fn):
    """Wrap a run(context) so a traceback reaches the user instead of vanishing."""
    def wrapper(context):
        ui = None
        try:
            _, ui = app_ui()
            fn(context)
        except Exception:  # noqa: BLE001 - Fusion swallows anything not shown
            if ui:
                ui.messageBox("Failed:\n{0}".format(traceback.format_exc()))
            else:
                sys.stderr.write(traceback.format_exc())
    return wrapper
