"""Boundary checks for FCC writers."""
from __future__ import annotations

from dataclasses import replace
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

from fastapi.testclient import TestClient
import pytest

from fcc.api.app import create_app
from fcc.errors import PathRefused
from fcc.fields import current_value, field_by_id, load_fields
from fcc.writer import write_value
from frame_tools.report_api import build_report
from frame_tools.params import project_root

ROOT = project_root()


def copy_project_data(tmp_path: Path) -> None:
    for directory in ("components", "docs"):
        (tmp_path / directory).mkdir(exist_ok=True)
    for relpath in (
        "fields.yaml",
        "params.yaml",
        "components/materials.yaml",
        "components/loadout.yaml",
        "docs/measurements.md",
    ):
        shutil.copy2(ROOT / relpath, tmp_path / relpath)


def copy_cli_project(tmp_path: Path) -> None:
    copy_project_data(tmp_path)
    (tmp_path / "src").mkdir(exist_ok=True)
    ignore = shutil.ignore_patterns("__pycache__")
    shutil.copytree(ROOT / "src" / "frame_tools", tmp_path / "src" / "frame_tools", ignore=ignore)
    shutil.copytree(ROOT / "src" / "fcc", tmp_path / "src" / "fcc", ignore=ignore)


def run_frame(tmp_path: Path, *args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    temp_src = str(tmp_path / "src")
    if env.get("PYTHONPATH"):
        env["PYTHONPATH"] = temp_src + os.pathsep + env["PYTHONPATH"]
    else:
        env["PYTHONPATH"] = temp_src
    return subprocess.run(
        [sys.executable, "-m", "frame_tools.cli", *args],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def changed_line_numbers(before: bytes, after: bytes) -> list[int]:
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    assert len(before_lines) == len(after_lines)
    return [
        index
        for index, (old, new) in enumerate(zip(before_lines, after_lines), start=1)
        if old != new
    ]


FIELD_IDS = [field.id for field in load_fields()]


@pytest.mark.parametrize(
    "relpath",
    [
        "../params.yaml",
        "..\\params.yaml",
        ".git/config",
        ".venv/params.yaml",
        ".pytest-work-tmp-copy/params.yaml",
    ],
)
def test_writer_refuses_paths_outside_or_inside_protected_dirs(tmp_path, relpath):
    copy_project_data(tmp_path)
    field = replace(field_by_id("stock_thickness"), file=relpath)

    with pytest.raises(PathRefused):
        write_value(field, 2.7, root=tmp_path)


def test_writer_refuses_absolute_paths(tmp_path):
    copy_project_data(tmp_path)
    outside = tmp_path.parent / "outside.yaml"
    field = replace(field_by_id("stock_thickness"), file=str(outside.resolve()))

    with pytest.raises(PathRefused):
        write_value(field, 2.7, root=tmp_path)


def test_fcc_package_does_not_use_shell_true():
    findings = []
    for path in (ROOT / "src" / "fcc").glob("*.py"):
        if "shell=True" in path.read_text(encoding="utf-8"):
            findings.append(path.relative_to(ROOT).as_posix())

    assert not findings


def test_frame_fields_lists_all_fields_values_questions_and_todo_status(tmp_path):
    copy_cli_project(tmp_path)

    result = run_frame(tmp_path, "fields")

    assert result.returncode == 0, result.stderr
    fields = load_fields(root=tmp_path)
    for field in fields:
        assert field.id in result.stdout
        assert field.question in result.stdout
    stock = field_by_id("stock_thickness", root=tmp_path)
    assert f"{current_value(stock, root=tmp_path):g} mm" in result.stdout
    assert re.search(r"stock_thickness\s+3 mm\s+\[TODO guess\]", result.stdout)


def test_frame_set_writes_value_ticks_checklist_and_prints_check_summary(tmp_path):
    copy_cli_project(tmp_path)
    before_params = (tmp_path / "params.yaml").read_bytes()
    before_measurements = (tmp_path / "docs" / "measurements.md").read_bytes()

    result = run_frame(tmp_path, "set", "stock_thickness", "3.2")

    assert result.returncode == 0, result.stderr
    assert "FIELD WRITE" in result.stdout
    assert "changed             params.yaml:11" in result.stdout
    assert "checklist           ticked" in result.stdout
    assert "PRE-CUT CHECKS" in result.stdout
    assert "10 passed, 0 warnings, 0 failures" in result.stdout

    after_params = (tmp_path / "params.yaml").read_bytes()
    after_measurements = (tmp_path / "docs" / "measurements.md").read_bytes()
    assert changed_line_numbers(before_params, after_params) == [11]
    assert after_params.count(b"\r\n") == before_params.count(b"\r\n")
    assert after_params.count(b"\n") == before_params.count(b"\n")
    assert changed_line_numbers(before_measurements, after_measurements) == [45]
    assert after_measurements.count(b"\r\n") == before_measurements.count(b"\r\n")
    assert after_measurements.count(b"\n") == before_measurements.count(b"\n")

    fields = run_frame(tmp_path, "fields")
    assert fields.returncode == 0, fields.stderr
    assert re.search(r"stock_thickness\s+3\.2 mm\s+\[measured\]", fields.stdout)


def test_frame_set_saves_out_of_range_value_and_reports_failed_validation(tmp_path):
    copy_cli_project(tmp_path)

    result = run_frame(tmp_path, "set", "stock_thickness", "0.5")

    assert result.returncode == 0, result.stderr
    assert "[warn] stock_thickness is outside the expected 1..8 mm range. Value saved anyway." in result.stdout
    assert "[FAIL] stock thickness" in result.stdout
    assert "0.5mm - thin plywood arms flex and cause gyro noise; 3mm+ recommended" in result.stdout
    assert "This design does not currently validate. The measurement was saved" in result.stdout
    assert "thickness_mm: 0.5" in (tmp_path / "params.yaml").read_text(encoding="utf-8")
    assert "- [x] Actual thickness (measure, do not trust the label): 0.5 mm" in (
        tmp_path / "docs" / "measurements.md"
    ).read_text(encoding="utf-8")


def test_frame_set_unknown_id_exits_nonzero_and_lists_valid_ids(tmp_path):
    copy_cli_project(tmp_path)

    result = run_frame(tmp_path, "set", "not_a_field", "2.7")

    assert result.returncode != 0
    assert "unknown field id 'not_a_field'" in result.stderr
    assert "valid ids:" in result.stderr
    assert "stock_thickness" in result.stderr
    assert "receiver_mass" in result.stderr


@pytest.mark.parametrize("field_id", FIELD_IDS)
def test_frame_fields_and_api_fields_report_same_status_and_line(tmp_path, field_id):
    copy_cli_project(tmp_path)
    cli = run_frame(tmp_path, "fields")
    api = TestClient(create_app(report_provider=lambda: build_report(tmp_path), root=tmp_path))
    fields = api.get("/api/fields")

    assert cli.returncode == 0, cli.stderr
    assert fields.status_code == 200
    api_field = next(field for field in fields.json()["fields"] if field["id"] == field_id)
    match = re.search(
        rf"^\s*{re.escape(field_id)}\s+.*\[(?P<status>TODO guess|measured)\]\s+"
        rf"{re.escape(api_field['file'])}:(?P<line>\d+)$",
        cli.stdout,
        re.MULTILINE,
    )
    assert match is not None
    cli_status = "todo" if match.group("status") == "TODO guess" else "measured"
    assert cli_status == api_field["status"]
    assert int(match.group("line")) == api_field["line"]


def test_cli_and_api_do_not_define_duplicate_field_helpers():
    offenders = []
    for relpath in ("src/fcc/api/routes.py", "src/frame_tools/cli.py"):
        text = (ROOT / relpath).read_text(encoding="utf-8")
        for name in ("_target_line", "_is_todo", "_is_todo_guess", "_coerce_value"):
            if re.search(rf"^def {name}\(", text, re.MULTILINE):
                offenders.append(f"{relpath}:{name}")

    assert not offenders


def test_only_cli_and_report_adapter_import_fcc_from_frame_tools():
    allowed = {"cli.py", "report_api.py"}
    findings = []
    for path in (ROOT / "src" / "frame_tools").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if path.name not in allowed and ("from fcc" in text or "import fcc" in text):
            findings.append(path.relative_to(ROOT).as_posix())

    assert not findings
    assert "from fcc" in (ROOT / "src" / "frame_tools" / "cli.py").read_text(encoding="utf-8")
    assert "from fcc.api" in (ROOT / "src" / "frame_tools" / "report_api.py").read_text(encoding="utf-8")
