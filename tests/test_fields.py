"""Validate the measurement field specification."""
from __future__ import annotations

from pathlib import Path
import re

import pytest
import yaml

from fcc.errors import AmbiguousLabel, LabelNotFound, SpecError
from fcc.fields import FieldSpec, current_value, field_by_id, load_fields
from frame_tools.params import project_root

ROOT = project_root()


def write_spec(tmp_path: Path, mutate) -> Path:
    data = yaml.safe_load((ROOT / "fields.yaml").read_text(encoding="utf-8"))
    mutate(data)
    path = tmp_path / "fields.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def copy_project_data(tmp_path: Path) -> None:
    for directory in ("components", "docs"):
        (tmp_path / directory).mkdir(exist_ok=True)
    for relpath in (
        "params.yaml",
        "components/loadout.yaml",
        "docs/measurements.md",
    ):
        (tmp_path / relpath).write_text((ROOT / relpath).read_text(encoding="utf-8"), encoding="utf-8")


def test_load_fields_returns_all_todo_backed_measurements():
    fields = load_fields()

    assert len(fields) == 21


def test_every_todo_target_has_a_field_and_every_field_targets_a_todo():
    fields = load_fields()
    expected = todo_targets(
        (ROOT / "params.yaml").read_text(encoding="utf-8"),
        (ROOT / "components" / "loadout.yaml").read_text(encoding="utf-8"),
    )
    actual = {target_for_field(field) for field in fields}

    assert expected - actual == set(), f"TODO targets without fields: {sorted(expected - actual)}"
    assert actual - expected == set(), f"fields without TODO targets: {sorted(actual - expected)}"


def test_todo_coverage_detects_orphaned_param_todo():
    params_text = (ROOT / "params.yaml").read_text(encoding="utf-8")
    params_text = params_text.replace(
        "kerf_mm: 0.2               # laser",
        "kerf_mm: 0.2               # TODO laser",
        1,
    )
    expected = todo_targets(
        params_text,
        (ROOT / "components" / "loadout.yaml").read_text(encoding="utf-8"),
    )
    actual = {target_for_field(field) for field in load_fields()}

    assert "params.yaml:stock.kerf_mm" in expected - actual


def test_fields_are_valid_by_construction():
    fields = load_fields()
    labels = [field.measurement_label for field in fields if field.measurement_label]

    assert len(labels) == len(set(labels))
    for field in fields:
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


def test_current_value_uses_supplied_root(tmp_path):
    copy_project_data(tmp_path)
    spec = write_spec(tmp_path, lambda data: data)
    params_path = tmp_path / "params.yaml"
    params_path.write_text(
        params_path.read_text(encoding="utf-8").replace("thickness_mm: 3.0", "thickness_mm: 2.4", 1),
        encoding="utf-8",
    )

    field = field_by_id("stock_thickness", spec_path=spec, root=tmp_path)

    assert current_value(field, root=tmp_path) == 2.4


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


def test_duplicate_measurement_label_is_rejected(tmp_path):
    def mutate(data):
        data["fields"][1]["measurement_label"] = data["fields"][0]["measurement_label"]

    spec = write_spec(tmp_path, mutate)

    with pytest.raises(AmbiguousLabel, match="already used"):
        load_fields(spec_path=spec)


def test_ambiguous_checklist_label_is_rejected(tmp_path):
    copy_project_data(tmp_path)

    def mutate(data):
        data["fields"][0]["measurement_label"] = "Repeated label"

    spec = write_spec(tmp_path, mutate)
    (tmp_path / "docs" / "measurements.md").write_text(
        "# Measurements\n"
        "- [ ] Repeated label: ____ mm\n"
        "- [ ] Repeated label: ____ mm\n",
        encoding="utf-8",
    )

    with pytest.raises(AmbiguousLabel, match="multiple checklist lines"):
        load_fields(spec_path=spec, root=tmp_path)


def todo_targets(params_text: str, loadout_text: str) -> set[str]:
    return _params_todo_targets(params_text) | _loadout_todo_targets(loadout_text)


def target_for_field(field: FieldSpec) -> str:
    if field.file == "params.yaml":
        return f"params.yaml:{field.key_path}"
    if field.file == "components/loadout.yaml":
        return f"components/loadout.yaml:{field.item}.{field.field}"
    return f"{field.file}:{field.key_path}"


def _params_todo_targets(text: str) -> set[str]:
    section = ""
    targets: set[str] = set()
    for line in text.splitlines():
        if not line.startswith(" ") and line.rstrip().endswith(":"):
            section = line.strip().removesuffix(":")
            continue
        if "# TODO" not in line:
            continue
        stripped = line.strip()
        if stripped.startswith("#") or ":" not in stripped:
            continue
        key = stripped.split(":", 1)[0].strip()
        targets.add(f"params.yaml:{section}.{key}")
    return targets


def _loadout_todo_targets(text: str) -> set[str]:
    targets: set[str] = set()
    for line in text.splitlines():
        if "# TODO" not in line:
            continue
        name_match = re.search(r"name:\s*([^,\s}]+)", line)
        if name_match and "mass_g:" in line:
            targets.add(f"components/loadout.yaml:{name_match.group(1)}.mass_g")
    return targets
