# docs/

**Purpose:** Human-written notes. Measurements going *in*, lessons coming *out*.

**Data stored here:** Markdown only. Screenshots and photos go to
[`photos/`](../photos/README.md) and are linked from here.

## Portals

| Portal | File | Type | Holds | Status |
|---|---|---|---|---|
| `measure____` | [measurements.md](measurements.md) | Markdown | Caliper checklist for every salvaged part | **Fill this in first** |
| `buildlog____` | [build-log.md](build-log.md) | Markdown | Dated log of what changed and what happened | Append as you go |

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
