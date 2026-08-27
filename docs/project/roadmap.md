# FusionControlCenter Development Roadmap

**Status:** active -- this is the build order
**Created:** 2026-08-28
**Authority:** `docs/project/description.md` (mission), `docs/project/architecture.md` (stack)
**Supersedes:** the short roadmap in `description.md` section 10, which now points here

---

## 0. The governing idea

There is a tension in "build the tool, then use it": every week spent building
FusionControlCenter is a week the drone frame is not built, and the frame is the
only thing that proves FCC works.

The resolution is not a compromise -- it is a sequence where each unblocks the
other, in a specific order:

> **FCC's first user is the drone frame. The frame's first tool is FCC.**

Concretely: the frame is blocked on 20 unmeasured numbers. FCC's first real
feature is the thing that captures measurements safely. So the first slice of
FCC gets built, then immediately used to unblock the frame, then the frame gets
built, and *then* the harder FCC features get designed -- by someone who has now
actually measured a motor and cut a sheet of plywood.

That ordering has a second benefit. The 3D measurement viewer (Phase 7) is the
most expensive feature in the project and the hardest to specify. Building it
**after** a real measurement session means it is designed against remembered
frustration rather than imagined need.

Three rules hold the sequence together:

1. **Nothing is built before the thing it depends on is proven.** Each phase's
   exit criteria are observable from outside the code.
2. **The frame is never more than one phase away from progress.** No stretch of
   the plan is pure tooling.
3. **Every phase leaves the repo working.** Both canonical commands pass at
   every phase boundary, or the phase is not done.

---

## 1. Phases at a glance

| # | Phase | Delivers | Frame progress | Size |
|---|---|---|---|---|
| **0** | Ground zero | Green repo, committed, no contradictions | -- | ~done |
| **1** | Data spine | Field spec + surgical writer + CLI | Can fill TODOs from the terminal | 1 plan |
| **2** | Local workstation | FastAPI + React form + live validation | Can fill TODOs in a browser | 1-2 plans |
| **3** | **Dogfood: measure reality** | 20 real numbers replacing 20 guesses | **Design becomes real** | a session with calipers |
| **4** | Photo evidence | HEIC ingest, EXIF strip, note per photo | Measurements have proof | 1 plan |
| **5** | Fusion round trip | Kerf calibration, model, nest, DXF export | Cut files exist | 1 plan + Fusion work |
| **6** | **The frame exists** | Cut, assembled, flown, logged | **Done** | the actual build |
| **7** | 3D measurement viewer | Parametric models + dimension animation | Next build is easier | 1-2 plans |
| **8** | Generalisation | `fcc/` proven domain-blind | Ready for project two | 1 plan |
| **9** | Operate | Second project; UC2 groundwork | -- | ongoing |

**"The project is finished" means Phase 8.** Phase 9 is using it, which is the
point of having built it.

---

## 2. The phases

### Phase 0 -- Ground zero

**Goal.** A repository where development can actually start: no failing checks,
no uncommitted work, no documents contradicting each other.

**State on 2026-08-28.** Substantially complete.

| Item | Status |
|---|---|
| Both canonical commands run clean | **Done** -- 116 passed / 0 errors, 10 checks / 0 failures |
| Temp-directory blocker diagnosed | **Done** -- see `decision-scope-split.md`; canonical command uses explicit `.pytest-work-tmp` |
| Knowledge capture split out, all docs updated | **Done** |
| Duplicate manifesto review removed | **Done** |
| Retroactive baseline plan exists | **Done** -- `claudePlan-project-baseline-1.md`, awaiting sign-off |
| Architecture proposed | **Done** -- awaiting Codex review |
| Everything committed | **Outstanding** |

**Exit criteria.**

1. `git status --short` is empty. Nothing important lives only in the working
   tree.
2. Both canonical commands pass.
3. `claudePlan-project-baseline-1.md` has a PASS sign-off.
4. The six open questions in `architecture.md` section 11 are answered.

**Do this first, today.** It is minutes of work guarding weeks of it.

---

### Phase 1 -- The data spine

**Goal.** Turn "edit YAML by hand and hope" into a safe, programmatic,
byte-exact operation that anything can call.

**Why first.** Every later phase writes measurements. If the writer is wrong,
everything built on it inherits the fault -- and the specific fault available
here is silent destruction of `params.yaml`'s comments, which are load-bearing
provenance. This phase is small, has no UI, adds no dependencies, and is
verifiable by property tests rather than by looking at it.

**Deliverables.**

- `fields.yaml` -- the single declarative spec: one row per measurable number,
  carrying its question, unit, target file, key path, `measurements.md` label,
  plausible range, and a `shape_hint` reserved for Phase 7.
