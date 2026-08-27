"""Enforce the folder-index convention.

Every folder carries a README.md that says what lives there, what data type it
holds, and gives portal links. These tests keep that from rotting.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from frame_tools.params import project_root

ROOT = project_root()
SKIP = {
    ".git", ".venv", "__pycache__", ".pytest_cache", ".pytest-run-tmp",
    ".pytest-work-tmp",
    ".claude", ".codex", ".agents", "node_modules",
}
DATA_TYPES = {
    "YAML", "Python", "Python (in Fusion)", "Markdown", "JSON",
    "Vector", "Binary CAD", "Raster",
}


def indexed_dirs() -> list[Path]:
    out = []
    for path in ROOT.rglob("*"):
        if not path.is_dir():
            continue
        if any(part in SKIP or part.endswith(".egg-info") for part in path.relative_to(ROOT).parts):
            continue
        out.append(path)
    return sorted(out)


def _read_or_skip(folder: Path) -> str:
    """Content of the folder README, or skip - the missing-README test reports it."""
    readme = folder / "README.md"
    if not readme.exists():
        pytest.skip("no README.md - see test_folder_has_readme")
    return readme.read_text(encoding="utf-8")


@pytest.mark.parametrize("folder", indexed_dirs(), ids=lambda p: str(p.relative_to(ROOT)))
def test_folder_has_readme(folder: Path):
    readme = folder / "README.md"
    assert readme.exists(), (
        f"{folder.relative_to(ROOT)}/ has no README.md. "
        "Every folder needs one - see CLAUDE.md."
    )


@pytest.mark.parametrize("folder", indexed_dirs(), ids=lambda p: str(p.relative_to(ROOT)))
def test_readme_declares_purpose_and_portals(folder: Path):
    text = _read_or_skip(folder)
    assert "**Purpose:**" in text, f"{folder.name}/README.md is missing a **Purpose:** line"
    assert "## Portals" in text, f"{folder.name}/README.md is missing a ## Portals table"


@pytest.mark.parametrize("folder", indexed_dirs(), ids=lambda p: str(p.relative_to(ROOT)))
def test_readme_uses_known_data_types(folder: Path):
    """Portal tables must tag rows with a type from CLAUDE.md's vocabulary."""
    text = _read_or_skip(folder)
    portals = text.split("## Portals", 1)[1]
    rows = [ln for ln in portals.splitlines() if ln.startswith("|") and "---" not in ln][1:]
    rows = [r for r in rows if r.strip().startswith("|")]
    assert rows, f"{folder.name}/README.md has an empty Portals table"

    used = set()
    for row in rows:
        cells = [c.strip().strip("*_`") for c in row.strip("|").split("|")]
        used.update(c for c in cells if c in DATA_TYPES)
    assert used, (
        f"{folder.name}/README.md portal table declares no known data type. "
        f"Use one of: {', '.join(sorted(DATA_TYPES))}"
    )


def test_root_index_exists():
    assert (ROOT / "CLAUDE.md").exists(), "CLAUDE.md is the master index - do not delete it"
