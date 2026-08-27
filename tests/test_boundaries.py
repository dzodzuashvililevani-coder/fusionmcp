"""Boundary checks for FCC writers."""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from fcc.errors import PathRefused
from fcc.fields import field_by_id
from fcc.writer import write_value
from frame_tools.params import project_root

ROOT = project_root()


def copy_project_data(tmp_path: Path) -> None:
    for directory in ("components", "docs"):
        (tmp_path / directory).mkdir(exist_ok=True)
    for relpath in (
        "params.yaml",
        "components/loadout.yaml",
        "docs/measurements.md",
    ):
        (tmp_path / relpath).write_text((ROOT / relpath).read_text(encoding="utf-8"), encoding="utf-8")


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


def test_frame_tools_do_not_import_fcc_before_cli_phase():
    findings = []
    for path in (ROOT / "src" / "frame_tools").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "from fcc" in text or "import fcc" in text:
            findings.append(path.relative_to(ROOT).as_posix())

    assert not findings
