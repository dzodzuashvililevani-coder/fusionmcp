# Idea: vision model as a measurement assistant

**Created:** 2026-08-28
**Status:** rough
**Author:** Claude (planner), from a brief by the user
**Related:** [idea-web-workstation.md](idea-web-workstation.md) (the UI this lives
inside), roadmap Phase 4 (photo evidence) and Phase 7 (3D viewer)

## Problem

The user's framing, in their words: *the user inputs measurements manually
inside the UI that shows, beside the input, what part of the hardware they are
holding should be measured; the user can even provide a photo of the part and
ask questions.*

Two problems sit behind that, and they are not the same size.

**Problem A — "which dimension does this label mean?"** Already documented in
`idea-web-workstation.md` and already the highest-risk step in the build. A
wrong-but-plausible number passes every check in `validate.py`, because the
validator tests relationships between numbers, not whether a number describes
the thing its name claims.

**Problem B — "what am I even holding?"** New, and specific to this project.
The parts are salvaged from a Temu toy drone. There is no datasheet, no model
number, and in several cases no way to tell a flight controller from a
receiver-plus-ESC board by looking at it. You cannot measure a component's mass
into the right row of `components/loadout.yaml` until you know which component
it is. **This blocks Phase 3, which is the next phase.**

Problem A is a *presentation* problem. Problem B is a *recognition* problem.
Only the second one needs vision.

## Desired outcome

Inside the measurement UI, the user can attach a photo of the part in hand and
have a conversation about it: what is this board, which of these two edges is
the "base diameter", does this number I just typed look right for this part.

## Four separable capabilities

They get lumped together as "add a vision model" and they have very different
value and very different risk. Rated separately on purpose.

### 1. Identify an unlabelled salvaged part — **9/10, do this**

Read the silkscreen text, connector count, and board outline from a photo; say
what the part probably is and what to search for. This is the highest-value use
in this project because it unblocks something nothing else can: the loadout file
has six components to weigh and the user may not be able to name three of them.

Cheap to build (one image, one prompt), fails safely (a wrong guess costs a
search), and needed *before* Phase 3 rather than after.

### 2. Answer "where do I measure?" from a photo — **4/10, mostly not vision**

Worth having as a fallback, but the primary answer to this question is a diagram
or a 3D model with the dimension highlighted — which is roadmap Phase 7, is
deterministic, is drawn from live parameter values, and does not need a model at
all. A vision model answering "measure across there" from a photo is a weaker
version of a picture the project can simply draw.

Build the diagram first. Vision here is the fallback for the parts the diagram
does not cover.

### 3. Sanity-check a number the user typed, against the photo — **7/10**

*"You entered 9.4mm for the bolt circle, but that board looks like an M2 pattern
on a 12mm base — worth re-checking."* Cheap, low-risk, and it catches the exact
error class the numeric validator structurally cannot: a plausible number
attached to the wrong dimension. It is advice, never a block, and never a write.

### 4. Read the measurement off the photo as the value — **2/10, do not build**

Estimating a physical dimension from an image is where this goes wrong. The
project's tolerances are millimetres: `validate.py` warns if the FC hole pattern
leaves under 4mm to the plate edge, and a 0.3mm error in the bolt circle means
the motor does not bolt on. Scale from a photo is unreliable at that resolution
even with a reference object in frame, and the failure is silent — a confident
wrong number that passes every check.

**One narrow exception that is not the same thing:** photographing a *digital
caliper's display* and reading the digits off it. There the caliper did the
measuring; the model is doing OCR on a seven-segment display. That is a
legitimate convenience and should be labelled as what it is.

## The provenance rule this must obey

This project already has the vocabulary, in
[`../knowledge/capture-candidates.md`](../knowledge/capture-candidates.md):

| Source | Meaning |
|---|---|
| `caliper` | Direct physical measurement |
| `datasheet` | Manufacturer or distributor datasheet |
| `vendor-claim` | Listing, product page, package text |
| `estimated` | Human estimate used as a temporary placeholder |
| `ai-derived` | AI-generated or AI-inferred value; **never promote without another source** |

That last row was written before this idea existed and it settles the design.
Anything a vision model produces enters as `source: ai-derived`,
`verification_state: unverified`, and cannot become `measured` without a caliper
reading confirming it. The UI should show that difference, not hide it.

**A vision model is a second opinion, not a source of truth.** The moment it
writes an authoritative number, the project has traded its provenance discipline
for convenience — which is the exact thing Phase 1 was built to prevent.

## Constraints

- **Photos leave the machine.** Every other part of this project runs locally.
  Sending a photo to a hosted model is the first outbound data flow in the
  repository and belongs in `docs/protocol/trust-boundaries.md` before it is
  built, not after.
- **EXIF first.** `test_privacy.py` already fails on private identifiers in
  tracked text; roadmap Phase 4 plans EXIF stripping and a test that fails on any
  tracked image carrying GPS. **Strip before upload, not just before commit** —
  otherwise the first photo sent carries the user's home coordinates.
- **It must not become a write path.** The vision layer proposes; the user
  confirms; the existing `fcc.writer` performs the write. No new writer.
- **No new authority.** `params.yaml` stays the single source of truth and
  geometry stays solved once in `geometry.py`.
- **Cost is per-photo and recurring**, unlike everything else here. For 21
  numbers measured once by one person it is hard to justify; across the second
  and third project (roadmap Phase 9) it pays for itself. That argues for
  building it as a `fcc` capability, not a frame-specific one.

## Where it belongs in the roadmap

| Capability | Suggested phase | Why |
|---|---|---|
| 1. Identify a salvaged part | **Before or during Phase 3** | It blocks Phase 3. A one-off conversation with a photo may be enough — this may not need code at all |
| 3. Sanity-check a typed value | Phase 4, with photo intake | Needs the photo pipeline that Phase 4 builds anyway |
| 2. Where-to-measure diagram | Phase 7, as already planned | Deterministic beats inferred |
| 4. Measure from a photo | Not planned | See above |

Note what capability 1 implies: **the most valuable use of vision here might need
no feature at all.** Photograph the mystery board, ask, write the answer down.
If that is all it takes, building a vision pipeline first would be tooling
getting ahead of need again — the exact failure mode the roadmap's governing
idea exists to prevent.

## Candidate acceptance checks

- A photo of an unidentified board produces a named guess plus what to search
  for; the guess is recorded with `source: ai-derived`.
- No value written by any vision path carries `verification_state: measured`.
- A photo with GPS EXIF is rejected or stripped **before** any upload; a test
  proves it.
- Turning the vision feature off leaves every measurement path working.
- The value written to disk is written by `fcc.writer`, unchanged.

## Open questions

1. Is capability 1 a feature, or one conversation with a phone camera? Answer
   this before writing a plan.
2. Does `fcc` — declared domain-blind — grow an outbound network call? That is a
   real architectural change and needs a decision record, not a plan.
3. What does the UI show for an `ai-derived` value so it never reads as measured?
4. Local model or hosted? Local removes the trust-boundary problem and most of
   the cost, at a large accuracy penalty for silkscreen text.

## Next routing step

Do not plan this yet. Answer open question 1 first — photograph one unidentified
board and see whether a conversation resolves it. If it does, capability 1 is a
habit rather than a feature, and only capability 3 is left worth planning, which
belongs with Phase 4's photo intake.
