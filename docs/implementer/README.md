# docs/implementer/

**Purpose:** Implementer inbox for Plan-Gate-Verify work.

**Data stored here:** Markdown only. Plans, error-fix specs, and gate report
templates live here so an implementer can continue without reading chat.

## Portals

| Portal | File pattern | Type | Holds |
|---|---|---|---|
| `plantemplate____` | [plan-template.md](plan-template.md) | Markdown | Required sections for `claudePlan-<slug>-<N>.md` |
| `fixtemplate____` | [errorfix-template.md](errorfix-template.md) | Markdown | Required sections for `claudePlan-<slug>-<N>-errorFix-<M>.md` |
| `gatetemplate____` | [gate-report-template.md](gate-report-template.md) | Markdown | Five-section gate report body to append to a plan |
| `plans____` | `claudePlan-<slug>-<N>.md` | Markdown | Feature plans written by the planner |
| `fixes____` | `claudePlan-<slug>-<N>-errorFix-<M>.md` | Markdown | Planner-written fix specs after failed verification |

## Contract

- Plans are append-only once implementation starts, except sign-off entries and
  explicit revision notes.
- A gate is a hard halt. The implementer stops after writing the gate report.
- Chat is routing and clarification only. Durable state lives in these files.
- Files outside a plan's `## 3. Files in scope` are off-limits unless a plan
  revision or error-fix expands the scope.
- Use ordinals, not dates, in plan file names.

## Naming

| File kind | Pattern | Example |
|---|---|---|
| User feature spec | `feat-<slug>.md` | `feat-fusion-export.md` |
| Plan | `claudePlan-<slug>-<N>.md` | `claudePlan-fusion-export-1.md` |
| Error fix | `claudePlan-<slug>-<N>-errorFix-<M>.md` | `claudePlan-fusion-export-1-errorFix-1.md` |

Small one-line fixes do not need a plan. Use this protocol when the change
needs phased work, durable handoff, or independent verification.
