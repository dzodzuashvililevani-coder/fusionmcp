"""Pytest configuration shared by both agent environments."""
from __future__ import annotations

import getpass
from pathlib import Path
import shutil
import tempfile
import uuid
import warnings


def pytest_configure(config):
    """Choose a writable basetemp when pytest's default is blocked."""
    if getattr(config.option, "basetemp", None):
        return
    selected = _select_basetemp()
    if selected is not None:
        config.option.basetemp = str(selected)


def _select_basetemp() -> Path | None:
    root = Path(__file__).resolve().parent
    default = Path(tempfile.gettempdir()) / f"pytest-of-{getpass.getuser()}"
    if default.exists() and _can_use(default):
        return None

    for parent, prefix in (
        (Path(tempfile.gettempdir()), "fcc-pytest-basetemp-"),
        (root, ".pytest-work-tmp-"),
    ):
        candidate = _mkdtemp(parent, prefix)
        if candidate is None:
            continue
        if _can_use(candidate):
            return candidate
        shutil.rmtree(candidate, ignore_errors=True)

    warnings.warn(
        "could not select a writable pytest basetemp; leaving pytest default in place",
        RuntimeWarning,
        stacklevel=2,
    )
    return None


def _can_use(path: Path) -> bool:
    probe = path / f".probe-{uuid.uuid4().hex}"
    try:
        probe.mkdir()
        (probe / "write-check.txt").write_text("ok", encoding="utf-8")
        list(path.iterdir())
    except OSError:
        return False
    finally:
        shutil.rmtree(probe, ignore_errors=True)
    return True


def _mkdtemp(parent: Path, prefix: str) -> Path | None:
    try:
        return Path(tempfile.mkdtemp(prefix=prefix, dir=parent))
    except OSError:
        return None
