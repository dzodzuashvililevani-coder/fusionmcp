"""Compare Fusion's real geometry against the estimate in `frame mass`.

`mass.py` models the frame as a rectangle plus four trapezoids. That ignores
lightening holes, the plate/arm overlap, and every fillet -- so it errs heavy,
by design. Once the model exists, Fusion knows the true volume. This closes
that loop.

Mass is computed as **Fusion's volume x the density from materials.yaml**, not
Fusion's own mass number. Fusion's number is only right if you remembered to
assign a material with the correct density, and a default-steel body would give
you a wildly wrong answer without saying so.

    Fusion: Utilities -> ADD-INS -> Scripts -> mass_check -> Run

If the model comes out much lighter than the estimate, that headroom is real:
put it back into `params.yaml` as a bigger battery, or leave it as flight time.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from _common import active_design, app_ui, guard, load_payload, report, to_mm  # noqa: E402

# Bodies whose name starts with this are the wooden parts. Anything else in the
# design -- a mocked-up motor, the battery block -- is excluded from the wood
# total, because it is not cut from the sheet.
WOOD_PREFIX = "CUT_"


def wooden_bodies(design):
    """(bodies, skipped_names). Falls back to every visible body if nothing is
    named CUT_*, so the script is still useful before you rename anything."""
    matched, others = [], []
    for component in design.allComponents:
        for body in component.bRepBodies:
            (matched if body.name.startswith(WOOD_PREFIX) else others).append(body)
    if matched:
        return matched, [b.name for b in others]
    return [b for b in others if b.isVisible], []


def volume_cm3(bodies):
    """Fusion's physical volume is already in cm^3."""
    return sum(body.physicalProperties.volume for body in bodies)


def centre_of_mass_mm(bodies):
    """Volume-weighted centroid of the wood, in mm. Uniform sheet, so volume
    centroid and mass centroid are the same thing."""
    total = volume_cm3(bodies)
    if total <= 0:
        return 0.0, 0.0, 0.0
    cx = cy = cz = 0.0
    for body in bodies:
        props = body.physicalProperties
        com = props.centerOfMass
        cx += props.volume * com.x
        cy += props.volume * com.y
        cz += props.volume * com.z
    return to_mm(cx / total), to_mm(cy / total), to_mm(cz / total)


@guard
def run(context):
    _, ui = app_ui()
    design = active_design(ui)
    if not design:
        return
    payload = load_payload(ui)
    if not payload:
        return

    bodies, skipped = wooden_bodies(design)
    if not bodies:
        report(ui, "mass_check", [
            "No solid bodies in this design yet.",
            "",
            "Extrude the cut profiles by `stock_thickness` first, then name the",
            "wooden ones CUT_<something> so this script can tell wood from a mockup.",
        ])
        return

    density = payload["mass"]["density_g_cm3"]
    estimate = payload["mass"]["frame_wood_g"]
    auw = payload["mass"]["auw_g"]

    volume = volume_cm3(bodies)
    actual = volume * density
    delta = actual - estimate
    cx, cy, cz = centre_of_mass_mm(bodies)

    lines = [
        "{0} wooden body(ies), {1} ({2} g/cm^3)".format(
            len(bodies), payload["mass"]["material"], density),
        "",
        "Fusion volume      {0:8.2f} cm^3".format(volume),
        "-> wood mass       {0:8.1f} g".format(actual),
        "frame mass says    {0:8.1f} g".format(estimate),
        "difference         {0:+8.1f} g  ({1:+.0f}%)".format(
            delta, 100.0 * delta / estimate if estimate else 0.0),
        "",
        "AUW would move     {0:8.1f} g  ->  {1:.1f} g".format(auw, auw + delta),
        "",
        "wood centroid      ({0:+.2f}, {1:+.2f}, {2:+.2f}) mm".format(cx, cy, cz),
    ]

    if abs(cx) > 1.0 or abs(cy) > 1.0:
        lines += ["  ^ the wood itself is off-centre; on a symmetric X quad it should not be"]

    if delta > 0.5:
        lines += [
            "",
            "The model is HEAVIER than the estimate. That should not happen -- the",
            "estimate ignores holes and overlap, so it is meant to be the upper bound.",
            "Check for double-counted overlap, or a body that is not actually wood.",
        ]
    elif delta < -0.5:
        lines += [
            "",
            "The model is lighter than budgeted, which is expected. Either bank it as",
            "flight time, or spend it: a heavier battery, or thicker stock for stiffer arms.",
        ]

    if skipped:
        lines += ["", "Not counted as wood: " + ", ".join(skipped)]

    lines += ["", "Copy the real number into docs/build-log.md."]
    report(ui, "mass_check", lines)
