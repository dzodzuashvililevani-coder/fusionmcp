# Knowledge Capture Candidates

This file is a staging ledger for information that may become reusable hardware
knowledge later. It is intentionally lighter than a real knowledge base.

The future standalone knowledge-capture project should be able to read this
file, follow each source, and decide whether a candidate is ready to promote.

## Verification States

| State | Meaning |
|---|---|
| `unverified` | Captured from a note, idea, assumption, or external source |
| `measured` | Directly measured from hardware, but not yet tested in a build |
| `tested` | Used in a command, model, cut, or assembly attempt |
| `verified` | Confirmed by real build or repeated successful use |
| `rejected` | Kept for history, but should not be reused |

## Candidate Template

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

No candidates yet.
