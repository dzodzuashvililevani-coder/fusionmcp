# FusionControlCenter Project Description

**Status:** finalized baseline
**Updated:** 2026-08-27
**First case study:** parametric wooden drone frame for Fusion 360

## 1. Project Identity

FusionControlCenter is a local-first hardware development control center for
Fusion 360 work assisted by Codex, Claude, and repeatable scripts.

The current repository remains the first concrete case study: a parametric
wooden FPV drone frame built around real measured parts. The broader
FusionControlCenter idea grows from this project only after the drone workflow
has produced real measurements, CAD artifacts, build results, and reusable
lessons.

## 2. Why This Exists

This project exists to make Fusion 360 hardware development easier, more
repeatable, and easier to learn from.

Fusion 360 is the modeling environment, but the work around it is larger than
modeling. The project must help with measurement capture, parameter management,
part planning, Fusion script handoff, build logging, design review, and later
knowledge reuse. The long-term value is not only the drone frame. The value is
the system that remembers what was measured, what was tried, what failed, what
worked, and what can be reused in a future hardware project.

## 3. Source Of Truth

Project truth is layered. The right-hand column maps each layer onto the
Interpretable Context Methodology (arXiv:2603.16021), whose vocabulary this
project adopts -- see `docs/brainstorming/review-icm-paper.md`.

| Layer | Source | Role | ICM |
|---|---|---|---|
| Mission truth | `docs/project/description.md` | Explains why the project exists and what must stay true | L0 |
| Routing truth | `CLAUDE.md`, folder `README.md` portal tables | Which folder answers which question | L1 |
| Method truth | `docs/protocol/`, plans in `docs/codex/` | How a unit of work is contracted and gated | L2 |
| Measurement truth | `docs/measurements.md` | Raw human measurements before they become parameters | L4 |
| Design truth | `params.yaml` and `components/loadout.yaml` | Machine-readable dimensions, masses, and positions | L4 |
| Execution truth | `fusion_scripts/`, `frame` commands, and generated handoff JSON | Repeatable actions used by Fusion 360 | L2/L3 |
| Result truth | `docs/build-log.md`, photos, CAD exports, DXF exports | What actually happened during build and test | L4 |
| Candidate knowledge | `docs/knowledge/capture-candidates.md` | Facts that may become reusable knowledge later | L4 awaiting L3 |
| Reference knowledge | (future) component cards, verified lessons | Stable facts every later build reads as constraints | L3 |
| Raw thinking | `docs/brainstorming/` | Ideas, reviews, and decisions before they become durable contracts | -- |

The distinction that matters most is **Layer 3 against Layer 4**. Layer 4 is
this build: it changes every run and is processed as input. Layer 3 is what
survives the build: it is stable across runs and is absorbed as a constraint.
Everything this project calls knowledge capture is the movement of an artifact
from Layer 4 to Layer 3, and section 8 defines when that movement is allowed.

Raw brainstorming is not implementation truth. A major idea becomes active only
after it is promoted into this project description, a protocol document, a
planned Codex task, or a structured data file.

## 4. Primary Use Cases

### Use Case 1: Build Around Hardware In Hand

The user already has real hardware, such as a motor, flight controller, camera,
battery, receiver, frame material, or fasteners.

The system should guide the user through measurements, record the original
values, convert accepted values into project parameters, validate the design,
send clean data into Fusion 360, and preserve lessons after the part is modeled,
cut, assembled, and tested.

The target experience is a guided workflow where the user can see what to
measure, enter the value, understand whether it is plausible, and then use the
accepted data to drive 2D planning and 3D modeling.

### Use Case 2: Start From An Idea

The user does not yet have all hardware in hand, but has a mission and design
intent, such as a fixed-wing drone with long flight time.

The system should help collect requirements, compare candidate components,
track datasheets and sources, reason about electronics and mechanics, and then
turn selected components into the same structured measurement and design flow
used by Use Case 1.

This use case is important, but it depends on stronger provenance rules.
Internet sourced component data must be treated as unverified until the project
can track source, confidence, and verification state.

## 5. Current Scope

The current scope is not to build the full FusionControlCenter platform at
once. The current scope is to finish a capture-ready drone-frame workflow.

In scope now:

- Keep the parametric drone frame reproducible from `params.yaml`.
- Preserve raw measurements and build results in Markdown.
- Keep Fusion work repeatable through scripts and generated handoff data.
- Use Plan-Gate-Verify for multi-agent work.
- Capture reusable lessons as candidates before promoting them into permanent
  knowledge.
- Prepare folder and file contracts that a future standalone knowledge-capture
  project can read.

Out of scope for now:

- A general-purpose knowledge extractor.
- A full independent FusionControlCenter application.
- Automatic CAD generation from unverified internet research.
- A permanent reusable component library before real build data exists.

## 6. Standalone Knowledge Capture Boundary

The standalone knowledge-capture project should be separate.

