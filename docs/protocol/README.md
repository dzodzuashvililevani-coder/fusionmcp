# docs/protocol/

**Purpose:** Shared Plan-Gate-Verify protocol definition for this project.

**Data stored here:** Markdown only. These documents define the method that
Claude, Codex, and the user follow when work is coordinated through files.

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `protocol____` | [README.md](README.md) | Markdown | Roles, flow, phase types, gates, and feature-complete rules |
| `contracts____` | [contracts.md](contracts.md) | Markdown | Typed handoff contracts used by plans, gates, and fixes |
| `trust____` | [trust-boundaries.md](trust-boundaries.md) | Markdown | Security rules for paths, subprocesses, local files, and generated state |

## Core Thesis

Separate the planner from the implementer: the planner is not the implementer.
Put a hard halt between them. Make every durable handoff a file, never a
conversation.

## Roles

| Role | Folder | Responsibility | Forbidden |
|---|---|---|---|
| User | [../brainstorming/](../brainstorming/README.md) | Writes rough ideas and decides priorities | Treating chat as durable project state |
| Claude | [../claude/](../claude/README.md) | Plans and verifies outcomes | Writing production code for work it will verify |
| Codex | [../codex/](../codex/README.md) | Implements scoped phases and reports gates | Inventing scope or signing off its own work |

## Flow

```
docs/brainstorming/idea-<slug>.md
        |
        v
docs/codex/claudePlan-<slug>-1.md
        |
        v
implement phase(s) -> gate report -> hard halt
        |                              |
        |                              v
        |                         Claude verify
        |                         PASS or errorFix
        v
complete only after final verify phase passes
```

## Phase Types

Every phase in a plan is one of three types:

| Type | Actor | Meaning |
|---|---|---|
| `implement` | Codex | Write or edit files listed in the plan scope |
| `gate` | Codex | Run commands, append the five-section gate report, then stop |
| `verify` | Claude | Inspect diff, rerun checks, sign off or write error-fix |

## Gate Rule

The gate is a hard halt. Codex must not start the next implementation phase
until Claude has appended a PASS sign-off to the plan or written an error-fix.

Gate reports must include:

1. Commit SHA.
2. Files changed.
3. Test command output.
4. Self-assessment.
5. Open questions.

## Deterministic Checks

Use real tools with exit codes wherever possible:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

No agent opinion replaces these commands. If a command fails, the gate fails.
These module entry points are canonical because Windows Application Control may
block unsigned `.exe` shims in `.venv\Scripts\`.

## Feature Complete

A feature is complete only when all of these are true:

1. Every phase in the plan has a PASS entry or a resolved error-fix trail.
2. All acceptance criteria were verified.
3. No open error-fix files remain for that feature.
4. The diff is committed cleanly.
5. The plan has a short user-facing summary of what changed.

Anything less stays `in-progress` or `blocked`.
