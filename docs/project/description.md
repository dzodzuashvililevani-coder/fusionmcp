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

This project exists to make Fusion 360 hardware development easier and more
repeatable.

Fusion 360 is the modeling environment, but the work around it is larger than
modeling. The project must help with measurement capture, parameter management,
part planning, Fusion script handoff, build logging, and design review.

**FusionControlCenter is a creation tool. It is not a knowledge system.**
Knowledge capture -- extraction, promotion, deduplication, cross-project memory
-- belongs to a separate project that does not exist yet. See section 6, and
`docs/brainstorming/decision-scope-split.md` for why.

What this project owes that future one is narrow: **finished products land in
named folders, in a documented shape, with their provenance written alongside
them.** Recording where a number came from is cheap at the moment it is produced
and impossible to reconstruct later. Deciding what to do with that record is
someone else's job.

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
| Candidate knowledge | `docs/knowledge/capture-candidates.md` | The handoff contract: what gets exported, in what shape, with what labels | L4, marked for export |
| Raw thinking | `docs/brainstorming/` | Ideas, reviews, and decisions before they become durable contracts | -- |

**This project produces Layer 4 and stops there.** Layer 4 is this build: it
changes every run and is processed as input. Layer 3 -- stable reference absorbed
as constraints by later projects -- is produced by the separate knowledge project
from what this one exports. The Layer 4 to Layer 3 movement is real and still
matters; it just happens downstream, on the other side of the handoff described
in section 6.

What this repository does at that boundary is mark a thing finished and record
its provenance. It does not decide what the thing is worth.

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
- Deposit finished products into the named folders of section 8, with their
  provenance recorded alongside them.

Out of scope, permanently:

- A knowledge extractor, of any kind.
- Promotion, ranking, deduplication, or linking of captured facts.
- A reusable component library intended for cross-project use.
- Cross-project memory or any schema for it.

Out of scope for now:

- A full independent FusionControlCenter application.
- Automatic CAD generation from unverified internet research.

## 6. Standalone Knowledge Capture Boundary

Knowledge capture is a **separate project** that does not exist yet. This is a
hard boundary, not a sequencing preference.

| This repository | The knowledge project |
|---|---|
| Makes things | Remembers things |
| Produces finished artifacts and marks them finished | Extracts, normalises, deduplicates, links, promotes |
| Records where each number came from | Decides what that provenance is worth |
| Exports in stable, boring formats | Owns the schema it imports into |
| Useful on its own, forever | Reads many projects, not just this one |

Three rules hold the boundary:

1. **This repo never depends on the knowledge project to be useful.** If the
   other project is never built, nothing here breaks.
2. **This repo never implements any part of it.** Not a prototype, not a
   placeholder, not "just the schema".
3. **The knowledge project reads this repo without special access** -- no private
   local paths, no account data, no machine-specific state. Already enforced by
   `tests/test_privacy.py`.

The reason for the split is in `docs/brainstorming/decision-scope-split.md`. The
short version: creation is bursty and project-shaped, knowledge is continuous and
cross-project, and a knowledge system designed against a single wooden drone
frame would be designed against one data point.

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

This is a **handoff contract**, not a workflow. It says where finished things
live so the knowledge project can collect them. It does not say what should be
done with them.

### The named folders

Every kind of output has exactly one destination. Nothing important is allowed
to live only in a working directory, a scratch file, or a conversation.

| Output | Named folder | Format |
|---|---|---|
| Raw dimensions as measured | `docs/measurements.md` | Markdown |
| Accepted numeric design state | `params.yaml`, `components/loadout.yaml` | YAML |
| Material assumptions | `components/materials.yaml` | YAML |
| Planning and gate history | `docs/codex/` | Markdown |
| Design debates and direction changes | `docs/brainstorming/` | Markdown |
| Build outcomes and physical surprises | `docs/build-log.md` | Markdown |
| Photos and visual evidence | `photos/own/`, `photos/reference/` | JPG, PNG |
| Fusion models and neutral CAD exports | `cad/` | `.f3d`, `.step` |
| Cutter-ready profiles | `dxf/` | `.dxf` |
| Repeatable Fusion operations | `fusion_scripts/` | Python |
| The handoff contract itself | `docs/knowledge/capture-candidates.md` | Markdown |

These names are stable. Renaming one is a breaking change to the handoff and
requires a decision record.

### The promotion event

There is one event this project recognises, and it is deliberately simple:
**a completed physical build marks its artifacts finished.**

Finished means: the part was cut or the model was exported, the build happened,
and the outcome is known. That is the moment an artifact stops being working
material and becomes something worth exporting.

| What happened | What this repo records |
|---|---|
| The build confirmed it -- the screw fit, the frame flew | `verified`, stamped with the build that proved it |
| The build contradicted it -- the hole was wrong, the arm cracked | `rejected`, kept with the reason it failed |
| The build never exercised it | Unchanged. A build that did not test something proves nothing about it |

`verified` is never set by inspection, agreement, or repetition. Only physical
evidence sets it, and only for what the build actually tested.

**This repo writes that label and stops.** Whether a `verified` artifact is worth
reusing, how it relates to artifacts from other projects, and whether it becomes
a reusable component card are all questions for the knowledge project.

