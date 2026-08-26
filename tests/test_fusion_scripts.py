"""Exercise `fusion_scripts/` against a stubbed Fusion API.

These scripts cannot be imported normally -- they need `adsk`, which only
exists inside Fusion. [`fusion_stub.py`](fusion_stub.py) supplies just enough
of it to run them.

A pass here means the script runs end to end against the real
`frame_params.json`: no missing payload key, no broken format string, no
factor-of-ten unit slip. It does NOT mean Fusion will draw what you expect.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

import fusion_stub
from frame_tools.params import project_root

FUSION_SCRIPTS = project_root() / "fusion_scripts"


@pytest.fixture
def fusion():
    """A stubbed Fusion with an empty design, with fusion_scripts importable."""
    app = fusion_stub.install()
    sys.path.insert(0, str(FUSION_SCRIPTS))
    try:
        yield app
    finally:
        sys.path.remove(str(FUSION_SCRIPTS))
        fusion_stub.remove()


def _import(name):
    import importlib

    return importlib.import_module(name)


# --- the handoff file itself ---------------------------------------------
def test_handoff_json_is_committed_and_current():
    """`frame fusion -o` output is committed so the .f3d and its numbers stay
    together in git. If this fails, re-run it."""
    import json

    from frame_tools import fusion as fusion_payload
    from frame_tools import geometry, mass, params, thrust, validate

    path = FUSION_SCRIPTS / "frame_params.json"
    assert path.exists(), "run: frame fusion -o"

    p = params.load_params()
    lay = geometry.solve(p)
    m = mass.build(p, lay, params.load_loadout())
    t = thrust.build(p, m.total_mass_g)
    expected = fusion_payload.build_payload(p, lay, m, t, validate.run(p, lay, m, t))

    assert json.loads(path.read_text(encoding="utf-8")) == expected, (
        "fusion_scripts/frame_params.json is stale - re-run `frame fusion -o`"
    )


# --- sync_params ----------------------------------------------------------
def test_sync_params_creates_every_parameter(fusion):
    sync_params = _import("sync_params")
    sync_params.run(None)

    design = fusion.activeProduct
    names = {p.name for p in design.userParameters}
    assert "motor_radius" in names
    assert len(names) == len(_payload()["user_parameters"])
    assert "created:   {0}".format(len(names)) in fusion.userInterface.last


def test_sync_params_is_idempotent(fusion):
    sync_params = _import("sync_params")
    sync_params.run(None)
    first = len(fusion.activeProduct.userParameters)

    sync_params.run(None)
    assert len(fusion.activeProduct.userParameters) == first, "second run duplicated parameters"
    assert "created:   0" in fusion.userInterface.last
    assert "unchanged: {0}".format(first) in fusion.userInterface.last


def test_sync_params_updates_a_changed_value_in_place(fusion):
    """The whole point: a sketch dimension bound to `motor_radius` must survive
    a params change. Updating in place preserves the binding; delete-and-recreate
    would break every dimension referencing it."""
    sync_params = _import("sync_params")
    sync_params.run(None)

    param = fusion.activeProduct.userParameters.itemByName("motor_radius")
    original = param.expression
    param.expression = "1 mm"

    sync_params.run(None)
    assert fusion.activeProduct.userParameters.itemByName("motor_radius") is param
    assert param.expression == original
    assert "motor_radius: 1 mm ->" in fusion.userInterface.last


def test_sync_params_leaves_hand_made_parameters_alone(fusion):
    from adsk.core import ValueInput

    design = fusion.activeProduct
    design.userParameters.add("my_own_thing", ValueInput.createByString("5 mm"), "mm", "mine")

    _import("sync_params").run(None)
    assert design.userParameters.itemByName("my_own_thing").expression == "5 mm"


# --- hole_pattern ---------------------------------------------------------
def test_bolt_circle_takes_a_diameter_not_a_radius(fusion):
    """Motor specs quote hole-to-hole across the base. Halving it twice is the
    classic way to drill a pattern the motor cannot bolt to."""
    import math

    hole_pattern = _import("hole_pattern")
    points = hole_pattern.bolt_circle(0.0, 0.0, 9.0, 4)
    assert len(points) == 4
    for x, y in points:
        assert math.hypot(x, y) == pytest.approx(4.5)


def test_square_pattern_uses_edge_pitch(fusion):
    hole_pattern = _import("hole_pattern")
    points = hole_pattern.square_pattern(0.0, 0.0, 25.5)
    xs = sorted({round(x, 6) for x, _ in points})
    assert xs == [-12.75, 12.75]


def test_hole_pattern_stamps_every_hole_the_frame_needs(fusion):
    hole_pattern = _import("hole_pattern")
    hole_pattern.run(None)

    sketch = fusion.activeProduct.rootComponent.sketches[0]
    # 4 motors x 4 bolts, plus 4 FC holes.
    assert len(sketch.sketchCurves.sketchCircles) == 4 * 4 + 4
    # Two strap slots, each two arcs and two lines.
    assert len(sketch.sketchCurves.sketchArcs) == 4
    assert sketch.isComputeDeferred is False


def test_strap_slots_respect_the_edge_distance(fusion):
    """A slot cut too close to the plate edge tears out under strap tension."""
    hole_pattern = _import("hole_pattern")
    hole_pattern.run(None)

    payload = _payload()
    up = payload["user_parameters"]
    plate_half = up["plate_width"]["value"] / 2.0
    slot_w = up["ziptie_slot_width"]["value"]
    edge = payload["limits"]["min_screw_edge_distance_mm"]

    sketch = fusion.activeProduct.rootComponent.sketches[0]
    xs = [abs(arc.centre.x) * 10.0 for arc in sketch.sketchCurves.sketchArcs]
    assert xs, "no slots were drawn"
    assert plate_half - (max(xs) + slot_w / 2.0) >= edge - 1e-9


def test_hole_pattern_reuses_its_sketch(fusion):
    hole_pattern = _import("hole_pattern")
    hole_pattern.run(None)
    hole_pattern.run(None)
    assert len(fusion.activeProduct.rootComponent.sketches) == 1


# --- nest_parts -----------------------------------------------------------
def test_shelf_pack_fits_the_real_frame_on_one_sheet(fusion):
    nest_parts = _import("nest_parts")
    payload = _payload()
    sheet_w, sheet_h = payload["stock"]["size_mm"]
    up = payload["user_parameters"]

    parts = [("CUT_center_plate", up["plate_width"]["value"], up["plate_depth"]["value"])]
    for i in range(4):
        parts.append((f"CUT_arm_{i}", up["arm_length"]["value"], up["arm_width_root"]["value"]))

    placements, leftovers = nest_parts.shelf_pack(parts, sheet_w, sheet_h, 2.0)
    assert leftovers == [], f"the default design does not nest: {leftovers}"
    assert len(placements) == len(parts)


def test_shelf_pack_never_overlaps_or_leaves_the_sheet(fusion):
    nest_parts = _import("nest_parts")
    parts = [(f"CUT_p{i}", 40.0 + i * 7, 30.0 + i * 5) for i in range(9)]
    placements, _ = nest_parts.shelf_pack(parts, 250.0, 250.0, 3.0)

    for name, x, y, w, h in placements:
        assert x >= 0 and y >= 0 and x + w <= 250.0 and y + h <= 250.0, name

    for i, (n1, x1, y1, w1, h1) in enumerate(placements):
        for n2, x2, y2, w2, h2 in placements[i + 1:]:
            apart = x1 + w1 <= x2 or x2 + w2 <= x1 or y1 + h1 <= y2 or y2 + h2 <= y1
            assert apart, f"{n1} overlaps {n2}"


def test_shelf_pack_reports_a_part_too_big_for_the_sheet(fusion):
    nest_parts = _import("nest_parts")
    placements, leftovers = nest_parts.shelf_pack(
        [("CUT_ok", 50.0, 50.0), ("CUT_huge", 400.0, 50.0)], 250.0, 250.0, 3.0)
    assert leftovers == ["CUT_huge"]
    assert [p[0] for p in placements] == ["CUT_ok"]


def test_nest_parts_says_so_when_there_is_nothing_named_cut(fusion):
    _import("nest_parts").run(None)
    assert "CUT_" in fusion.userInterface.last


# --- mass_check -----------------------------------------------------------
def test_mass_check_converts_volume_to_grams(fusion):
    from adsk.fusion import BRepBody

    payload = _payload()
    density = payload["mass"]["density_g_cm3"]
    volume_cm3 = 30.0

    root = fusion.activeProduct.rootComponent
    root.bRepBodies.append(BRepBody("CUT_center_plate", volume_cm3))

    _import("mass_check").run(None)
    text = fusion.userInterface.last
    assert "{0:8.1f} g".format(volume_cm3 * density).strip() in text
    assert "{0:8.2f} cm^3".format(volume_cm3).strip() in text


def test_mass_check_centroid_is_reported_in_mm(fusion):
    from adsk.core import Point3D
    from adsk.fusion import BRepBody

    mass_check = _import("mass_check")
    bodies = [
        BRepBody("CUT_a", 10.0, Point3D(1.0, 0.0, 0.0)),   # 10mm in Fusion's cm
        BRepBody("CUT_b", 10.0, Point3D(-1.0, 0.0, 0.0)),
    ]
    cx, cy, cz = mass_check.centre_of_mass_mm(bodies)
    assert (cx, cy, cz) == pytest.approx((0.0, 0.0, 0.0))

    cx, _, _ = mass_check.centre_of_mass_mm([bodies[0]])
    assert cx == pytest.approx(10.0), "centimetres leaked into a millimetre report"


def test_mass_check_ignores_non_wood_bodies(fusion):
    from adsk.fusion import BRepBody

    mass_check = _import("mass_check")
    root = fusion.activeProduct.rootComponent
    root.bRepBodies.append(BRepBody("CUT_plate", 10.0))
    root.bRepBodies.append(BRepBody("battery_mockup", 1000.0))

    bodies, skipped = mass_check.wooden_bodies(fusion.activeProduct)
    assert [b.name for b in bodies] == ["CUT_plate"]
    assert skipped == ["battery_mockup"]


def test_mass_check_needs_a_body(fusion):
    _import("mass_check").run(None)
    assert "No solid bodies" in fusion.userInterface.last


# --- export_dxf -----------------------------------------------------------
def test_export_dxf_writes_only_cut_sketches(fusion, tmp_path, monkeypatch):
    export_dxf = _import("export_dxf")
    monkeypatch.setattr(export_dxf, "DXF_DIR", str(tmp_path))

    root = fusion.activeProduct.rootComponent
    keep = fusion_stub.Sketch("CUT_center_plate", extent_mm=(70.0, 70.0))
    drop = fusion_stub.Sketch("REFERENCE_nest", extent_mm=(250.0, 250.0))
    root.sketches.extend([keep, drop])

    export_dxf.run(None)
    assert keep.exported_to and not drop.exported_to
    assert Path(keep.exported_to[0]).name == "CUT_center_plate.dxf"


def test_export_dxf_flags_a_part_bigger_than_the_stock(fusion, tmp_path, monkeypatch):
    export_dxf = _import("export_dxf")
    monkeypatch.setattr(export_dxf, "DXF_DIR", str(tmp_path))

    root = fusion.activeProduct.rootComponent
    root.sketches.append(fusion_stub.Sketch("CUT_toobig", extent_mm=(300.0, 40.0)))

    export_dxf.run(None)
    assert "DOES NOT FIT" in fusion.userInterface.last
    assert "STOP" in fusion.userInterface.last


def test_export_dxf_measures_in_millimetres(fusion):
    export_dxf = _import("export_dxf")
    sketch = fusion_stub.Sketch("CUT_plate", extent_mm=(70.0, 45.0))
    assert export_dxf.sketch_extent_mm(sketch) == pytest.approx((70.0, 45.0))


def test_export_dxf_refuses_an_unbuildable_design(fusion, tmp_path, monkeypatch):
    """The last gate before a machine. A design that fails validation must not
    produce a cut file, however far through the workflow you already are."""
    export_dxf = _import("export_dxf")
    monkeypatch.setattr(export_dxf, "DXF_DIR", str(tmp_path))

    payload = _payload()
    payload["checks"]["failures"] = ["thrust-to-weight"]
    monkeypatch.setattr(export_dxf, "load_payload", lambda ui: payload)

    root = fusion.activeProduct.rootComponent
    sketch = fusion_stub.Sketch("CUT_plate", extent_mm=(70.0, 70.0))
    root.sketches.append(sketch)

    export_dxf.run(None)
    assert not sketch.exported_to, "exported a cut file from a failing design"
    assert "Refusing" in fusion.userInterface.last


# --- the installed shims --------------------------------------------------
def test_installer_covers_every_runnable_script():
    """The installer skips leading-underscore files. If that convention ever
    disagrees with which files define run(), a script silently stops being
    installable."""
    runnable, private = set(), set()
    for path in FUSION_SCRIPTS.glob("*.py"):
        (private if path.name.startswith("_") else runnable).add(path.stem)
        text = path.read_text(encoding="utf-8")
        has_run = "\ndef run(context)" in text
        assert has_run == (not path.name.startswith("_")), (
            f"{path.name}: leading underscore and def run(context) disagree"
        )
    assert runnable and private == {"_common"}


def _payload():
    import json

    return json.loads((FUSION_SCRIPTS / "frame_params.json").read_text(encoding="utf-8"))
