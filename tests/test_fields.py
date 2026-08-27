"""Validate the measurement field specification."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from fcc.errors import LabelNotFound, SpecError
from fcc.fields import FieldSpec, current_value, field_by_id, load_fields
from frame_tools.params import project_root

ROOT = project_root()

EXPECTED_TODO_FIELDS = {
    "stock_thickness",
    "prop_diameter",
    "motor_bolt_circle",
    "motor_base_diameter",
    "motor_mass",
    "motor_max_thrust",
    "center_plate_width",
    "center_plate_length",
    "fc_hole_pattern",
    "battery_length",
    "battery_width",
    "battery_height",
    "battery_mass",
    "camera_width",
    "camera_mount_ear_spacing",
    "flight_controller_mass",
    "esc_4in1_mass",
    "camera_mass",
    "vtx_mass",
    "antenna_mass",
    "receiver_mass",
}


def write_spec(tmp_path: Path, mutate) -> Path:
    data = yaml.safe_load((ROOT / "fields.yaml").read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "fields.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def test_load_fields_returns_all_todo_backed_measurements():
    fields = load_fields()
    ids = {field.id for field in fields}

    assert len(fields) == 21
    assert ids == EXPECTED_TODO_FIELDS


def test_fields_are_valid_by_construction():
    for field in load_fields():
        assert isinstance(field, FieldSpec)
        assert field.min <= field.max
        assert field.unit in {"mm", "g", "deg", "count"}
        assert field.type in {"float", "int"}
        assert field.file in {"params.yaml", "components/loadout.yaml", "docs/measurements.md"}
        assert field.question
        assert field.shape_hint
        current_value(field)


def test_inline_list_fields_address_one_element():
    width = field_by_id("center_plate_width")
    length = field_by_id("center_plate_length")
    battery_height = field_by_id("battery_height")

    assert width.key_path == "center_plate.size_mm"
    assert width.index == 0
    assert current_value(width) == 70
    assert length.index == 1
    assert current_value(length) == 70
    assert battery_height.key_path == "battery.size_mm"
    assert battery_height.index == 2
    assert current_value(battery_height) == 18


def test_loadout_fields_address_named_flow_map_items():
    field = field_by_id("esc_4in1_mass")

    assert field.file == "components/loadout.yaml"
    assert field.item == "esc_4in1"
    assert field.field == "mass_g"
    assert current_value(field) == 7.0


def test_duplicate_id_is_rejected(tmp_path):
    spec = write_spec(tmp_path, lambda data: data["fields"].__setitem__(1, dict(data["fields"][0])))

    with pytest.raises(SpecError, match="duplicate id"):
        load_fields(spec_path=spec)


def test_bad_key_path_is_rejected(tmp_path):
    def mutate(data):
        data["fields"][0]["key_path"] = "stock.nope"

    spec = write_spec(tmp_path, mutate)

    with pytest.raises(SpecError, match="key_path"):
        load_fields(spec_path=spec)


def test_bad_file_is_rejected(tmp_path):
    def mutate(data):
        data["fields"][0]["file"] = "../params.yaml"

    spec = write_spec(tmp_path, mutate)

    with pytest.raises(SpecError, match="file must be"):
        load_fields(spec_path=spec)


def test_reversed_range_is_rejected(tmp_path):
    def mutate(data):
        data["fields"][0]["min"] = 10
        data["fields"][0]["max"] = 1

    spec = write_spec(tmp_path, mutate)

    with pytest.raises(SpecError, match="min must be <= max"):
        load_fields(spec_path=spec)


def test_missing_measurement_label_is_rejected(tmp_path):
    def mutate(data):
        data["fields"][0]["measurement_label"] = "not a real label"

    spec = write_spec(tmp_path, mutate)

    with pytest.raises(LabelNotFound, match="not found"):
        load_fields(spec_path=spec)
