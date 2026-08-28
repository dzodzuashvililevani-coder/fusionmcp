# docs/

**Purpose:** Human-written notes. Measurements going *in*, lessons coming *out*.

**Data stored here:** Markdown only. Screenshots and photos go to
[`photos/`](../photos/README.md) and are linked from here.

## Portals

| Portal | File | Type | Holds | Status |
|---|---|---|---|---|
| `measure____` | [measurements.md](measurements.md) | Markdown | Caliper checklist for every salvaged part | **Fill this in first** |
| `project____` | [project/](project/README.md) | Markdown | Project identity, mission, scope, source-of-truth hierarchy | Read before major changes |
| `reports____` | [reports/](reports/README.md) | Markdown | Plain-language report per finished roadmap phase | Read to understand the project |
| `buildlog____` | [build-log.md](build-log.md) | Markdown | Dated log of what changed and what happened | Append as you go |
| `knowledge____` | [knowledge/](knowledge/README.md) | Markdown | Export contract for a separate knowledge project | Read before exporting |
| `brainstorm____` | [brainstorming/](brainstorming/README.md) | Markdown | Rough feature ideas before a plan exists | Start feature thinking here |
| `protocol____` | [protocol/](protocol/README.md) | Markdown | Shared Plan-Gate-Verify rules, contracts, trust boundaries | Read before multi-agent work |
| `claude____` | [claude/](claude/README.md) | Markdown | Claude planner/verifier role docs | Read before planning |
| `codex____` | [codex/](codex/README.md) | Markdown | Codex inbox, plan templates, gate reports | Use for implementation |

## The flow

```
measure the part  ->  docs/measurements.md  ->  params.yaml
                                                    |
                                              frame report
                                                    |
                                     cut / assemble / fly
                                                    |
                                          docs/build-log.md
```

`measurements.md` is the raw record -- keep it even after the numbers are
copied into `params.yaml`, so you can tell a mis-measurement from a mis-typing.

`build-log.md` is where the value compounds. Log the surprises especially:
the reason the second frame is better than the first lives in that file. When a
build **finishes** something, record it in its named folder with its source and
verification state -- the export contract is in
[`knowledge/capture-candidates.md`](knowledge/capture-candidates.md).

Knowledge capture itself is a **separate project** (decided 2026-08-28,
[`brainstorming/decision-scope-split.md`](brainstorming/decision-scope-split.md)).
This repo deposits finished products in named folders and does nothing further
with them.

## Multi-agent work

This repo uses the Plan-Gate-Verify protocol for changes that span more than a
small fix. Read [`project/description.md`](project/description.md) for mission
and source-of-truth boundaries, brainstorm rough ideas in
[`brainstorming/`](brainstorming/README.md), use
[`protocol/`](protocol/README.md) as the shared method, Claude writes a
self-contained plan into [`codex/`](codex/README.md), Codex edits only the named
scope, and every gate stops until Claude signs off in the plan file.
