import copy
import json
import math

from frame_tools import geometry, mass, params, thrust, validate


def test_layout_clears_props():
    p = params.load_params()
    lay = geometry.solve(p)
    assert lay.motor_radius_mm >= lay.min_radius_mm
    assert lay.motor_radius_mm <= lay.max_radius_mm
    # adjacent motors must be at least one prop diameter apart
    assert lay.adjacent_spacing_mm >= p["props"]["diameter_mm"]


def test_motors_are_symmetric():
    lay = geometry.solve(params.load_params())
    assert len(lay.motors) == 4
    assert abs(sum(x for _, x, _ in lay.motors)) < 1e-6
    assert abs(sum(y for _, _, y in lay.motors)) < 1e-6
    for _, x, y in lay.motors:
        assert math.isclose(math.hypot(x, y), lay.motor_radius_mm, rel_tol=1e-9)


def test_mass_and_thrust_are_consistent():
    p = params.load_params()
    lay = geometry.solve(p)
    m = mass.build(p, lay, params.load_loadout())
    t = thrust.build(p, m.total_mass_g)
    assert m.total_mass_g == sum(i.mass_g for i in m.items)
    assert math.isclose(t.twr, t.total_thrust_g / m.total_mass_g)


def test_layout_clears_the_centre_plate():
    """Arms leave at 45 degrees, straight at the plate corners - props must miss them."""
    lay = geometry.solve(params.load_params())
    assert lay.plate_prop_gap_mm > 0
    assert lay.prop_inner_r_mm > lay.plate_corner_r_mm


def test_solver_takes_the_binding_constraint():
    """min_radius is whichever lower bound is larger, never just the prop one."""
    p = copy.deepcopy(params.load_params())

    # A big plate makes the plate corner bind.
    p["center_plate"]["size_mm"] = [90, 90]
    big = geometry.solve(p)
    assert big.min_radius_plate_mm > big.min_radius_props_mm
    assert big.min_radius_mm == big.min_radius_plate_mm

    # A tiny plate hands the constraint back to prop-to-prop.
    p["center_plate"]["size_mm"] = [20, 20]
    small = geometry.solve(p)
    assert small.min_radius_props_mm > small.min_radius_plate_mm
    assert small.min_radius_mm == small.min_radius_props_mm

    for lay in (big, small):
        assert lay.motor_radius_mm >= lay.min_radius_mm


def test_explicit_radius_overrides_the_solver():
    p = copy.deepcopy(params.load_params())
    p["arm"]["motor_radius_mm"] = 95.0
    lay = geometry.solve(p)
    assert lay.auto_solved is False
    assert lay.motor_radius_mm == 95.0
    assert lay.diagonal_mm == 190.0


def test_shipped_design_passes_its_own_validator():
    """params.yaml as committed must be buildable - `frame check` exits 0."""
    p = params.load_params()
    lay = geometry.solve(p)
    m = mass.build(p, lay, params.load_loadout())
    t = thrust.build(p, m.total_mass_g)
    failures = [c for c in validate.run(p, lay, m, t) if c.status == "FAIL"]
    assert not failures, "\n".join(f"{c.name}: {c.detail}" for c in failures)


def test_fusion_payload_is_json_serialisable():
    """`frame fusion` is the handoff to the MCP - it must always encode."""
    lay = geometry.solve(params.load_params())
    payload = json.loads(json.dumps(lay.as_dict()))
    assert set(payload["motors"]) == set(geometry.MOTOR_NAMES)
    assert payload["motor_radius_mm"] == lay.motor_radius_mm
