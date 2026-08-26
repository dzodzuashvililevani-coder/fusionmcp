# docs/claude/

**Purpose:** Claude-owned planning and verification documents.

**Data stored here:** Markdown only. These files define how Claude turns
brainstorming notes into implementation plans and how it verifies Codex work.

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `behaviour____` | [behaviour.md](behaviour.md) | Markdown | Claude role contract: planner and verifier responsibilities |
| `verify____` | [verification-checklist.md](verification-checklist.md) | Markdown | Six-step gate verification checklist |

## Boundary

Claude owns intent and verification. Codex owns implementation. The same agent
should not both implement a feature and sign off that the right thing was built.

Claude output that Codex must act on goes to `docs/codex/`, not this folder.
