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
| `reviews____` | `review-<slug>.md` | Markdown | Claude's analysis of an idea: rating, gaps, open questions |
| `uimanifestoreview____` | [review-user-UI-manifesto.md](review-user-UI-manifesto.md) | Markdown | Review and brainstorming analysis of the user UI manifesto |
| `uimanifestoalign____` | [review-user-UI-manifesto-alignment.md](review-user-UI-manifesto-alignment.md) | Markdown | Claude alignment review of the UI manifesto against current project decisions |
| `decisions____` | `decision-<slug>.md` | Markdown | Short decision records when an idea changes direction |
| `uimanifesto____` | [user-UI-manifesto.md](user-UI-manifesto.md) | Markdown | User-written UI/workspace philosophy for future brainstorming |

## Flow

1. Start with `idea-<slug>.md` copied from `idea-template.md`.
2. Keep the idea rough until the goal and constraints are clear.
3. Ask Claude to turn the idea into `docs/codex/claudePlan-<slug>-1.md`.
4. Once implementation starts, durable state moves to `docs/codex/`.

Brainstorming files are allowed to be messy. They are not implementation
contracts. A Codex task starts only when a plan exists in `docs/codex/`.
