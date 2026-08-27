"""Pytest configuration shared by both agent environments."""
from __future__ import annotations

from pathlib import Path
import shutil
import tempfile
import uuid


def pytest_configure(config):
    """Choose a writable basetemp when pytest's default is blocked."""
    if getattr(config.option, "basetemp", None):
        return
    config.option.basetemp = str(_select_basetemp())


def _select_basetemp() -> Path:
    root = Path(__file__).resolve().parent
    candidates = [
        Path(tempfile.gettempdir()) / "fcc-pytest-basetemp",
        root / ".pytest-work-tmp",
    ]
    for candidate in candidates:
        if _can_use(candidate):
            return candidate
    raise RuntimeError("no writable pytest basetemp found")


def _can_use(path: Path) -> bool:
    probe = path / f".probe-{uuid.uuid4().hex}"
    try:
        path.mkdir(parents=True, exist_ok=True)
        probe.mkdir()
        (probe / "write-check.txt").write_text("ok", encoding="utf-8")
        list(path.iterdir())
    except OSError:
        return False
    finally:
        shutil.rmtree(probe, ignore_errors=True)
    return True
