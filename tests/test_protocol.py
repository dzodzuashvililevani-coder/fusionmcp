"""Enforce the Plan-Gate-Verify project workflow docs."""
from __future__ import annotations

import re
from pathlib import Path

from frame_tools.params import project_root

ROOT = project_root()
CODEX = ROOT / "docs" / "codex"
CLAUDE = ROOT / "docs" / "claude"
BRAINSTORMING = ROOT / "docs" / "brainstorming"
PROJECT = ROOT / "docs" / "project"
KNOWLEDGE = ROOT / "docs" / "knowledge"
PROTOCOL = ROOT / "docs" / "protocol"

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
    assert PROTOCOL.is_dir()
    assert CLAUDE.is_dir()
    assert CODEX.is_dir()
    assert BRAINSTORMING.is_dir()
    assert PROJECT.is_dir()
    assert KNOWLEDGE.is_dir()


def test_project_description_defines_fusion_control_center_scope():
    text = read(PROJECT / "description.md")
    sections = [
        "## 1. Project Identity",
        "## 2. Why This Exists",
        "## 3. Source Of Truth",
        "## 4. Primary Use Cases",
        "## 5. Current Scope",
        "## 6. Standalone Knowledge Capture Boundary",
        "## 7. Invariants And Free Variables",
        "## 8. Knowledge Capture Contract",
        "## 9. Where This Document Came From",
        "## 10. Roadmap",
        "## 11. Open Decisions",
    ]
    positions = [text.index(section) for section in sections]
    assert positions == sorted(positions)

    for phrase in [
        "FusionControlCenter",
        "Build Around Hardware In Hand",
        "Start From An Idea",
        "review-user-1.md",
    ]:
        assert phrase in text
    assert "| Mission truth |" in text
    assert "| Candidate knowledge |" in text
    assert "### Method invariants" in text
    assert "### Artifact invariants" in text
    assert "### Free variables" in text
    assert "### Change classification rule" in text
    assert "Touches an artifact invariant -> major" in text
    assert "Touches only free variables -> minor" in text
    assert "### The promotion event" in text


def test_knowledge_capture_staging_contract_exists():
    text = read(KNOWLEDGE / "capture-candidates.md")
    for phrase in [
        "standalone knowledge-capture project",
        "Verification States",
        "Candidate Template",
        "Dimension Provenance Template",
        "verified",
        "rejected",
    ]:
        assert phrase in text
    for state in ["unverified", "measured", "tested", "verified", "rejected"]:
        assert f"| `{state}` |" in text
    for source in ["caliper", "datasheet", "vendor-claim", "estimated", "ai-derived"]:
        assert source in text


def test_shared_protocol_defines_method_surface():
    text = read(PROTOCOL / "README.md")
    for phrase in [
        "Core Thesis",
        "Phase Types",
        "Gate Rule",
        "Deterministic Checks",
        "Feature Complete",
    ]:
        assert phrase in text
    assert "hard halt" in text
    assert "planner is not the implementer" in text
    assert r".\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp" in text
    assert r".\.venv\Scripts\python.exe -m frame_tools.cli report" in text


def test_contracts_define_handoff_types():
    text = read(PROTOCOL / "contracts.md")
    for phrase in ["## Plan", "## Phase", "## Gate Report", "## Error Fix", "## Sign-off"]:
        assert phrase in text
    assert "in-progress" in text
    assert "blocked" in text
    assert "complete" in text


def test_trust_boundaries_name_security_rules():
    text = read(PROTOCOL / "trust-boundaries.md")
    for phrase in ["File Boundaries", "Path Boundaries", "Subprocess Boundaries", "Learning Boundary"]:
        assert phrase in text
    assert "tests/test_privacy.py" in text


def test_claude_contract_names_forbidden_actions():
    text = read(CLAUDE / "behaviour.md")
    assert "## Forbidden" in text
    assert "write production code" in text
    assert "Verification Checklist" in text


def test_codex_contract_names_hard_gate():
    text = read(CODEX / "behaviour.md")
    assert "## Forbidden" in text
    assert "gate report" in text
    assert "stop for Claude verification" in text


def test_brainstorming_has_routing_template():
    text = read(BRAINSTORMING / "idea-template.md")
    assert "## Candidate acceptance checks" in text
    assert "docs/codex/" in text


def test_claude_verification_checklist_has_six_steps():
    text = read(CLAUDE / "verification-checklist.md")
    for step in range(1, 7):
        assert f"{step}." in text
    assert "PASS only if all six checks pass" in text


def test_plan_template_has_required_sections_in_order():
    text = read(CODEX / "plan-template.md")
    positions = [text.index(section) for section in PLAN_SECTIONS]
    assert positions == sorted(positions)
    assert "OFF-LIMITS" in text
    assert "gate report appended, then halt" in text


def test_errorfix_template_has_required_sections_in_order():
    text = read(CODEX / "errorfix-template.md")
    positions = [text.index(section) for section in ERROR_FIX_SECTIONS]
    assert positions == sorted(positions)
    assert "Do NOT" in text


def test_gate_report_template_has_five_required_sections():
    text = read(CODEX / "gate-report-template.md")
    for section in GATE_SECTIONS:
        assert section in text


def test_existing_plan_and_errorfix_names_follow_protocol():
    for path in CODEX.glob("claudePlan-*.md"):
        if "-errorFix-" in path.name:
            assert ERROR_FIX_NAME.match(path.name), path.name
        else:
            assert PLAN_NAME.match(path.name), path.name
