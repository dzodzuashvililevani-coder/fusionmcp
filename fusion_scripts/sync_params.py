"""Push `frame fusion` numbers into Fusion User Parameters.

Run this FIRST, before sketching anything. Then dimension every sketch against
a parameter name (`motor_radius`, `arm_width_root`, ...) rather than typing a
number. After that, changing `params.yaml` and re-running this script updates
the whole model.

    terminal:  frame fusion -o
    Fusion:    Utilities -> ADD-INS -> Scripts -> sync_params -> Run

Idempotent. Existing parameters are updated in place, so sketch dimensions that
already reference them survive. Nothing is ever deleted -- a parameter you
added by hand in Fusion is left alone.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import adsk.core  # noqa: E402

from _common import active_design, app_ui, guard, load_payload, report, warn_if_unbuildable  # noqa: E402


def _value_input(spec):
    """Fusion parses parameter expressions as strings, units included."""
    return adsk.core.ValueInput.createByString("{0} {1}".format(spec["value"], spec["unit"]))


def sync(design, table):
    """Create or update each user parameter. Returns (created, updated, unchanged)."""
    created, updated, unchanged = [], [], []
    params = design.userParameters

    for name in sorted(table):
        spec = table[name]
        expression = "{0} {1}".format(spec["value"], spec["unit"])
        existing = params.itemByName(name)

        if existing is None:
            params.add(name, _value_input(spec), spec["unit"], spec.get("comment", ""))
            created.append(name)
            continue

        if existing.expression.strip() == expression:
            unchanged.append(name)
            continue

        before = existing.expression
        existing.expression = expression
        existing.comment = spec.get("comment", existing.comment)
        updated.append("{0}: {1} -> {2}".format(name, before, expression))

    return created, updated, unchanged


@guard
def run(context):
    _, ui = app_ui()
    design = active_design(ui)
    if not design:
        return
    payload = load_payload(ui)
    if not payload:
        return
    warn_if_unbuildable(ui, payload)

    created, updated, unchanged = sync(design, payload["user_parameters"])

    lines = [
        "Synced from frame_params.json (schema {0})".format(payload["schema"]),
        "AUW {0} g, TWR {1}".format(payload["mass"]["auw_g"], payload["thrust"]["twr"]),
        "",
        "created:   {0}".format(len(created)),
        "updated:   {0}".format(len(updated)),
        "unchanged: {0}".format(len(unchanged)),
    ]
    if created:
        lines += ["", "NEW:"] + ["  " + n for n in created]
    if updated:
        lines += ["", "CHANGED:"] + ["  " + n for n in updated]
        lines += ["", "Rebuild the timeline and re-check any sketch that did not update."]

    report(ui, "sync_params", lines)