This repository should not try to solve extraction, ranking, summarization, or
cross-project memory yet. Its responsibility is to store capturable evidence in
predictable places so a future tool can extract it without guessing.

The boundary is:

- This repo captures source material, decisions, measurements, tests, build
  results, and reusable candidates.
- The future standalone project extracts, normalizes, deduplicates, links, and
  promotes knowledge across projects.
- This repo should not depend on the future extractor to remain useful.
- The future extractor should be able to read this repo without private local
  paths, account data, or hidden machine-specific state.

## 7. Invariants And Free Variables

Invariants come in two kinds, and the difference is operational rather than
philosophical: they answer different questions and are consumed by different
readers.

### Method invariants -- how the project works

Rules that should not change without explicit review:

- The physical mission of the active hardware project comes before platform
  ambition.
- Raw measurements are preserved even after conversion into YAML.
- Machine-readable parameters must be reproducible and testable.
- Generated outputs are not hand-edited.
- Real build evidence is stronger than guesses, assumptions, or web data.
- A fact is not reusable knowledge until its source and verification state are
  known.
- Fusion MCP exploration should be converted into repeatable scripts when it
  proves useful.

### Artifact invariants -- what the current build must stay true to

These describe the thing being built, not the process building it. Each carries
its reason, because the reason is what makes it an invariant rather than a
preference. **These are specific to the active project and are rewritten when a
new hardware project starts.**

For the wooden drone frame:

| Invariant | Why |
|---|---|
| Cut from a single 250x250mm sheet | That is the stock actually owned |
| Flies on the salvaged Temu motors | It is a salvage project; buying new motors makes it a different project |
| Cuttable on a laser in one pass | No CNC access |
| Carries the flight controller stack and battery already on hand | Those parts are fixed inputs, not choices |

### Free variables -- optimise freely

Project-level:

- UI shape and technology.
- Exact folder names for future extracted knowledge libraries.
- Whether the final platform remains in this repository or becomes a separate
  repository.
- Component categories supported by future guided measurement screens.
- How much of the workflow is automated after the first physical build.

Frame-level:

- Arm width, taper profile, and lightening holes.
- Centre plate size, within the flight controller stack footprint.
- Battery position along the y axis.
- Camera tilt angle.

### Change classification rule

Artifact invariants and free variables exist to make one specific decision
mechanical rather than a matter of AI judgment.

When a change to the active hardware project is proposed:

- **Touches an artifact invariant -> major.** Halt. The change contradicts a
  reason the project exists. It escalates to deliberation, and the outcome is
  written as a decision record in `docs/brainstorming/` -- including the
  alternatives rejected and why, since the rejected option is the reusable part.
- **Touches only free variables -> minor.** Proceed. Validate with
  `frame check`, and log anything surprising.
- **Touches something on neither list -> the lists are incomplete.** Stop and
  extend them before deciding. A change that cannot be classified is the signal
  that this section is out of date, not a licence to guess.

Without this rule the invariant lists are a philosophy statement. With it they
are a lookup table, which is the only form an agent can apply consistently.

## 8. Knowledge Capture Contract

During development, capturable information should be written where it belongs:

| Capturable data | Primary location |
|---|---|
| Raw dimensions | `docs/measurements.md` |
| Accepted numeric design state | `params.yaml`, `components/loadout.yaml` |
| Material assumptions | `components/materials.yaml` |
| Planning and gate history | `docs/codex/` |
| Design debates and direction changes | `docs/brainstorming/` |
| Build outcomes and physical surprises | `docs/build-log.md` |
| Candidate reusable facts | `docs/knowledge/capture-candidates.md` |
| Photos and visual evidence | `photos/` |
| Fusion models and neutral CAD exports | `cad/` |
| Cutter-ready profiles | `dxf/` |
| Repeatable Fusion operations | `fusion_scripts/` |

Knowledge candidates should identify their source, evidence, verification
state, and reuse target. A future extractor should be able to promote a
candidate into a reusable component card or lesson only after the candidate has
enough evidence.

### The promotion event

