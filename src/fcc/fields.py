"""Load and validate the measurement field specification."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

import yaml

from fcc.errors import AmbiguousLabel, LabelNotFound, SpecError
from frame_tools.params import project_root

ALLOWED_FILES = {"params.yaml", "components/loadout.yaml", "docs/measurements.md"}
ALLOWED_TYPES = {"float", "int"}
ALLOWED_UNITS = {"mm", "g", "deg", "count"}
FIELD_ID = re.compile(r"^[a-z][a-z0-9_]*$")


@dataclass(frozen=True)
class FieldSpec:
    id: str
    question: str
    unit: str
    file: str
    key_path: str
    index: int | None
    item: str | None
    field: str | None
    measurement_label: str | None
    min: float
    max: float
    type: str
    shape_hint: str


def load_fields(spec_path: Path | None = None, root: Path | None = None) -> list[FieldSpec]:
    """Return validated fields from fields.yaml."""
    root = root or project_root()
    spec_path = spec_path or root / "fields.yaml"
    data = _load_spec(spec_path)
    fields = [_field_from_mapping(row) for row in data["fields"]]
    _validate_fields(fields, root)
    return fields


def field_by_id(field_id: str, spec_path: Path | None = None, root: Path | None = None) -> FieldSpec:
    """Return one field by stable id."""
    fields = load_fields(spec_path=spec_path, root=root)
    for field in fields:
        if field.id == field_id:
            return field
    valid = ", ".join(field.id for field in fields)
    raise SpecError(f"unknown field id {field_id!r}; valid ids: {valid}")


def current_value(field: FieldSpec, root: Path | None = None) -> Any:
    """Read the current value addressed by a field from project files."""
    root = root or project_root()
    if field.file == "params.yaml":
        value = _resolve_key_path(_load_yaml(root, "params.yaml"), field.key_path, field.id)
        if field.index is not None:
            return value[field.index]
        return value
    if field.file == "components/loadout.yaml":
        item = _loadout_item(field.item, field.id, root)
        return item[field.field]
    if field.file == "docs/measurements.md":
        return None
    raise SpecError(f"{field.id}: unsupported file {field.file!r}")


def coerce_value(field: FieldSpec, value: str | int | float) -> int | float:
    """Parse user input for a field without applying range policy."""
    try:
        if field.type == "int":
            return int(value)
        if field.type == "float":
            return float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field.id}: value {value!r} cannot be converted to {field.type}") from exc
    raise ValueError(f"{field.id}: unsupported type {field.type!r}")


def is_todo_guess(field: FieldSpec, root: Path | None = None) -> bool:
    """Return whether a field still appears to hold an unmeasured TODO value."""
    root = root or project_root()
    if field.measurement_label:
        return not _measurement_is_ticked(field, root)
    line = _target_line(field, root)
    return "# TODO" in line


def _load_spec(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SpecError(f"missing field spec: {path}")
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if data.get("version") != 1:
        raise SpecError("fields.yaml: version must be 1")
    if not isinstance(data.get("fields"), list):
        raise SpecError("fields.yaml: fields must be a list")
    return data


def _field_from_mapping(row: Any) -> FieldSpec:
    if not isinstance(row, dict):
        raise SpecError("field row must be a mapping")
    required = {
        "id", "question", "unit", "file", "key_path", "index", "item",
        "field", "measurement_label", "min", "max", "type", "shape_hint",
    }
    missing = sorted(required - set(row))
    if missing:
        name = row.get("id", "<unknown>")
        raise SpecError(f"{name}: missing keys: {', '.join(missing)}")
    try:
        return FieldSpec(
            id=str(row["id"]),
            question=str(row["question"]),
            unit=str(row["unit"]),
            file=str(row["file"]),
            key_path=str(row["key_path"]),
            index=None if row["index"] is None else int(row["index"]),
            item=None if row["item"] is None else str(row["item"]),
            field=None if row["field"] is None else str(row["field"]),
            measurement_label=None
            if row["measurement_label"] is None
            else str(row["measurement_label"]),
            min=float(row["min"]),
            max=float(row["max"]),
            type=str(row["type"]),
            shape_hint=str(row["shape_hint"]),
        )
    except (TypeError, ValueError) as exc:
        name = row.get("id", "<unknown>")
        raise SpecError(f"{name}: invalid field value") from exc


def _validate_fields(fields: list[FieldSpec], root: Path) -> None:
    seen: set[str] = set()
    seen_labels: dict[str, str] = {}
    for field in fields:
        _validate_field_shape(field, seen)
        if field.file == "params.yaml":
            _validate_params_field(field, root)
        elif field.file == "components/loadout.yaml":
            _validate_loadout_field(field, root)
        elif field.file == "docs/measurements.md":
            pass
        else:
            raise SpecError(f"{field.id}: unsupported file {field.file!r}")
        if field.measurement_label:
            owner = seen_labels.get(field.measurement_label)
            if owner is not None:
                raise AmbiguousLabel(
                    f"{field.id}: measurement label {field.measurement_label!r} "
                    f"is already used by {owner!r}"
                )
            seen_labels[field.measurement_label] = field.id
            _validate_measurement_label(field, root)


def _validate_field_shape(field: FieldSpec, seen: set[str]) -> None:
    if not FIELD_ID.match(field.id):
        raise SpecError(f"{field.id}: id must be snake_case")
    if field.id in seen:
        raise SpecError(f"{field.id}: duplicate id")
    seen.add(field.id)
    if field.file not in ALLOWED_FILES:
        raise SpecError(f"{field.id}: file must be one of {sorted(ALLOWED_FILES)}")
    if field.unit not in ALLOWED_UNITS:
        raise SpecError(f"{field.id}: unsupported unit {field.unit!r}")
    if field.type not in ALLOWED_TYPES:
        raise SpecError(f"{field.id}: unsupported type {field.type!r}")
    if field.min > field.max:
        raise SpecError(f"{field.id}: min must be <= max")
    if not field.question.strip():
        raise SpecError(f"{field.id}: question is required")
    if not field.shape_hint.strip():
        raise SpecError(f"{field.id}: shape_hint is required")


def _validate_params_field(field: FieldSpec, root: Path) -> None:
    if field.item is not None or field.field is not None:
        raise SpecError(f"{field.id}: item/field only apply to loadout.yaml")
    value = _resolve_key_path(_load_yaml(root, "params.yaml"), field.key_path, field.id)
    if field.index is not None:
        if not isinstance(value, list):
            raise SpecError(f"{field.id}: index given for non-list key_path")
        if field.index < 0 or field.index >= len(value):
            raise SpecError(f"{field.id}: index {field.index} out of range")


def _validate_loadout_field(field: FieldSpec, root: Path) -> None:
    if field.index is not None:
        raise SpecError(f"{field.id}: index is not used for loadout fields")
    if not field.item or not field.field:
        raise SpecError(f"{field.id}: loadout fields need item and field")
    item = _loadout_item(field.item, field.id, root)
    if field.field not in item:
        raise SpecError(f"{field.id}: item {field.item!r} has no field {field.field!r}")


def _validate_measurement_label(field: FieldSpec, root: Path) -> None:
    lines = (root / "docs" / "measurements.md").read_text(encoding="utf-8").splitlines()
    label = re.escape(field.measurement_label or "")
    pattern = re.compile(rf"(?:^|\s)- \[[ xX]\] {label}:")
    hits = [number for number, line in enumerate(lines, start=1) if pattern.search(line)]
    if not hits:
        raise LabelNotFound(f"{field.id}: measurement label {field.measurement_label!r} not found")
    if len(hits) > 1:
        joined = ", ".join(str(hit) for hit in hits)
        raise AmbiguousLabel(
            f"{field.id}: measurement label {field.measurement_label!r} "
            f"matches multiple checklist lines: {joined}"
        )


def _measurement_is_ticked(field: FieldSpec, root: Path) -> bool:
    text = (root / "docs" / "measurements.md").read_text(encoding="utf-8")
    label = re.escape(field.measurement_label or "")
    pattern = re.compile(rf"- \[(?P<mark>[ xX])\] {label}:")
    for line in text.splitlines():
        match = pattern.search(line)
        if match:
            return match.group("mark").lower() == "x"
    return False


def _target_line(field: FieldSpec, root: Path) -> str:
    text = (root / field.file).read_text(encoding="utf-8")
    if field.file == "params.yaml":
        section, key = field.key_path.split(".", 1)
        current_section = ""
        for line in text.splitlines():
            stripped = line.strip()
            if line and not line.startswith(" ") and stripped.endswith(":"):
                current_section = stripped.removesuffix(":")
                continue
            if current_section == section and re.match(rf"\s+{re.escape(key)}:", line):
                return line
    if field.file == "components/loadout.yaml" and field.item and field.field:
        name_pattern = re.compile(rf"\bname:\s*{re.escape(field.item)}(?=[,\s}}])")
        field_pattern = re.compile(rf"\b{re.escape(field.field)}:")
        for line in text.splitlines():
            if name_pattern.search(line) and field_pattern.search(line):
                return line
    return ""


def _resolve_key_path(data: dict[str, Any], key_path: str, field_id: str) -> Any:
    value: Any = data
    for key in key_path.split("."):
        if not isinstance(value, dict) or key not in value:
            raise SpecError(f"{field_id}: key_path {key_path!r} does not resolve")
        value = value[key]
    return value


def _load_yaml(root: Path, relpath: str) -> Any:
    path = root / relpath
    if not path.exists():
        raise SpecError(f"missing {relpath}")
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _loadout_item(name: str | None, field_id: str, root: Path) -> dict[str, Any]:
    for item in _load_yaml(root, "components/loadout.yaml").get("items", []):
        if item.get("name") == name:
            return item
    raise SpecError(f"{field_id}: loadout item {name!r} not found")
