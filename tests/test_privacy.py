"""Keep local credentials and personal machine details out of committed files."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

from frame_tools.params import project_root

ROOT = project_root()
THIS_FILE = Path(__file__).resolve()
TEXT_EXTENSIONS = {
    ".json", ".md", ".ps1", ".py", ".toml", ".yaml", ".yml",
    ".code-workspace", ".gitignore",
}

SECRET_PATTERNS = [
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"(?i)(api|access|auth|bearer|private|secret|token)[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_./+=-]{16,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"(?i)\bpassword\s*[:=]\s*['\"][^'\"]+['\"]"),
]

# Split these strings so this test does not contain the exact identifiers it blocks.
LOCAL_IDENTIFIERS = [
    "C:" + "\\Users" + "\\",
    "C:" + "/Users" + "/",
    "iliame" + "eqvse",
    "iliadzodzuashvili" + "787",
    "ucha" + ".dzodzuashvili",
]

EMAIL = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
ALLOWED_EMAILS = {"noreply@github.com"}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [ROOT / line.strip() for line in result.stdout.splitlines() if line.strip()]


def read_if_text(path: Path) -> str | None:
    if path.resolve() == THIS_FILE:
        return None
    if path.suffix.lower() not in TEXT_EXTENSIONS and path.name not in TEXT_EXTENSIONS:
        return None
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None


def test_no_secrets_or_private_identifiers_in_tracked_text_files():
    findings: list[str] = []

    for path in tracked_files():
        text = read_if_text(path)
        if text is None:
            continue

        rel = path.relative_to(ROOT).as_posix()
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                findings.append(f"{rel}: matches sensitive pattern {pattern.pattern!r}")

        for identifier in LOCAL_IDENTIFIERS:
            if identifier.lower() in text.lower():
                findings.append(f"{rel}: contains local/private identifier {identifier!r}")

        for match in EMAIL.finditer(text):
            email = match.group(0).lower()
            if email not in ALLOWED_EMAILS:
                findings.append(f"{rel}: contains email address {email!r}")

    assert not findings, "\n".join(findings)
