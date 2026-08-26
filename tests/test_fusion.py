"""The Fusion handoff and the generated cut files.

These are the two places where a number leaves the project and reaches a
machine, so they get tested harder than the rest.
"""
from __future__ import annotations

import copy
import json
import re

import pytest

from frame_tools import dxf_out, fusion, geometry, mass, params, thrust, validate

IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


@pytest.fixture(scope="module")
def payload():
    p = params.load_params()
    lay = geometry.solve(p)
    m = mass.build(p, lay, params.load_loadout())
    t = thrust.build(p, m.total_mass_g)
    return fusion.build_payload(p, lay, m, t, validate.run(p, lay, m, t))


def test_payload_round_trips_through_json(payload):
    assert json.loads(json.dumps(payload)) == payload


def test_user_parameter_names_are_valid_fusion_identifiers(payload):
    """Fusion rejects a parameter name that is not an identifier, and it does so
    halfway through the sync - leaving the model half updated."""
    for name in payload["user_parameters"]:
        assert IDENTIFIER.match(name), f"{name!r} is not a legal Fusion parameter name"


def test_user_parameters_carry_a_unit_and_a_comment(payload):
    for name, spec in payload["user_parameters"].items():
        assert spec["unit"] in {"mm", "deg"}, f"{name} has unit {spec['unit']!r}"
        assert isinstance(spec["value"], (int, float)), f"{name} value is not numeric"
        assert spec["comment"], f"{name} has no comment - it will be a mystery in Fusion"


def test_every_motor_position_is_exported(payload):
    names = set(payload["user_parameters"])
    for abbrev in ("fr", "fl", "rl", "rr"):
        assert f"motor_{abbrev}_x" in names
        assert f"motor_{abbrev}_y" in names


def test_payload_agrees_with_the_solver(payload):
    """Fusion must not be told a different radius from the one `frame geometry`
    printed - that divergence is invisible until the parts do not fit."""
    lay = geometry.solve(params.load_params())
    up = payload["user_parameters"]
    assert up["motor_radius"]["value"] == pytest.approx(lay.motor_radius_mm)
    assert up["motor_diagonal"]["value"] == pytest.approx(lay.diagonal_mm)
    assert up["arm_length"]["value"] == pytest.approx(lay.arm_length_mm)
    assert payload["layout"]["motor_radius_mm"] == lay.motor_radius_mm


def test_payload_reports_buildability(payload):
    assert payload["buildable"] is True
    assert payload["checks"]["failures"] == []


def test_failing_design_is_marked_unbuildable():
    """A design that fails validation must say so in the payload, so the Fusion
    scripts can refuse to export a cut file from it."""
    p = copy.deepcopy(params.load_params())
    p["motors"]["max_thrust_g"] = 5          # nowhere near enough to fly
    lay = geometry.solve(p)
    m = mass.build(p, lay, params.load_loadout())
    t = thrust.build(p, m.total_mass_g)
    bad = fusion.build_payload(p, lay, m, t, validate.run(p, lay, m, t))
    assert bad["buildable"] is False
    assert "thrust-to-weight" in bad["checks"]["failures"]


def test_screw_holes_are_bigger_than_the_screw():
    p = params.load_params()
    for designation in (p["motors"]["screw"], p["center_plate"]["fc_screw"]):
        nominal = params.screw_diameter_mm(designation)
        assert params.hole_diameter_mm(p, designation) > nominal


@pytest.mark.parametrize("bad", ["2", "", "MM", "M0", "Mx"])
def test_bad_screw_designations_are_rejected(bad):
    with pytest.raises(ValueError):
        params.screw_diameter_mm(bad)


def test_kerf_test_dxf_has_the_documented_layers(tmp_path):
    ezdxf = pytest.importorskip("ezdxf", reason="install with: uv pip install -e \".[dxf]\"")
    path, sizes = dxf_out.write_kerf_test(params.load_params(), tmp_path / "kerf_test.dxf")
    assert path.exists() and sizes

    doc = ezdxf.readfile(path)
    layers = {layer.dxf.name for layer in doc.layers}
    assert set(dxf_out.LAYERS).issubset(layers)

    msp = doc.modelspace()
    squares = [e for e in msp if e.dxftype() == "LWPOLYLINE" and e.dxf.layer == "CUT"]
    assert len(squares) == len(sizes)
    assert [e for e in msp if e.dxftype() == "CIRCLE" and e.dxf.layer == "HOLES"]


def test_kerf_test_squares_are_their_nominal_size(tmp_path):
    """The coupon is only a measuring tool if the geometry is exactly nominal -
    kerf compensation happens in the cutter, never here."""
    ezdxf = pytest.importorskip("ezdxf")
    path, sizes = dxf_out.write_kerf_test(params.load_params(), tmp_path / "k.dxf")
    msp = ezdxf.readfile(path).modelspace()

    measured = []
    for entity in msp:
        if entity.dxftype() != "LWPOLYLINE" or entity.dxf.layer != "CUT":
            continue
        xs = [p[0] for p in entity.get_points("xy")]
        ys = [p[1] for p in entity.get_points("xy")]
        measured.append(round(max(xs) - min(xs), 6))
        assert max(ys) - min(ys) == pytest.approx(max(xs) - min(xs))

    assert sorted(measured) == sorted(sizes)
