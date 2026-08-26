# docs/

**Purpose:** Human-written notes. Measurements going *in*, lessons coming *out*.

**Data stored here:** Markdown only. Screenshots and photos go to
[`photos/`](../photos/README.md) and are linked from here.

## Portals

| Portal | File | Type | Holds | Status |
|---|---|---|---|---|
| `measure____` | [measurements.md](measurements.md) | Markdown | Caliper checklist for every salvaged part | **Fill this in first** |
| `buildlog____` | [build-log.md](build-log.md) | Markdown | Dated log of what changed and what happened | Append as you go |
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
the reason the second frame is better than the first lives in that file.

## Multi-agent work

This repo uses the Plan-Gate-Verify protocol for changes that span more than a
small fix. Brainstorm rough ideas in [`brainstorming/`](brainstorming/README.md),
use [`protocol/`](protocol/README.md) as the shared method, Claude writes a
self-contained plan into [`codex/`](codex/README.md), Codex edits only the named
scope, and every gate stops until Claude signs off in the plan file.
