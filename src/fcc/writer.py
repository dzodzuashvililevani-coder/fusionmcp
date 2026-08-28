"""Surgical writers for measurement-backed project files."""
from __future__ import annotations

from dataclasses import dataclass
import difflib
import os
from pathlib import Path
import re
import tempfile
from typing import Any

import yaml

from fcc.errors import AmbiguousLabel, LabelNotFound, PathRefused, SpecError, UnsurgicalEdit
from fcc.fields import FieldSpec, current_value
from frame_tools.params import project_root

FORBIDDEN_PARTS = {".git", ".venv", "__pycache__", ".pytest_cache"}
FORBIDDEN_PREFIXES = (".pytest-",)


@dataclass(frozen=True)
class WriteResult:
    file: str
    line_number: int
    old_text: str
    new_text: str
    checklist_ticked: bool


def write_value(field: FieldSpec, value: Any, root: Path | None = None) -> WriteResult:
    """Write one field value and tick its measurement checklist line if present."""
    root = root or project_root()
    text = _read_target(root, field.file)
    formatted = _format_value(field, value)

    if field.file == "params.yaml":
        new_text, line_number, old_line, new_line = _replace_params_value(text, field, formatted)
    elif field.file == "components/loadout.yaml":
        new_text, line_number, old_line, new_line = _replace_loadout_value(text, field, formatted)
    else:
        raise UnsurgicalEdit(f"{field.id}: cannot write values to {field.file!r}")

    measurement_update: tuple[str, str] | None = None
    if field.measurement_label:
        measurement_text = _read_target(root, "docs/measurements.md")
        new_measurement, _, _, _ = _replace_measurement(
            measurement_text,
            field.measurement_label,
            formatted,
            field.unit,
        )
        measurement_update = (measurement_text, new_measurement)

    changed = _write_if_changed(root, field.file, text, new_text, validate_yaml=True)
    ticked = False
    if measurement_update is not None:
        measurement_text, new_measurement = measurement_update
        ticked = _write_if_changed(
            root,
            "docs/measurements.md",
            measurement_text,
            new_measurement,
            validate_yaml=False,
        )

    return WriteResult(
        file=field.file,
        line_number=line_number,
        old_text=old_line if changed else new_line,
        new_text=new_line,
        checklist_ticked=ticked,
    )


def tick_measurement(label: str, value: Any, unit: str, root: Path | None = None) -> WriteResult:
    """Fill the exact checklist label and mark that checkbox complete."""
    root = root or project_root()
    relpath = "docs/measurements.md"
    text = _read_target(root, relpath)
    new_text, line_number, old_line, new_line = _replace_measurement(text, label, str(value), unit)
    changed = _write_if_changed(root, relpath, text, new_text, validate_yaml=False)
    return WriteResult(
        file=relpath,
        line_number=line_number,
        old_text=old_line if changed else "",
        new_text=new_line,
        checklist_ticked=changed,
    )


def preview(field: FieldSpec, value: Any, root: Path | None = None) -> str:
    """Return a unified diff of the writes that would happen."""
    root = root or project_root()
    formatted = _format_value(field, value)
    diffs: list[str] = []

    text = _read_target(root, field.file)
    if field.file == "params.yaml":
        new_text, _, _, _ = _replace_params_value(text, field, formatted)
    elif field.file == "components/loadout.yaml":
        new_text, _, _, _ = _replace_loadout_value(text, field, formatted)
    else:
        raise UnsurgicalEdit(f"{field.id}: cannot write values to {field.file!r}")
    diffs.extend(_diff(field.file, text, new_text))

    if field.measurement_label:
        relpath = "docs/measurements.md"
        measurement = _read_target(root, relpath)
        new_measurement, _, _, _ = _replace_measurement(
            measurement,
            field.measurement_label,
            formatted,
            field.unit,
        )
        diffs.extend(_diff(relpath, measurement, new_measurement))

    return "".join(diffs)


def locate(field: FieldSpec, root: Path | None = None) -> tuple[int, str]:
    """Return the 1-based line number and full text of the line this field addresses."""
    root = root or project_root()
    text = _read_target(root, field.file)
    formatted = _format_value(field, current_value(field, root=root))
    if field.file == "params.yaml":
        _, line_number, old_line, _ = _replace_params_value(text, field, formatted)
        return line_number, old_line
    if field.file == "components/loadout.yaml":
        _, line_number, old_line, _ = _replace_loadout_value(text, field, formatted)
        return line_number, old_line
    raise UnsurgicalEdit(f"{field.id}: cannot locate values in {field.file!r}")


