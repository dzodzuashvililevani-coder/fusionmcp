"""Validate surgical measurement writes."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import shutil

import pytest
import yaml

from fcc.errors import LabelNotFound, UnsurgicalEdit
from fcc.fields import field_by_id
from fcc.writer import preview, tick_measurement, write_value
from frame_tools import params as frame_params

ROOT = frame_params.project_root()


def copy_project_data(tmp_path: Path) -> None:
    for directory in ("components", "docs"):
        (tmp_path / directory).mkdir(exist_ok=True)
    for relpath in (
        "params.yaml",
        "components/loadout.yaml",
        "docs/measurements.md",
    ):
        shutil.copy2(ROOT / relpath, tmp_path / relpath)


def changed_line_numbers(before: bytes, after: bytes) -> list[int]:
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    assert len(before_lines) == len(after_lines)
    return [
        index
        for index, (old, new) in enumerate(zip(before_lines, after_lines), start=1)
        if old != new
    ]


def read(tmp_path: Path, relpath: str) -> str:
    return (tmp_path / relpath).read_text(encoding="utf-8")


def read_bytes(tmp_path: Path, relpath: str) -> bytes:
    return (tmp_path / relpath).read_bytes()


def target_line(data: bytes, line_number: int) -> str:
    return data.splitlines(keepends=True)[line_number - 1].decode("utf-8")


def line_ending(data: bytes, line_number: int) -> str:
    line = target_line(data, line_number)
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    return ""


def test_scalar_write_changes_one_line_and_preserves_comment(tmp_path):
    copy_project_data(tmp_path)
    before_params = read_bytes(tmp_path, "params.yaml")
    before_measurements = read_bytes(tmp_path, "docs/measurements.md")
    field = field_by_id("stock_thickness")

    result = write_value(field, 2.7, root=tmp_path)

    after_params = read_bytes(tmp_path, "params.yaml")
    after_measurements = read_bytes(tmp_path, "docs/measurements.md")
    assert changed_line_numbers(before_params, after_params) == [11]
    assert before_params.count(b"#") == after_params.count(b"#")
    assert after_params.count(b"\r\n") == before_params.count(b"\r\n")
    assert after_params.count(b"\n") == before_params.count(b"\n")
    assert result.file == "params.yaml"
    assert result.line_number == 11
    assert result.old_text == target_line(before_params, 11)
    assert result.new_text == target_line(after_params, 11)
    assert result.checklist_ticked is True
    assert changed_line_numbers(before_measurements, after_measurements) == [45]
    assert after_measurements.count(b"\r\n") == before_measurements.count(b"\r\n")
    assert after_measurements.count(b"\n") == before_measurements.count(b"\n")
    after_measurements_text = read(tmp_path, "docs/measurements.md")
    assert "- [x] Actual thickness (measure, do not trust the label): 2.7 mm" in after_measurements_text


def test_inline_list_write_changes_only_target_section_element(tmp_path):
    copy_project_data(tmp_path)
    before = read_bytes(tmp_path, "params.yaml")
    field = field_by_id("battery_width")

    write_value(field, 34.5, root=tmp_path)

    after = read_bytes(tmp_path, "params.yaml")
    assert changed_line_numbers(before, after) == [43]
    after_text = read(tmp_path, "params.yaml")
    assert "  size_mm: [250, 250]\n" in after_text
    assert "  size_mm: [65, 34.5, 18]      # TODO L x W x H\n" in after_text
    assert before.count(b"#") == after.count(b"#")


def test_flow_map_write_changes_only_requested_token(tmp_path):
    copy_project_data(tmp_path)
    before = read_bytes(tmp_path, "components/loadout.yaml")
    field = field_by_id("esc_4in1_mass")

    result = write_value(field, 8.25, root=tmp_path)

    after = read_bytes(tmp_path, "components/loadout.yaml")
    assert changed_line_numbers(before, after) == [10]
    assert after.count(b"\r\n") == before.count(b"\r\n")
    assert after.count(b"\n") == before.count(b"\n")
    assert result.line_number == 10
    after_text = read(tmp_path, "components/loadout.yaml")
    assert "  - { name: esc_4in1,          mass_g: 8.25,  pos_mm: [0,   0,   6]  }   # TODO or omit if ESCs are on the FC\n" in after_text
    data = yaml.safe_load(after_text)
    esc = next(item for item in data["items"] if item["name"] == "esc_4in1")
    assert esc["mass_g"] == 8.25


def test_round_trip_through_frame_params_loader(tmp_path, monkeypatch):
    copy_project_data(tmp_path)
    field = field_by_id("prop_diameter")

    write_value(field, 63.5, root=tmp_path)
    monkeypatch.setattr(frame_params, "project_root", lambda: tmp_path)

    assert frame_params.load_params()["props"]["diameter_mm"] == 63.5


def test_preview_returns_diff_without_writing(tmp_path):
    copy_project_data(tmp_path)
    before_params = read_bytes(tmp_path, "params.yaml")
    before_measurements = read_bytes(tmp_path, "docs/measurements.md")
    field = field_by_id("motor_bolt_circle")

    diff = preview(field, 9.4, root=tmp_path)

    assert "--- a/params.yaml" in diff
    assert "+++ b/docs/measurements.md" in diff
    assert (
        f"+  bolt_circle_mm: 9.4        # TODO measure hole-to-hole across the motor base"
        f"{line_ending(before_params, 23)}"
    ) in diff
    assert (
        f"+- [x] Bolt circle (hole to hole, across the base): 9.4 mm"
        f"{line_ending(before_measurements, 7)}"
    ) in diff
    assert read_bytes(tmp_path, "params.yaml") == before_params
    assert read_bytes(tmp_path, "docs/measurements.md") == before_measurements


def test_parse_failure_leaves_original_file_untouched(tmp_path, monkeypatch):
    copy_project_data(tmp_path)
    before = read_bytes(tmp_path, "params.yaml")
    field = field_by_id("prop_diameter")

    def fail_parse(_file):
        raise yaml.YAMLError("forced parse failure")

    monkeypatch.setattr("fcc.writer.yaml.safe_load", fail_parse)

    with pytest.raises(yaml.YAMLError, match="forced parse failure"):
        write_value(field, 63.5, root=tmp_path)

    assert read_bytes(tmp_path, "params.yaml") == before


def test_missing_measurement_label_is_reported_before_data_write(tmp_path):
    copy_project_data(tmp_path)
    before = read_bytes(tmp_path, "params.yaml")
    field = replace(field_by_id("prop_diameter"), measurement_label="Not a real checklist label")

    with pytest.raises(LabelNotFound, match="Not a real checklist label"):
        write_value(field, 63.5, root=tmp_path)

    assert read_bytes(tmp_path, "params.yaml") == before


def test_idempotent_write_leaves_second_result_identical(tmp_path):
    copy_project_data(tmp_path)
    field = field_by_id("stock_thickness")
    write_value(field, 2.7, root=tmp_path)
    after_first_params = read(tmp_path, "params.yaml")
    after_first_measurements = read(tmp_path, "docs/measurements.md")

    write_value(field, 2.7, root=tmp_path)

    assert read(tmp_path, "params.yaml") == after_first_params
    assert read(tmp_path, "docs/measurements.md") == after_first_measurements


def test_tick_measurement_handles_second_checkbox_on_same_line(tmp_path):
    copy_project_data(tmp_path)
    before = read_bytes(tmp_path, "docs/measurements.md")

    result = tick_measurement("Antenna mass and length", 3.2, "g", root=tmp_path)

    after = read_bytes(tmp_path, "docs/measurements.md")
    assert changed_line_numbers(before, after) == [42]
    assert after.count(b"\r\n") == before.count(b"\r\n")
    assert after.count(b"\n") == before.count(b"\n")
    assert result.line_number == 42
    after_text = read(tmp_path, "docs/measurements.md")
    assert "- [ ] Receiver mass: ____   - [x] Antenna mass and length: 3.2 g" in after_text


@pytest.mark.parametrize(
    ("name", "content"),
    [
        (
            "crlf",
            b"version: 1\r\nstock:\r\n  thickness_mm: 3.0          # keep\r\nprops:\r\n  diameter_mm: 65.0\r\n",
        ),
        (
            "lf",
            b"version: 1\nstock:\n  thickness_mm: 3.0          # keep\nprops:\n  diameter_mm: 65.0\n",
        ),
        (
            "mixed",
            b"version: 1\r\nstock:\r\n  thickness_mm: 3.0          # keep\nprops:\r\n  diameter_mm: 65.0\n",
        ),
    ],
)
def test_params_write_preserves_per_line_terminators_in_synthetic_files(tmp_path, name, content):
    path = tmp_path / "params.yaml"
    path.write_bytes(content)
    field = replace(field_by_id("stock_thickness"), measurement_label=None)

    write_value(field, 2.7, root=tmp_path)

    after = path.read_bytes()
    assert changed_line_numbers(content, after) == [3]
    assert after.count(b"\r\n") == content.count(b"\r\n")
    assert after.count(b"\n") == content.count(b"\n")
    assert yaml.safe_load(after.decode("utf-8"))["stock"]["thickness_mm"] == 2.7


def test_unaddressable_key_path_is_refused(tmp_path):
    copy_project_data(tmp_path)
    field = replace(field_by_id("stock_thickness"), key_path="stock.thickness_mm.extra")

    with pytest.raises(UnsurgicalEdit, match="two-part params key paths"):
        write_value(field, 2.7, root=tmp_path)


def test_writer_source_does_not_call_yaml_dump():
    source = (ROOT / "src" / "fcc" / "writer.py").read_text(encoding="utf-8")

    assert "yaml.dump" not in source
    assert "safe_dump" not in source
