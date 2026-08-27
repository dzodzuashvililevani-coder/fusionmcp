# Export Contract

**This file defines the shape of an exported record. It is not a knowledge
base and it is not a workflow.**

Knowledge capture left this project on 2026-08-28 -- see
[`../brainstorming/decision-scope-split.md`](../brainstorming/decision-scope-split.md).
The standalone knowledge-capture project reads this repository, follows each
source, and decides what is worth keeping. **This repository writes labels and
stops.**

What that means in practice:

| This repo does | The knowledge project does |
|---|---|
| Marks a thing finished when a build settles it | Decides whether it is reusable |
| Records where each number came from | Normalises, deduplicates, links |
| Uses the states and sources below as **labels** | Uses them as **inputs to a decision** |

Only **finished products** get recorded here -- things whose build has happened
and whose outcome is known. Works in progress stay in their working files.

## Verification States

Labels, not stages. Nothing in this repo moves a record between them except a
physical build.

| State | Meaning |
|---|---|
| `unverified` | Captured from a note, idea, assumption, or external source |
| `measured` | Directly measured from hardware, but not yet tested in a build |
| `tested` | Used in a command, model, cut, or assembly attempt |
| `verified` | Confirmed by real build or repeated successful use |
| `rejected` | Kept for history, but should not be reused |

## Candidate Template

One record per finished thing. `Reuse target` is a hint for the other project,
never a decision made here.

```markdown
### KC-YYYYMMDD-01 - Short Title

- Source:
- Category: component | dimension | Fusion workflow | build lesson | design rule | script pattern
- Candidate:
- Evidence:
- Verification state: unverified
- Reuse target:
- Notes:
```

## Dimension Provenance Template

Use one record-level verification state for broad lessons and Fusion workflow
notes. Use per-dimension provenance for components, because a component can mix
measured, sourced, estimated, and rejected facts in one physical part.

```yaml
dimensions:
  bolt_circle_mm:
    value: 9.0
    source: caliper
    verification_state: measured
    verified_by: null
    evidence: docs/measurements.md
  kv_rating:
    value: 12000
    source: vendor-claim
    verification_state: unverified
    verified_by: null
    evidence: null
```

Allowed sources:

| Source | Meaning |
|---|---|
| `caliper` | Direct physical measurement |
| `datasheet` | Manufacturer or distributor datasheet |
| `vendor-claim` | Listing, product page, package text, or other sales material |
| `estimated` | Human estimate used as a temporary placeholder |
| `ai-derived` | AI-generated or AI-inferred value; never promote without another source |

## Active Candidates

No candidates yet -- nothing has been built. The first entries arrive after the
first physical frame is cut and flown.