- `src/fcc/fields.py` -- loads and validates the spec.
- `src/fcc/writer.py` -- surgical writer for `params.yaml`,
  `components/loadout.yaml`, `docs/measurements.md`.
- CLI: `frame fields` (what still needs measuring) and `frame set <id> <value>`.

**Exit criteria.**

1. Every key currently marked `TODO` has a spec row; a test fails if a new
   `TODO` appears without one.
2. Writing a value changes exactly one line, and that line keeps its key and its
   trailing comment byte-for-byte.
3. The writer refuses anything it cannot edit surgically. It never reformats.
4. `frame set motor_bolt_circle 9.4` updates `params.yaml` **and** ticks the
   matching box in `docs/measurements.md`.
5. A value that fails validation is still written; the failure is reported.

**Independently useful.** With Phase 1 alone you can fill in every measurement
from the terminal. If Phase 2 slipped indefinitely, the frame would still be
unblocked. That is deliberate.

**Plan:** `docs/codex/claudePlan-data-spine-1.md`.

---

### Phase 2 -- The local workstation

**Goal.** The same operation through a browser, with the recomputed design
visible beside the input.

**Why here.** The terminal works but does not *show* you the consequence. The
value of the UI is that changing prop diameter and watching arm radius and TWR
move turns checking into designing.

**Deliverables.**

- `src/fcc/api/` -- FastAPI app, Pydantic models, endpoints for fields, report,
  and value writes.
- Generated `web/src/api.d.ts` from OpenAPI, with a drift test.
- `web/` -- Vite + React + TypeScript. Two panes: form built entirely from
  `/api/fields`, live report panel showing solver output and every check.
- `frame ui` -- starts the server, serves the built assets, opens a browser.

**Exit criteria.**

1. Entering a value in the browser changes the file on disk and updates the
   report in one round trip.
2. A value that fails validation still saves, and the failing check's text
   appears verbatim from `validate.py`.
3. No field name, unit, or range literal appears anywhere in the TypeScript.
4. The server binds `127.0.0.1` only; path traversal is refused; a test proves
   both.
5. Regenerating types from the running server produces no diff.

---

### Phase 3 -- Dogfood: measure reality

**Goal.** Replace 20 guesses with 20 measurements.

**This is the pivot of the whole roadmap.** Everything before it is
speculative tooling; everything after it rests on real numbers. It is also the
first genuine test of Phases 1 and 2 -- if the form is confusing or the writer
mangles a file, this is where it surfaces, on data that matters.

**Deliverables.**

- All 12 `TODO` keys in `params.yaml` filled from physical measurement.
- All 6 `TODO` masses in `components/loadout.yaml` weighed.
- All 33 blanks in `docs/measurements.md` filled.
- Motor thrust measured on a kitchen scale -- the one number with no datasheet
  and no substitute.

**Exit criteria.**

1. `grep -c TODO params.yaml` returns 0. Same for `components/loadout.yaml`.
2. `frame report` passes **on real numbers**. If it now fails, that is a true
   finding about the design, not a bug -- fix the design.
3. `docs/build-log.md` has its first real entry: what surprised you.

**Expect the design to change here.** The current arm radius of 91.87mm is
derived from guessed prop and plate dimensions. Real numbers will move it.

---

### Phase 4 -- Photo evidence

**Goal.** The measurements have visual proof attached, safely.

**Deliverables.** HEIC to JPG conversion, **all** EXIF stripped, downscale to
~1500px, rename to the `photos/own/` convention, one note per photo, and
`test_privacy.py` extended to fail on any tracked image carrying EXIF GPS.

**Exit criteria.**

1. An uploaded `.HEIC` lands as a downscaled `.jpg` with no EXIF.
2. No tracked image carries GPS coordinates; a test enforces it.
3. Each photo has a note saying what it evidences.

**Why after Phase 3.** You will have taken the photos during the measurement
session. This phase files them properly rather than guessing what you will
photograph.

---

### Phase 5 -- Fusion round trip

**Goal.** Real numbers become real cut files.

**Deliverables.**

- Kerf coupon cut and measured; `stock.kerf_mm` set from reality.
- The Fusion model built from `frame_params.json` via `sync_params.py`.
- `hole_pattern`, `nest_parts`, `mass_check`, `export_dxf` run in order.
- `dxf/` holds cuttable profiles.

**Exit criteria.**

1. Fusion's computed mass agrees with `frame mass` within a stated tolerance.
   Disagreement means one of them is wrong -- find out which before cutting.
