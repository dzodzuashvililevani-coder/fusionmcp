# docs/codex/

**Purpose:** Codex-owned implementer inbox for Plan-Gate-Verify work.

**Data stored here:** Markdown only. Claude writes plans and error-fix specs
here because Codex must be able to continue without reading chat.

## Portals

| Portal | File pattern | Type | Holds |
|---|---|---|---|
| `behaviour____` | [behaviour.md](behaviour.md) | Markdown | Codex role contract and forbidden actions |
| `plantemplate____` | [plan-template.md](plan-template.md) | Markdown | Required sections for `claudePlan-<slug>-<N>.md` |
| `fixtemplate____` | [errorfix-template.md](errorfix-template.md) | Markdown | Required sections for `claudePlan-<slug>-<N>-errorFix-<M>.md` |
| `gatetemplate____` | [gate-report-template.md](gate-report-template.md) | Markdown | Five-section gate report body to append to a plan |
| `plans____` | `claudePlan-<slug>-<N>.md` | Markdown | Feature plans written by Claude for Codex |
| `fixes____` | `claudePlan-<slug>-<N>-errorFix-<M>.md` | Markdown | Claude-written fix specs after failed verification |

## Contract

- Codex implements only files listed in the plan's `## 3. Files in scope`.
- A gate is a hard halt. Codex appends a gate report and stops.
- Codex does not sign off its own work.
- Chat is routing and clarification only. Durable state lives in these files.
- If the task is blocked, Codex records the blocker instead of inventing scope.

## Naming

| File kind | Pattern | Example |
|---|---|---|
| User feature spec | `feat-<slug>.md` | `feat-fusion-export.md` |
| Plan | `claudePlan-<slug>-<N>.md` | `claudePlan-fusion-export-1.md` |
| Error fix | `claudePlan-<slug>-<N>-errorFix-<M>.md` | `claudePlan-fusion-export-1-errorFix-1.md` |

Small one-line fixes do not need a plan. Use this protocol when the change
needs phased work, durable handoff, or independent verification.
