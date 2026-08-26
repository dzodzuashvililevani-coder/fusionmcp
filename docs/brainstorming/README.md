# docs/brainstorming/

**Purpose:** Early feature thinking before a Plan-Gate-Verify plan exists.

**Data stored here:** Markdown only. Use this folder for rough ideas, tradeoff
notes, sketches in words, and user-written feature briefs that are not ready
for Codex implementation yet.

## Portals

| Portal | File pattern | Type | Holds |
|---|---|---|---|
| `ideatemplate____` | [idea-template.md](idea-template.md) | Markdown | Structured prompt for a rough feature idea |
| `ideas____` | `idea-<slug>.md` | Markdown | Brainstorming notes before Claude turns them into a plan |
| `decisions____` | `decision-<slug>.md` | Markdown | Short decision records when an idea changes direction |

## Flow

1. Start with `idea-<slug>.md` copied from `idea-template.md`.
2. Keep the idea rough until the goal and constraints are clear.
3. Ask Claude to turn the idea into `docs/codex/claudePlan-<slug>-1.md`.
4. Once implementation starts, durable state moves to `docs/codex/`.

Brainstorming files are allowed to be messy. They are not implementation
contracts. A Codex task starts only when a plan exists in `docs/codex/`.