"Enough evidence" is not a judgment call. In ICM terms, promotion moves an
artifact from Layer 4 (this build) to Layer 3 (every later build's reference),
and **a completed physical build is the event that authorises it.**

The trigger runs in both directions:

| What happened | Effect on the candidate |
|---|---|
| The part was measured, and the build confirmed it -- the screw fit, the frame flew | `measured` -> `verified`, stamped with the build that proved it |
| The part was measured, and the build contradicted it -- the hole was wrong, the arm cracked | -> `rejected`, kept with the reason it failed |
| The build never exercised it | State unchanged. A build that did not test something proves nothing about it |

Nothing reaches `verified` on inspection, agreement, or repetition alone. Only
physical evidence sets that state, and only for what the build actually tested.

### Provenance is per number, not per record

A component record carries many dimensions and they rarely share a source. On a
salvaged motor the bolt circle may be caliper-measured, the KV rating a vendor
claim, the maximum thrust read off a kitchen scale, the stator size stamped on
the bell. One verification state for the whole record would misdescribe most of
them.

So each stored dimension carries its own `source`
(`caliper` | `datasheet` | `vendor-claim` | `estimated` | `ai-derived`),
its own verification state, and the build that verified it. This is what keeps
Use Case 2's internet-sourced numbers from becoming indistinguishable from Use
Case 1's measured ones once both are sitting in the same file.

The candidate ledger in `docs/knowledge/capture-candidates.md` is currently one
state per record, which is sufficient for lessons and Fusion techniques and
insufficient for components. Reconciling it is queued as
`claudePlan-knowledge-schema-1.md`.

## 9. Where This Document Came From

This baseline is a synthesis, not an original. Its reasoning lives upstream in
`docs/brainstorming/`, and that is where to go when a decision here needs its
justification rather than its conclusion:

| Source | Contributed |
|---|---|
| `idea-user-1.md` | The user's manifesto. Why the project exists, and both use cases |
| `review-user-1.md` | Sequencing (build before capture), provenance, the invariant/free-variable split |
| `review-icm-paper.md` | The Layer 3 / Layer 4 vocabulary and the promotion event of section 8 |
| `idea-web-workstation.md` | The guided measurement workstation, and why its data spine comes before its 3D layer |
| `review-project-final.md` | Verification of this baseline, and the changes applied to it |

Two conclusions carried forward from those documents are load-bearing enough to
restate here.

**Sequencing.** The project must not build a standalone knowledge-capture
platform before it has real hardware development data to capture. The drone
frame produces the first evidence. Designing a knowledge system around imagined
data guarantees it will be shaped for the wrong data.

**Provenance.** A saved motor model, measurement, shortcut, Fusion trick, or
design rule is only valuable if the project knows where it came from, whether it
was measured or assumed, whether a build verified it, and where it was reused.

The refinement on both: this repo should still prepare for the standalone
knowledge-capture project now, through stable document locations, clear file
purposes, and lightweight candidate records. That is not the same as building
the extractor yet.

## 10. Roadmap

0. **Keep canonical checks runnable.** On this workstation `.pytest-run-tmp`
   became unreadable and Windows Application Control blocked the generated
   `frame.exe` shim. The canonical commands therefore use
   `python.exe -m pytest -p no:cacheprovider` with `.pytest-work-tmp` and
   `python.exe -m frame_tools.cli report`. No gate may substitute a nearby
   command silently.
1. Finalize this project description and use it as the source-of-truth baseline.
2. Keep the drone frame workflow working and tested.
3. Fill in real measurements and update parameters. 13 `TODO` values remain in
   `params.yaml` and 6 in `components/loadout.yaml`; every design number is a
   guess until they are zero.
4. Extend deliberation records only where project direction changes.
5. Build the local guided measurement workstation. Planned in
   `docs/codex/claudePlan-web-workstation-1.md`, blocked on step 0. Its first
   phase is the data spine -- field spec and comment-preserving writer -- and
   the 3D viewer is deliberately a later plan.
6. Cut, assemble, test, and log the first physical frame. **This is the step
   that produces everything the knowledge system exists to capture.**
7. Convert verified repeated lessons into component cards or reusable records,
   using the promotion event defined in section 8.
8. Extract the standalone knowledge-capture project after at least one real
   hardware workflow has produced usable evidence -- and preferably on the
   second project, when two instances exist to define the shared interface.

## 11. Open Decisions

Answered by the reviews, recorded here so they are not reopened by default:

- **Repository split.** Keep this repo as the instance and extract
  FusionControlCenter on the second project. Layer-2 tooling is written
  domain-blind from the start so extraction is a move, not a rewrite.
- **Verification states.** `unverified` / `measured` / `tested` / `verified` /
  `rejected`, as defined in `docs/knowledge/capture-candidates.md`, with
  promotion authorised only by a completed physical build.
- **MCP versus scripts.** The rule already in `fusion_scripts/README.md` holds:
  explore with MCP, then lock proven steps into a committed script. Extend the
  third-party server only for what scripts genuinely cannot do.

Still open:

- What exact schema should reusable component cards use? Queued as
  `claudePlan-knowledge-schema-1.md`.
- When should the project name change from the drone-frame case study to the
  broader FusionControlCenter identity? Proposed trigger: at extraction, on the
  second project -- not before.
- Which parts of Omnissiah's software knowledge workflow should be copied
  directly, and which need hardware-specific changes? **Blocked:** this needs
  Omnissiah's actual layout. If it already implements ICM concretely, FCC should
  mirror its skeleton rather than invent a parallel one.
- Do ICM's numbered stages apply to the *process* only, leaving artifact folders
  intact -- or is the whole repository restructured ICM-style? Argued for the
  first in `docs/brainstorming/review-icm-paper.md` section 6.3; awaiting a
  decision.
- Is Fusion Electronics in scope? It is a second discipline of comparable size
  to the mechanical one, and the MCP server already exposes an electronics
  surface.