### Provenance is per number, not per record

A finished component carries many dimensions and they rarely share a source. On
a salvaged motor the bolt circle may be caliper-measured, the KV rating a vendor
claim, the maximum thrust read off a kitchen scale, the stator size stamped on
the bell. One label for the whole record would misdescribe most of them.

So each exported dimension carries its own `source`
(`caliper` | `datasheet` | `vendor-claim` | `estimated` | `ai-derived`), its own
state, and the build that verified it. This is what keeps Use Case 2's
internet-sourced numbers from becoming indistinguishable from Use Case 1's
measured ones -- a distinction that is free to record at the moment of
measurement and unrecoverable afterwards.

Recording it is in scope. Acting on it is not.

## 9. Where This Document Came From

This baseline is a synthesis, not an original. Its reasoning lives upstream in
`docs/brainstorming/`, and that is where to go when a decision here needs its
justification rather than its conclusion:

| Source | Contributed |
|---|---|
| `idea-user-1.md` | The user's manifesto. Why the project exists, and both use cases |
| `review-user-1.md` | Sequencing (build before capture), provenance, the invariant/free-variable split |
| `review-icm-paper.md` | The Layer 3 / Layer 4 vocabulary |
| `idea-web-workstation.md` | The guided measurement workstation, and why its data spine comes before its 3D layer |
| `review-project-final.md` | Verification of this baseline, and the changes applied to it |
| `decision-scope-split.md` | **The 2026-08-28 decision that knowledge capture leaves this project entirely** |

**Read `decision-scope-split.md` before the three reviews.** Those reviews were
written while knowledge capture was still this project's responsibility, and
they argue at length for mechanisms that now live elsewhere. They carry
superseding banners, but the decision record is the authority.

Two conclusions from those documents survive the split intact, because they are
about this project rather than the knowledge one.

**Sequencing.** The frame gets measured, cut, built, and flown. That is still the
work, and it is still what produces everything the other project will eventually
consume. Nothing about the split makes the physical build less urgent -- it makes
it more so, because it is now the only thing this repo is for.

**Provenance.** A measurement, model, or design rule is only worth exporting if
the project records where it came from, whether it was measured or assumed, and
whether a build confirmed it. That record is cheap at the moment of measurement
and impossible to reconstruct later.

What is gone is any obligation to *act on* that provenance beyond writing it
down.

## 10. Roadmap

**The authority is [`roadmap.md`](roadmap.md)**, which breaks the work into
nine phases with observable exit criteria. The summary below is the shape of it.

0. **Keep canonical checks runnable.** On this workstation `.pytest-run-tmp`
   became unreadable and Windows Application Control blocked the generated
   `frame.exe` shim. The canonical commands therefore use
   `python.exe -m pytest -p no:cacheprovider --basetemp=.pytest-work-tmp` and
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
6. Cut, assemble, test, and log the first physical frame. **This is the step the
   whole repository exists for.**
7. Deposit the finished artifacts into the named folders of section 8, with
   provenance recorded. This is bookkeeping, not a system.
8. **Stop.** The knowledge-capture project is separate work in a separate
   repository, started when and if you choose. Nothing here waits on it.

## 11. Open Decisions

Answered by the reviews, recorded here so they are not reopened by default:

- **Repository split.** Keep this repo as the instance and extract
  FusionControlCenter on the second project. Layer-2 tooling is written
  domain-blind from the start so extraction is a move, not a rewrite.
- **Knowledge capture is a separate project.** Decided 2026-08-28. This repo
  deposits finished products in named folders and does nothing further. See
  `docs/brainstorming/decision-scope-split.md`.
- **Verification states.** `unverified` / `measured` / `tested` / `verified` /
  `rejected`, as defined in `docs/knowledge/capture-candidates.md`. These are
  **labels this repo records**, set only by physical evidence. They are not a
  workflow this repo runs.
- **MCP versus scripts.** The rule already in `fusion_scripts/README.md` holds:
  explore with MCP, then lock proven steps into a committed script. Extend the
  third-party server only for what scripts genuinely cannot do.

Closed by the 2026-08-28 split, recorded so they are not reopened:

- ~~What schema should reusable component cards use?~~ **Not this project's
  question.** `claudePlan-knowledge-schema-1.md` is cancelled.
- ~~Which parts of Omnissiah's knowledge workflow should be copied?~~ **Moved**
  to the future knowledge project, where the comparison is meaningful.

Still open:

- When should the project name change from the drone-frame case study to the
  broader FusionControlCenter identity? Proposed trigger: on the second hardware
  project -- not before.
- Do ICM's numbered stages apply to the *process* only, leaving artifact folders
  intact -- or is the whole repository restructured ICM-style? Argued for the
  first in `docs/brainstorming/review-icm-paper.md` section 6.3; awaiting a
  decision. **Narrowed by the split:** with knowledge capture gone, the only
  pipelines left are the two use cases, so the case for restructuring the whole
  repo is weaker than it was.
- Is Fusion Electronics in scope? It is a second discipline of comparable size
  to the mechanical one, and the MCP server already exposes an electronics
  surface.