def _read_target(root: Path, relpath: str) -> str:
    with _resolve_target(root, relpath).open(encoding="utf-8", newline="") as fh:
        return fh.read()


def _write_if_changed(
    root: Path,
    relpath: str,
    old_text: str,
    new_text: str,
    *,
    validate_yaml: bool,
) -> bool:
    if old_text == new_text:
        return False
    path = _resolve_target(root, relpath)
    _atomic_write(path, new_text, validate_yaml=validate_yaml)
    return True


def _resolve_target(root: Path, relpath: str) -> Path:
    root = root.resolve()
    raw = Path(relpath)
    if raw.is_absolute() or ".." in raw.parts:
        raise PathRefused(f"refused path outside project root: {relpath}")
    path = (root / raw).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise PathRefused(f"refused path outside project root: {relpath}") from exc
    for part in relative.parts:
        if part in FORBIDDEN_PARTS or part.startswith(FORBIDDEN_PREFIXES):
            raise PathRefused(f"refused protected path: {relpath}")
    return path


def _atomic_write(path: Path, text: str, *, validate_yaml: bool) -> None:
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        if validate_yaml:
            with tmp.open(encoding="utf-8") as fh:
                yaml.safe_load(fh)
        os.replace(tmp, path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


def _replace_params_value(text: str, field: FieldSpec, formatted: str) -> tuple[str, int, str, str]:
    section, key = _split_two_part_path(field)
    lines = text.splitlines(keepends=True)
    current_section = ""
    for index, line in enumerate(lines):
        detected = _top_level_section(line)
        if detected:
            current_section = detected
            continue
        if current_section == section and _line_key(line) == key:
            old_line = line
            lines[index] = _replace_yaml_line_value(line, key, formatted, field.index)
            return "".join(lines), index + 1, old_line, lines[index]
    raise UnsurgicalEdit(f"{field.id}: key_path {field.key_path!r} not found on one editable line")


def _replace_loadout_value(text: str, field: FieldSpec, formatted: str) -> tuple[str, int, str, str]:
    if not field.item or not field.field:
        raise UnsurgicalEdit(f"{field.id}: loadout write needs item and field")
    lines = text.splitlines(keepends=True)
    name_pattern = re.compile(rf"\bname:\s*{re.escape(field.item)}(?=[,\s}}])")
    field_pattern = re.compile(rf"(?P<prefix>\b{re.escape(field.field)}:\s*)(?P<value>[^,\s}}]+)")
    for index, line in enumerate(lines):
        if not name_pattern.search(line):
            continue
        match = field_pattern.search(line)
        if not match:
            raise UnsurgicalEdit(f"{field.id}: field {field.field!r} not found in loadout item")
        old_line = line
        lines[index] = line[:match.start("value")] + formatted + line[match.end("value"):]
        return "".join(lines), index + 1, old_line, lines[index]
    raise UnsurgicalEdit(f"{field.id}: loadout item {field.item!r} not found")


def _replace_measurement(text: str, label: str, value: str, unit: str) -> tuple[str, int, str, str]:
    lines = text.splitlines(keepends=True)
    pattern = re.compile(rf"- \[[ xX]\] {re.escape(label)}:")
    hits = [(index, pattern.search(line)) for index, line in enumerate(lines) if pattern.search(line)]
    if not hits:
        raise LabelNotFound(f"measurement label {label!r} not found")
    if len(hits) > 1:
        line_numbers = ", ".join(str(index + 1) for index, _ in hits)
        raise AmbiguousLabel(f"measurement label {label!r} matches multiple lines: {line_numbers}")

    index, match = hits[0]
    assert match is not None
    line = lines[index]
    next_box = re.search(r"\s+- \[[ xX]\] ", line[match.end():])
    segment_end = match.end() + next_box.start() if next_box else len(line.rstrip("\r\n"))
    segment = line[match.start():segment_end]
    new_segment = _fill_measurement_segment(segment, value, unit)
    old_line = line
    lines[index] = line[:match.start()] + new_segment + line[segment_end:]
    return "".join(lines), index + 1, old_line, lines[index]


def _fill_measurement_segment(segment: str, value: str, unit: str) -> str:
    segment = segment.replace("- [ ]", "- [x]", 1).replace("- [X]", "- [x]", 1)
    blank = "____"
    if blank in segment:
        before, after = segment.split(blank, 1)
        if unit and re.match(rf"\s*{re.escape(unit)}(?:\b|$)", after):
            return before + value + after
        suffix = f" {unit}" if unit else ""
        return before + value + suffix + after

    prefix, current = segment.split(":", 1)
    value_text = f"{value} {unit}" if unit else value
    if current.strip() == value_text or current.strip() == value:
        return segment
    return f"{prefix}: {value_text}"


def _replace_yaml_line_value(line: str, key: str, formatted: str, item_index: int | None) -> str:
    content, eol = _split_eol(line)
    comment_at = content.find("#")
    main = content if comment_at == -1 else content[:comment_at]
    comment = "" if comment_at == -1 else content[comment_at:]
    colon = main.find(":")
    if colon == -1:
        raise UnsurgicalEdit(f"{key}: line has no ':' separator")
    prefix = main[: colon + 1]
    value_area = main[colon + 1:]
    leading_len = len(value_area) - len(value_area.lstrip(" "))
    trailing_len = len(value_area) - len(value_area.rstrip(" "))
    leading = value_area[:leading_len]
    trailing = "" if trailing_len == 0 else value_area[-trailing_len:]
    value_text = value_area[leading_len : len(value_area) - trailing_len if trailing_len else len(value_area)]

    if item_index is None:
        new_value = formatted
    else:
        new_value = _replace_inline_list_item(value_text, item_index, formatted)
    return prefix + leading + new_value + trailing + comment + eol


def _replace_inline_list_item(value_text: str, item_index: int, formatted: str) -> str:
    start = value_text.find("[")
    end = value_text.rfind("]")
    if start == -1 or end == -1 or end < start:
        raise UnsurgicalEdit("indexed write needs an inline list")
    inside = value_text[start + 1:end]
    matches = list(re.finditer(r"[^,]+", inside))
    if item_index < 0 or item_index >= len(matches):
        raise UnsurgicalEdit(f"inline list index {item_index} out of range")
    match = matches[item_index]
    chunk = match.group(0)
    leading_len = len(chunk) - len(chunk.lstrip(" "))
    trailing_len = len(chunk) - len(chunk.rstrip(" "))
    leading = chunk[:leading_len]
    trailing = "" if trailing_len == 0 else chunk[-trailing_len:]
    replacement = leading + formatted + trailing
    new_inside = inside[:match.start()] + replacement + inside[match.end():]
    return value_text[: start + 1] + new_inside + value_text[end:]


def _top_level_section(line: str) -> str | None:
    if line.startswith(" "):
        return None
    stripped = line.strip()
    if stripped.startswith("#") or not stripped.endswith(":"):
        return None
    return stripped.removesuffix(":")


def _line_key(line: str) -> str | None:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return None
    if line.startswith(" "):
        match = re.match(r"\s+([A-Za-z_][A-Za-z0-9_]*):", line)
        if match:
            return match.group(1)
    return None


def _split_two_part_path(field: FieldSpec) -> tuple[str, str]:
    parts = field.key_path.split(".")
    if len(parts) != 2:
        raise UnsurgicalEdit(f"{field.id}: only two-part params key paths are supported")
    return parts[0], parts[1]


def _split_eol(line: str) -> tuple[str, str]:
    if line.endswith("\r\n"):
        return line[:-2], "\r\n"
    if line.endswith("\n"):
        return line[:-1], "\n"
    return line, ""


def _format_value(field: FieldSpec, value: Any) -> str:
    try:
        if field.type == "int":
            return str(int(value))
        if field.type == "float":
            return str(float(value))
    except (TypeError, ValueError) as exc:
        raise SpecError(f"{field.id}: value {value!r} cannot be converted to {field.type}") from exc
    raise SpecError(f"{field.id}: unsupported type {field.type!r}")


def _diff(relpath: str, old_text: str, new_text: str) -> list[str]:
    if old_text == new_text:
        return []
    return list(
        difflib.unified_diff(
            old_text.splitlines(keepends=True),
            new_text.splitlines(keepends=True),
            fromfile=f"a/{relpath}",
            tofile=f"b/{relpath}",
        )
    )
