"""Enforce the Plan-Gate-Verify project workflow docs."""
from __future__ import annotations

import re
from pathlib import Path

from frame_tools.params import project_root

ROOT = project_root()
IMPLEMENTER = ROOT / "docs" / "implementer"
PLANNER = ROOT / "docs" / "planner"

PLAN_SECTIONS = [
    "## 1. Goal (<= 3 sentences)",
    "## 2. Out of scope",
    "## 3. Files in scope",
    "## 4. Acceptance criteria",
    "## 5. Phases",
    "## 6. Test commands (canonical)",
    "## 7. Sign-off log",
]

ERROR_FIX_SECTIONS = [
    "## 1. What's wrong (observed)",
    "## 2. Why it's wrong (root cause, best guess)",
    "## 3. What to change",
    "## 4. Acceptance for this fix",
    "## 5. Do NOT",
]

GATE_SECTIONS = [
    "## Commit SHA",
    "## Files changed",
    "## Test command output",
    "## Self-assessment",
    "## Open questions",
]

PLAN_NAME = re.compile(r"^claudePlan-[a-z0-9]+(?:-[a-z0-9]+)*-[1-9][0-9]*\.md$")
ERROR_FIX_NAME = re.compile(
    r"^claudePlan-[a-z0-9]+(?:-[a-z0-9]+)*-[1-9][0-9]*-errorFix-[1-9][0-9]*\.md$"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_protocol_folders_exist():
    assert PLANNER.is_dir()
    assert IMPLEMENTER.is_dir()


def test_planner_contract_names_forbidden_actions():
    text = read(PLANNER / "behaviour.md")
    assert "## Forbidden" in text
    assert "write production code" in text
    assert "Verification Checklist" in text


def test_plan_template_has_required_sections_in_order():
    text = read(IMPLEMENTER / "plan-template.md")
    positions = [text.index(section) for section in PLAN_SECTIONS]
    assert positions == sorted(positions)
    assert "OFF-LIMITS" in text
    assert "gate report appended, then halt" in text


def test_errorfix_template_has_required_sections_in_order():
    text = read(IMPLEMENTER / "errorfix-template.md")
    positions = [text.index(section) for section in ERROR_FIX_SECTIONS]
    assert positions == sorted(positions)
    assert "Do NOT" in text


def test_gate_report_template_has_five_required_sections():
    text = read(IMPLEMENTER / "gate-report-template.md")
    for section in GATE_SECTIONS:
        assert section in text


def test_existing_plan_and_errorfix_names_follow_protocol():
    for path in IMPLEMENTER.glob("claudePlan-*.md"):
        if "-errorFix-" in path.name:
            assert ERROR_FIX_NAME.match(path.name), path.name
        else:
            assert PLAN_NAME.match(path.name), path.name
