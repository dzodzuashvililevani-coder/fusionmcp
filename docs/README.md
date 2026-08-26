# docs/

**Purpose:** Human-written notes. Measurements going *in*, lessons coming *out*.

**Data stored here:** Markdown only. Screenshots and photos go to
[`photos/`](../photos/README.md) and are linked from here.

## Portals

| Portal | File | Type | Holds | Status |
|---|---|---|---|---|
| `measure____` | [measurements.md](measurements.md) | Markdown | Caliper checklist for every salvaged part | **Fill this in first** |
| `buildlog____` | [build-log.md](build-log.md) | Markdown | Dated log of what changed and what happened | Append as you go |
| `planner____` | [planner/](planner/README.md) | Markdown | Planner role contract and verification rules | Read before planning |
| `inbox____` | [implementer/](implementer/README.md) | Markdown | Implementer inbox, plan templates, gate reports | Use for multi-agent work |

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
small fix. The planner writes a self-contained plan into
[`implementer/`](implementer/README.md), the implementer edits only the named
scope, and every gate stops until a verifier signs off in the plan file.
