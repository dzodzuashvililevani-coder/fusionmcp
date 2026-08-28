"""Source-level guardrails for the browser workstation."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

from frame_tools.params import project_root

ROOT = project_root()
WEB = ROOT / "web"
WEB_SRC = WEB / "src"
TEXT_SOURCE_SUFFIXES = {".ts", ".tsx", ".css"}
TOKEN_NAMES = {
    "--ground",
    "--shell",
    "--panel",
    "--sunken",
    "--ink",
    "--muted",
    "--faint",
    "--rule",
    "--rule-firm",
    "--accent",
    "--accent-ink",
    "--accent-soft",
    "--ok",
    "--ok-soft",
    "--warn",
    "--warn-soft",
    "--fail",
    "--fail-soft",
}


def web_source_files() -> list[Path]:
    return sorted(
        path
        for path in WEB_SRC.rglob("*")
        if path.is_file() and path.suffix in TEXT_SOURCE_SUFFIXES
    )


def field_literals() -> list[str]:
    spec = yaml.safe_load((ROOT / "fields.yaml").read_text(encoding="utf-8"))
    literals: set[str] = set()
    for field in spec["fields"]:
        for key in ("id", "question", "measurement_label"):
            value = field.get(key)
            if value is not None:
                literals.add(str(value))
        for key in ("unit", "min", "max"):
            value = field.get(key)
            if value is not None:
                literals.add(str(value))
    return sorted(literals, key=lambda value: (len(value), value))


def test_web_source_contains_no_field_spec_literals():
    offenders = []
    for path in web_source_files():
        text = path.read_text(encoding="utf-8")
        for literal in field_literals():
            if literal_in_source(literal, text):
                offenders.append(f"{path.relative_to(ROOT).as_posix()}: {literal!r}")

    assert not offenders


def test_web_source_and_shell_have_no_external_urls():
    offenders = []
    paths = web_source_files() + [WEB / "index.html"]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        if "http://" in text or "https://" in text:
            offenders.append(path.relative_to(ROOT).as_posix())

    assert not offenders


def test_styles_define_complete_light_and_dark_token_sets():
    css = (WEB_SRC / "styles.css").read_text(encoding="utf-8")
    root_blocks = re.findall(r":root(?:\[data-theme=\"dark\"\])?(?:[^{]*)\{(?P<body>[^}]*)\}", css)
    assert len(root_blocks) >= 3
    for block in root_blocks[:3]:
        defined = set(re.findall(r"(--[a-z0-9-]+)\s*:", block))
        assert TOKEN_NAMES <= defined
    assert '@media (prefers-color-scheme: dark)' in css
    assert ':root:not([data-theme="light"])' in css
    assert ':root[data-theme="dark"]' in css


def test_api_types_are_current_when_node_dependencies_are_available():
    npm = shutil.which("npm.cmd") or shutil.which("npm")
    if not npm:
        pytest.skip("npm is not installed; cannot regenerate web API types")
    if not (WEB / "node_modules" / ".bin" / "openapi-typescript.cmd").exists() and not (
        WEB / "node_modules" / ".bin" / "openapi-typescript"
    ).exists():
        pytest.skip("web dependencies are not installed; run npm.cmd --prefix web install")

    before = (WEB_SRC / "api.d.ts").read_bytes()
    result = subprocess.run(
        [npm, "--prefix", str(WEB), "run", "gen:types"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert (WEB_SRC / "api.d.ts").read_bytes() == before
    first_lines = (WEB_SRC / "api.d.ts").read_text(encoding="utf-8").splitlines()[:3]
    assert first_lines == [
        "/**",
        " * Generated, do not edit. Regenerate with npm.cmd --prefix web run gen:types",
        " */",
    ]


def literal_in_source(literal: str, text: str) -> bool:
    if len(literal) <= 3 or re.fullmatch(r"\d+(?:\.\d+)?", literal):
        quoted = re.escape(literal)
        return re.search(rf'["\'`]{quoted}["\'`]', text) is not None
    return literal in text