2. `nest_parts` confirms every part fits the 250x250mm sheet.
3. `export_dxf` refuses to run if validation fails, and does not have to.

**Do not skip the kerf coupon.** Every hole is wrong by a consistent amount
without it, which is the worst kind of wrong because it looks fine.

---

### Phase 6 -- The frame exists

**Goal.** Cut it. Build it. Fly it. Write down what happened.

**This is what the repository is for.** Everything before it is preparation and
everything after it is improvement.

**Exit criteria.**

1. The frame is cut and assembled.
2. It flies, or it does not and `docs/build-log.md` says precisely why.
3. Finished artifacts are in their named folders per `description.md` section 8,
   with provenance recorded.
4. The export contract has been exercised once, on real output. Whatever was
   awkward about it is written down -- that is the feedback the future knowledge
   project needs and cannot get any other way.

**The most valuable output of this phase is the surprises.** The plywood that
was 2.7mm and not 3mm. The CG that sat aft because the strap was heavier than
assumed. Those go in the build log the day they happen, not later.

---

### Phase 7 -- 3D measurement viewer

**Goal.** Make the next measurement session unambiguous.

**Why this late.** It is the most expensive feature and the hardest to specify
from imagination. Built now, it is designed by someone who has measured a
salvaged motor and knows exactly which labels were ambiguous.

**Deliverables.** react-three-fiber component models drawn **from live parameter
values**, dimension callouts animated on field focus, driven by the `shape_hint`
field reserved in Phase 1.

**Exit criteria.**

1. Focusing a field highlights and animates the dimension it asks for.
2. The models render from current parameters -- entering a 9mm bolt circle on a
   12mm base visibly draws holes hanging off the edge.
3. No parameter is duplicated in TypeScript to make the model work.

**Criterion 2 is the point.** The model becomes a second validator that catches
the one error class no numeric check can: measuring the wrong dimension.

---

### Phase 8 -- Generalisation

**Goal.** Prove `src/fcc/` is actually domain-blind, rather than merely
declared so.

**Deliverables.** A second parameter set -- any simple part -- driving the same
UI with no code change. A test asserting no module under `frame_tools` imports
`fcc`. Documentation of what a new project must provide.

**Exit criteria.**

1. A second `params.yaml` + `fields.yaml` pair works in the same UI.
2. The import-direction test passes.
3. Extracting `fcc/` into its own repository would be a move, not a rewrite.

**This is where "the project is finished."**

---

### Phase 9 -- Operate

**Goal.** Use it.

Start the second hardware project with FCC as the tool. Begin UC2 groundwork --
designing from a mission rather than from parts in hand -- now that there is a
provenance discipline to keep sourced data from contaminating measured data.

If the knowledge-capture project is ever built, this is when it has two real
projects to read, which is the minimum for designing it against evidence rather
than imagination.

---

## 3. Milestones that matter

Four moments where the project changes character:

| Milestone | Phase | Why it matters |
|---|---|---|
| First measurement written by tool, not by hand | 1 | The spine works |
| `grep -c TODO params.yaml` returns 0 | 3 | The design stops being fiction |
| **The frame flies** | 6 | The thesis is proven or corrected |
| A second project runs on the same tooling | 8 | FCC is a platform, not a script |

---

## 4. What would change this plan

Stated in advance so a mid-course change is a decision rather than a drift:

- **Phase 3 reveals the design is unbuildable.** Real numbers may push arm radius
  or plate size outside what a 250x250 sheet allows. Then Phase 3 gains a design
  iteration, and the artifact invariants in `description.md` section 7 decide
  what may bend.
- **Phase 2 turns out to be unnecessary.** If filling every measurement through
  the Phase 1 CLI is comfortable, the browser UI is worth less than assumed.
  Phase 3 answers this honestly, and Phase 2 can shrink.
- **The frame is cut before Phase 5 completes.** Acceptable. Cutting by hand from
  printed DXF is a legitimate shortcut; the Fusion round trip is about
  repeatability, not permission.
- **Fusion Electronics enters scope.** A second discipline of comparable size to
  the mechanical one. It would become its own phase, not an addition to one.

---

## 5. Standing rules for every phase

1. Both canonical commands pass at every phase boundary.
2. `params.yaml` as committed passes `frame check`.
3. Geometry is solved exactly once, in `geometry.py`.
4. Every phase that adds a folder adds its `README.md` portal table in the same
   change.
5. Finished artifacts go to their named folders with provenance attached.
6. Multi-step work goes through Plan-Gate-Verify. The gate is a hard halt.
7. **This project makes things. It does not remember them.** No extractor, no
   component library, no promotion machinery.
