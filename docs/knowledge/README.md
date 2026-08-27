# docs/knowledge/

**Purpose:** The handoff contract. Defines what this project exports when
something is finished, in what shape, and with what labels attached -- so a
separate knowledge-capture project can collect it later without guessing.

**Data stored here:** Markdown only. This folder holds the **contract**, not the
knowledge. The finished artifacts themselves live in their named folders
(`cad/`, `dxf/`, `photos/`, `docs/build-log.md`, `params.yaml`).

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `candidates____` | [capture-candidates.md](capture-candidates.md) | Markdown | The export contract: verification labels, provenance fields, and the record template |

## This is not a knowledge base

Knowledge capture is a **separate project** that does not exist yet. Decided
2026-08-28 -- see [`../brainstorming/decision-scope-split.md`](../brainstorming/decision-scope-split.md).

| This folder does | This folder does not |
|---|---|
| Define the shape of an exported record | Store a knowledge library |
| Define the labels a finished artifact carries | Decide whether an artifact is worth reusing |
| Say where finished products live | Extract, rank, deduplicate, or link them |
| Stay small and boring | Grow into a system |

If you find yourself building an extractor here, stop. That is the other
project.

## Flow

1. Work on the hardware. Measure, model, cut, build, fly.
2. When something is **finished** -- the build happened and the outcome is known
   -- record it in its named folder from `description.md` section 8.
3. Attach its labels: where each number came from, and whether a build confirmed
   it. Cheap now, impossible to reconstruct later.
4. That is all. The other project reads this repo when it exists.

Nothing here waits on the knowledge project, and nothing here breaks if it is
never built.
