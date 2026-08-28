# Phase 1 report — The data spine

**Roadmap phase:** 1 of 9 ([roadmap.md](../project/roadmap.md) section 2)
**Plan:** [claudePlan-data-spine-1.md](../codex/claudePlan-data-spine-1.md)
**Period:** 2026-08-28
**Status:** complete, all 25 acceptance criteria verified
**Commits:** `0b07cd7`, `54611a1`, `146313d`, `40032ca`, plus uncommitted Phase 7 work

---

## 1. The problem this phase solved

This project designs a wooden drone frame. Every dimension of that frame is
calculated from numbers in `params.yaml` — how thick the plywood is, how wide
the propellers are, how far apart the motor screw holes sit. Change one number
and the arm length, the mass budget, and the safety checks all recompute.

The catch: **most of those numbers were guesses.** They were placeholders typed
in from memory and product listings, each marked with a `# TODO` comment saying
"measure this for real." There were 18 such markers covering 21 separate
numbers. Until they were replaced with caliper measurements, every calculation
downstream was fiction.

So the obvious next step was "go measure the parts and type the numbers in."
The reason that was not the next step is worth understanding, because it is the
whole justification for this phase.

### Why typing them in by hand was the wrong move

Open `params.yaml` and look at one line:

```yaml
  thickness_mm: 3.0          # TODO measure with caliper
```

That comment is not decoration. It is the only record of where the number came
from and whether anyone has checked it. The file is full of these — 39 `#`
characters in 67 lines. Some explain units, some explain why a value is
conservative, some flag that a number is a guess.

Now consider the normal programmatic way to change a value in a YAML file:

```python
data = yaml.safe_load(open("params.yaml"))
data["stock"]["thickness_mm"] = 2.7
yaml.safe_dump(data, open("params.yaml", "w"))
```

Three lines, and it works. It also **silently deletes every comment in the
file**, reorders the keys alphabetically, rewrites the indentation, and turns
inline lists like `[65, 32, 18]` into three-line blocks. The YAML library parses
into a Python dictionary; a dictionary has no concept of a comment, so the
comments cease to exist. You get a valid file that loads correctly and has lost
all its provenance.

That is a one-way loss. Once the "this is a guess" markers are gone you cannot
tell a measured 2.7 from a guessed 2.7, and the whole point of the exercise was
to know the difference.

So Phase 1's job was to build the thing that changes one number in a data file
**and leaves literally everything else untouched, byte for byte** — and then to
put a terminal command on top of it, so the measurement session could start.

---

## 2. What you can do now that you could not before

Two new commands exist. Here they are actually running.

### `frame fields` — what still needs measuring

```
$ python -m frame_tools.cli fields
--------------------------------------------------------------
MEASUREMENT FIELDS
--------------------------------------------------------------
  stock_thickness            3 mm           [TODO guess]
         Measure actual wood stock thickness with calipers.
  prop_diameter              76 mm          [TODO guess]
         Measure propeller diameter from tip to opposite tip.
  motor_bolt_circle          9 mm           [TODO guess]
         Measure motor bolt circle hole to hole, across the base.
  ...21 fields total
```

Each row gives the identifier you will type, the value currently in the file,
whether it is still a guess, and a plain-English instruction for how to measure
it. That last part matters more than it looks: "bolt circle" is ambiguous — is
it the distance across the motor base, or between two adjacent holes? The
question text says "hole to hole, across the base" so you cannot get it wrong at
the calipers.

### `frame set <id> <value>` — record one measurement

```
$ python -m frame_tools.cli set motor_bolt_circle 9.4
--------------------------------------------------------------
FIELD WRITE
--------------------------------------------------------------
  field               motor_bolt_circle
  value               9.4 mm
  changed             params.yaml:23
    -   bolt_circle_mm: 9.0        # TODO measure hole-to-hole across the motor base
    +   bolt_circle_mm: 9.4        # TODO measure hole-to-hole across the motor base
  checklist           ticked

--------------------------------------------------------------
PRE-CUT CHECKS
--------------------------------------------------------------
  [ ok ] prop clearance
         arm radius 91.87mm vs 60.81mm minimum (tip gap 53.92mm)
  ...10 checks
--------------------------------------------------------------
  10 passed, 0 warnings, 0 failures
```

One command did four things:

1. Changed exactly one line in `params.yaml`, keeping the key, the spacing, and
   the trailing comment identical.
2. Went to `docs/measurements.md` — the paper-style checklist you carry to the
   bench — found the matching line, filled in the blank, and ticked the box:

   ```
   before:  - [ ] Bolt circle (hole to hole, across the base): ____ mm
   after:   - [x] Bolt circle (hole to hole, across the base): 9.4 mm
   ```

3. Re-ran the full design validation with the new number.
4. Printed the result so you immediately see whether your measurement broke the
   design.

Before this phase, that was: open the YAML in an editor, find the right line,
type carefully, open the markdown checklist, find the matching line, type again,
tick the box manually, switch to the terminal, run the report. Seven steps,
two files kept in sync by hand, and no protection against a typo landing in the
wrong key.

---

## 3. What was built, piece by piece

Five new source files, one new data file, three new test files. Here is what
each is for and why it exists separately from the others.

### `fields.yaml` — the list of things to measure (275 lines, 21 entries)

A plain data file describing every measurable number. One entry looks like this:

```yaml
  - id: motor_bolt_circle
    question: Measure motor bolt circle hole to hole, across the base.
    unit: mm
    file: params.yaml
    key_path: motors.bolt_circle_mm
    index: null
    item: null
    field: null
    measurement_label: Bolt circle (hole to hole, across the base)
    min: 4.0
    max: 40.0
    type: float
    shape_hint: motor_bolt_circle
```

Read it as: *"There is a number called `motor_bolt_circle`. To get it, ask the
human this question. It is measured in millimetres. It lives in `params.yaml`
under `motors` → `bolt_circle_mm`. The checklist line it corresponds to is
titled 'Bolt circle (hole to hole, across the base)'. Anything below 4mm or
above 40mm is probably a mistake. It is a decimal number."*

**Why a separate data file rather than code?** Because everything downstream can
now be generated from it instead of written by hand. The `frame fields` command
does not contain a list of fields — it reads this file. When the browser UI
arrives in Phase 2, its form will be built from this file too, so a new
measurement means adding twelve lines of YAML and nothing else. No Python
changes, no TypeScript changes, no chance of the form and the file disagreeing.

The `shape_hint` key is deliberately unused today. Phase 7 plans a 3D viewer
that highlights the dimension you are being asked for; that field is reserved
for it now so the spec does not need reshaping later.

### `src/fcc/fields.py` — reads and checks that list (220 lines)

Loading a data file is easy. This module's real job is refusing to load a
**broken** one. Before returning anything it verifies:

- No two entries share an `id`.
- Every `key_path` actually resolves against the real `params.yaml`. A typo like
  `motors.bolt_circle` instead of `motors.bolt_circle_mm` is caught here, at
  load time, rather than at 11pm at the workbench.
- Every `file` is one of the three files this system is allowed to touch.
- `min` is not greater than `max`.
- Every `measurement_label` matches **exactly one** line in the checklist —
  not zero, and importantly not two.

That last rule has a story attached, in section 7.

### `src/fcc/errors.py` — named failure types (25 lines)

Five small exception classes: `SpecError`, `UnsurgicalEdit`, `LabelNotFound`,
`AmbiguousLabel`, `PathRefused`. Nothing clever, but the naming is the feature.
When something goes wrong the error says *which kind* of wrong — "I cannot edit
that line surgically" is a completely different problem from "I cannot find that
checklist label", and both are different from "that path points outside the
project."

### `src/fcc/writer.py` — the surgical writer (344 lines)

The load-bearing piece, and the reason the phase took four rounds of review.

It does not parse YAML at all. It treats the file as **a list of text lines**,
finds the one line that holds the value you named, replaces just the number
inside that line, and writes the file back. Everything it does not understand,
it leaves alone — which is why comments, spacing, and key order survive: the
writer never had them in a form it could lose.

Three shapes are supported:

| Shape | Example line | How the value is addressed |
|---|---|---|
| Plain value | `thickness_mm: 3.0    # TODO` | by key |
| Inline list | `size_mm: [65, 32, 18]  # TODO L x W x H` | by key + position (0, 1, 2) |
| Inline map | `- { name: vtx, mass_g: 4.0, pos_mm: [0, -25, 14] }` | by item name + field name |

Anything else — a nested block, a multi-line list, a key it cannot locate — it
**refuses**, by raising `UnsurgicalEdit` naming the path it could not handle.
This is the design decision worth internalising:

> A tool that refuses loudly is safer than a tool that guesses and reformats.

There is a test that greps the source code to prove `yaml.dump` is never called
anywhere in the file, so no future edit can quietly add a "just rewrite the
whole file" fallback.

**Writing safely.** Every write follows the same sequence:

1. Write the new content to a temporary file **in the same folder** as the
   target.
2. Re-read that temporary file and parse it as YAML to confirm it is still valid.
3. Only then replace the original with it, using an operation the operating
   system performs as a single step.

If the machine loses power at any point, you have either the complete old file
or the complete new one — never a half-written one. And if step 2 finds the
result would be broken YAML, the temporary file is deleted and the original is
never touched. The temporary file is in the same folder deliberately: replacing
a file is only guaranteed to be a single atomic step when both files are on the
same disk volume.

**The checklist edit happens in a specific order.** When you set a value that
has a checklist line, the writer works out the checklist change *first*, in
memory, and only then writes the data file. If your label is missing or
ambiguous it fails at that point, before anything on disk has changed. The
alternative — write the YAML, then discover the checklist label is wrong —
would leave the two files disagreeing, which is exactly the state this system
exists to prevent.

### `src/frame_tools/cli.py` — the two new commands (+132 lines)

The terminal interface described in section 2. Three details worth calling out:

**A failing measurement is still saved.** If you measure the plywood and it is
0.5mm — thin enough that the design's safety check fails — the value is written
anyway, and then the failure is reported:

```
  [warn] stock_thickness is outside the expected 1..8 mm range. Value saved anyway.
  [FAIL] stock thickness
         0.5mm - thin plywood arms flex and cause gyro noise; 3mm+ recommended
  9 passed, 0 warnings, 1 failures
  >> This design does not currently validate. The measurement was saved; fix the design next.
```

The command still exits successfully. This is intentional and it is the most
opinionated choice in the phase: **a measurement is a fact about the world, and
the design being wrong is a separate problem.** If the tool refused to save
numbers it disliked, the user would learn to type numbers the tool accepts
rather than numbers the calipers show. Then the validation is measuring the
user's patience instead of the design.

The range check still fires — it just warns instead of blocking. Out of range
means *implausible*, not *impossible*.

**Unknown identifiers fail loudly and helpfully.**

```
$ python -m frame_tools.cli set not_a_field 2
error: unknown field id 'not_a_field'; valid ids: stock_thickness, prop_diameter, ...
exit code 2
```

**The check-printing code was extracted, not duplicated.** `frame check` and
`frame set` print the identical validation summary because they call the same
function. There is no second copy to drift.

### `conftest.py` — a test-environment fix (63 lines)

Not a feature, but it consumed a genuine share of the effort so it belongs in an
honest report. Two different automated environments worked on this repository
and they had **opposite** restrictions on where temporary test files could be
created. The same test command produced 133 passing tests in one and a crash
before tests even started in the other.

The fix probes the available temporary locations at startup, picks one that
actually works in the environment it finds itself in, and warns rather than
crashing if none do. The important property is that the documented test command
carries no environment-specific flag — it is the same command everywhere, and
the code adapts.

### Three test files (675 lines, 40 tests)

| File | Tests | Covers |
|---|---|---|
| `tests/test_fields.py` | 14 | The spec loads, and broken specs are rejected |
| `tests/test_writer.py` | 14 | Byte-exact writes, comments survive, atomic replacement |
| `tests/test_boundaries.py` | 12 | Path safety, import rules, and the two CLI commands |

The CLI tests are worth a note on technique: rather than calling Python
functions directly, they **copy the whole project into a temporary folder and
launch the real command as a separate process**, then check its actual exit code
and its actual printed output. That is slower, and it is the only way to test
what a user experiences. A test that calls `cmd_set(args)` directly proves the
function works; it does not prove the command works.

---

## 4. Follow one command through the code

If you read one thing to understand how this project is wired, read this. It
traces `frame set motor_bolt_circle 9.4` from your keypress to the changed byte
on disk, naming every file it passes through.

```
you type:  python -m frame_tools.cli set motor_bolt_circle 9.4
```

**1. `src/frame_tools/cli.py` — `main()`**
Argument parsing. Recognises `set`, collects `id` and `value` as strings, and
calls `cmd_set`. This file is the only place in `frame_tools/` allowed to talk
to the general-purpose `fcc` half of the codebase.

**2. `src/frame_tools/params.py` — `project_root()`**
Answers "where is the project?" by walking up from its own location until it
finds `params.yaml`. Everything else takes the answer as an argument, which is
why the tests can point the whole system at a temporary copy.

**3. `src/fcc/fields.py` — `field_by_id("motor_bolt_circle")`**
Reads `fields.yaml`, validates every entry in it, and hands back one record: the
question, the unit, the target file, the key path, the checklist label, and the
plausible range. If the spec is broken — duplicate id, a key path that does not
exist, a label matching two checklist lines — it fails here, before anything is
written.

**4. Back in `cli.py` — `_coerce_value` and `_range_warning`**
Turns the string `"9.4"` into the number `9.4` using the type from the spec.
Compares it against `min`/`max` and prepares a warning if it is outside — a
warning, never a refusal.

**5. `src/fcc/writer.py` — `write_value(field, 9.4)` — the core**

- `_read_target` opens `params.yaml` with no line-ending translation and
  returns the raw text.
- `_replace_params_value` splits it into lines, walks down tracking which
  top-level section it is inside, and stops at the line under `motors:` whose
  key is `bolt_circle_mm`.
- `_replace_yaml_line_value` cuts that single line into four parts — the key
  and colon, the spacing, the value, the trailing comment — swaps only the
  value, and glues it back together.
- Because the field has a checklist label, `_replace_measurement` prepares the
  `docs/measurements.md` change **in memory first**, so a bad label fails
  before any file is touched.
- `_atomic_write` writes to a temporary file beside the original, re-parses it
  to confirm it is still valid YAML, then swaps it in as a single operation.
- Returns a `WriteResult`: which file, which line number, the old line text,
  the new line text, and whether the checklist was ticked.

**6. Back in `cli.py` — `cmd_set` prints the write**, then rebuilds the whole
design from the changed file and re-runs validation:

**7. `src/frame_tools/params.py` → `geometry.py` → `mass.py` → `thrust.py` →
`validate.py`**
`params.py` loads the files fresh. `geometry.py` solves arm length and motor
positions. `mass.py` totals the components and finds the centre of gravity.
`thrust.py` computes thrust-to-weight and hover throttle. `validate.py` runs ten
checks against all of it and returns a list of pass/warn/fail records.

**8. `cli.py` — `_print_checks`** renders that list with the `[ ok ]` /
`[warn]` / `[FAIL]` icons. The same function serves `frame check`, `frame
report`, and `frame set`, so all three look identical.

The shape worth remembering: **`fcc` knows how to edit files but nothing about
drones. `frame_tools` knows everything about drones but nothing about editing
files. `cli.py` is the only place they meet.**

---

## 5. Where everything lives — the whole project map

Every folder in this repository has its own `README.md` with a table of what is
inside. A test fails the build if one is missing, so the map cannot silently rot.
This section is that map gathered into one place.

### Top-level data files — the source of truth

| File | What it is | When you touch it |
|---|---|---|
| `params.yaml` | **The single source of truth.** Every design number: stock size, prop diameter, motor dimensions, plate size, battery, camera, screw sizes. Every calculation reads from here | Whenever a real dimension changes |
| `fields.yaml` | The measurement spec — one entry per number a human must measure, with its question, unit, target, and plausible range | When a new `TODO` appears in `params.yaml` |
| `components/loadout.yaml` | Each electronic component's mass and its x/y/z position on the frame. Feeds the centre-of-gravity calculation | When you weigh a component or move it |
| `components/materials.yaml` | Wood density lookup table, in grams per cubic centimetre | Rarely — when using a new material |
| `docs/measurements.md` | The checklist you carry to the bench. 33 blanks, ticked off as you measure | Automatically, by `frame set` |

### `src/frame_tools/` — the drone-specific half

Everything here knows what a propeller is. Nothing here may import `fcc`, except
`cli.py`.

| File | What it does |
|---|---|
| `params.py` | Finds the project root, loads the YAML files, resolves screw and hole sizes. The bottom of the stack — nearly everything imports it |
| `geometry.py` | **The solver.** Works out how long the arms must be so the propellers clear each other and the centre plate, and where each motor sits. Geometry is solved here exactly once; nothing downstream recalculates a dimension |
| `mass.py` | Adds up the wood and the components, and finds the centre of gravity. On a multirotor the CG must sit at the thrust centre or the aircraft fights you |
| `thrust.py` | Thrust-to-weight ratio and hover throttle percentage, from motor thrust and total mass |
| `validate.py` | The ten pre-cut checks. Each returns a status, a name, and a human-readable detail line. Run before putting a blade in wood |
| `fusion.py` | Builds the handoff payload — the resolved numbers packaged for the CAD program |
| `dxf_out.py` | Writes the kerf calibration coupon, the one cut file that does not need CAD |
| `cli.py` | All eight terminal commands, and the single wiring point between the two halves of the codebase |

### `src/fcc/` — the general-purpose half

Nothing here knows what a propeller is. This is the part Phase 8 will prove can
drive a completely different project unchanged.

| File | What it does |
|---|---|
| `fields.py` | Loads and validates `fields.yaml`; looks up one field by id; reads a field's current value |
| `writer.py` | The surgical writer. Changes one value in one line and leaves every other byte alone |
| `errors.py` | The five named failure types, so a caller can tell which kind of wrong happened |
| `__init__.py` | Package marker and version |

### `fusion_scripts/` — code that runs inside the CAD program

These run in Fusion's own Python interpreter, not the project's. The `adsk`
library they import exists only inside Fusion. **Inside Fusion every length is
in centimetres regardless of document units** — `_common.py` converts at that
boundary.

| File | What it does |
|---|---|
| `sync_params.py` | Run this first. Pushes the numbers from `frame fusion` into Fusion's User Parameter table so every sketch dimension is driven by the project |
| `hole_pattern.py` | Stamps bolt circles and square hole patterns into a sketch |
| `nest_parts.py` | Checks the cut parts fit on the 250×250mm sheet and draws where each goes |
| `mass_check.py` | Compares Fusion's real geometry against the estimate from `frame mass`. Disagreement means one of them is wrong — find out which before cutting |
| `export_dxf.py` | Exports every sketch named `CUT_*` to the `dxf/` folder |
| `_common.py` | Shared helpers and the millimetre/centimetre conversion. Not a script itself |
| `frame_params.json` | The generated handoff file. Machine-written by `frame fusion -o` — never edit by hand |

### `tests/` — what stops the project rotting

| File | What it guards |
|---|---|
| `test_geometry.py` | The design invariants: propellers clear each other, parts fit the sheet |
| `test_fields.py` | The measurement spec loads, and broken specs are rejected |
| `test_writer.py` | Byte-exact writes, comments surviving, atomic replacement |
| `test_boundaries.py` | Path safety, the import-direction rule, and both new CLI commands |
| `test_fusion.py` | The handoff payload and the generated cut files |
| `test_fusion_scripts.py` | The Fusion scripts, run against a fake `adsk` library |
| `fusion_stub.py` | That fake `adsk` library. Not a test — a stand-in so Fusion code can run outside Fusion |
| `test_structure.py` | Every folder has a `README.md` with a purpose line and a portal table |
| `test_protocol.py` | The planning workflow documents stay consistent |
| `test_privacy.py` | No credentials, personal paths, or email addresses in any committed file |

### `docs/` — the written half of the project

| Folder / file | What it holds |
|---|---|
| `docs/project/description.md` | **The mission baseline.** What this project is and is not. Read before any major change |
| `docs/project/architecture.md` | The technical stack, and every architectural decision with its reasoning |
| `docs/project/roadmap.md` | The nine-phase build order from here to a finished project |
| `docs/measurements.md` | The bench checklist |
| `docs/build-log.md` | Dated record of what actually happened during the build |
| `docs/brainstorming/` | Rough ideas before a plan exists. Nothing here is binding until promoted |
| `docs/protocol/` | The Plan-Gate-Verify rules: roles, contracts, gates, trust boundaries |
| `docs/claude/` | The planner/verifier role contract and the verification checklist |
| `docs/codex/` | The implementer's inbox: plans, error-fixes, gate reports, templates |
| `docs/knowledge/` | The export contract — what a finished thing looks like when handed to a separate knowledge project |
| `docs/reports/` | Phase reports. This document |

### Output and asset folders

| Folder | What it holds |
|---|---|
| `cad/` | Fusion `.f3d` and `.step` exports. Binary — commit milestones only |
| `dxf/` | Vector cut files for the laser or CNC. Generated, not hand-edited |
| `photos/own/` | Photos you take of the actual parts |
| `photos/reference/` | Web reference images, with `SOURCES.md` recording where each came from |

### Configuration and helper scripts

| File | What it does |
|---|---|
| `CLAUDE.md` | The master index. Every folder, every portal, the conventions, the commands |
| `README.md` | The human front door — the same map, aimed at a person rather than a tool |
| `pyproject.toml` | Package definition, dependencies, and which folders ship in the wheel |
| `conftest.py` | Chooses a writable temporary folder for the test run at startup |
| `.mcp.json` | The Fusion connection endpoint |
| `.vscode/` | Interpreter path, test runner, and debug configuration |
| `install-fusion-scripts.ps1` | Registers `fusion_scripts/` with Fusion as links back to this repository, so editing here edits what Fusion runs |
| `carry-session.ps1` | Moves an assistant conversation into this project's session store |

### How to answer a question about this project

| You want to know | Go here |
|---|---|
| Why is the arm this long? | `src/frame_tools/geometry.py` — the only place it is solved |
| Where does this number come from? | `params.yaml`, and the `# TODO` comment on its line |
| What still needs measuring? | Run `frame fields` |
| Why did a check fail? | `src/frame_tools/validate.py` — each check carries its own explanation |
| What is the plan for feature X? | `docs/codex/claudePlan-<slug>-N.md` |
| What was decided, and why? | `docs/project/architecture.md` |
| What gets built next? | `docs/project/roadmap.md` |
| What does this folder hold? | Its own `README.md` — every folder has one |

---

## 6. Two safety rules that are enforced by tests, not by convention

**Path containment.** The writer refuses any target that resolves outside the
project folder, refuses `..` traversal, and refuses `.git/`, `.venv/`, and cache
folders. The check resolves the path to its true location first, because
inspecting the text of a path is not enough — `docs/../../secrets.yaml` contains
no obvious warning sign as a string.

**Direction of dependency.** The project is split in two on purpose:

- `src/frame_tools/` — everything specific to drone frames: geometry, mass,
  thrust, validation.
- `src/fcc/` — the general-purpose half: read a field spec, write a value
  surgically. Nothing in it knows what a propeller is.

The rule is that the general half must never depend on the drone-specific half,
because Phase 8 plans to prove `fcc` works for a completely different project. A
test enforces it by reading the source files and failing if any drone-specific
module imports `fcc`.

There is exactly one deliberate exception: `cli.py`, which is where the two
halves are wired together. The test **names that file explicitly** and also
asserts that it *does* import `fcc` — so the exception cannot quietly rot into a
dead rule, and a second file cannot join it by accident.

---

## 7. How the work was actually reviewed, and what that caught

This project separates the agent that writes code from the agent that verifies
it. Plans are files, not chat messages, and each phase ends with a written
sign-off or a written error-fix. Phase 1 ran four review rounds. Three failed.

That is not a sign of trouble — it is the process finding real defects. What was
caught is more interesting than the count.

### Round 1 — a test that could not fail

The requirement was: *"a test enumerates the `TODO` markers and fails if any
lacks a spec row."* The test that shipped compared against a hardcoded list of
21 names. It passed. It would also have passed if someone added a new `TODO` to
`params.yaml` and forgot the spec row, which is the only situation the test
existed for.

The fix made the test read the actual files. It was then proven by deliberately
adding a fake `TODO` marker, confirming the test failed, and removing it. **For
a test whose entire purpose is to fail under a specific condition, watching it
fail is the only proof that counts.**

Round 1 also caught an ambiguity: three separate fields used the checklist label
`Mass`, which matched three different lines in the checklist under different
headings. Whichever one the writer ticked would have been a coin flip. The fix
made labels unique and added the "exactly one match" rule described in section 3.

### Round 2 — the environment split

The `conftest.py` story. Three rounds on temporary directory selection, started
by a confidently wrong diagnosis on the reviewing side. Recorded here because
"the reviewer was wrong first" is part of an honest account.

### Round 3 — the line-ending defect, and why every test missed it

This one is the most instructive thing in the phase.

The headline requirement was: *"after writing one value, exactly one line
differs; every other line is byte-identical."* The test asserting this passed.
The property was false.

On Windows, text files can end their lines with two characters (`\r\n`) or one
(`\n`). This repository's working files were mixed: `params.yaml` used two,
`components/loadout.yaml` used one, and `docs/measurements.md` used two on most
lines and one on three of them.

The writer read files with Python's default text mode, which **silently converts
every `\r\n` into `\n`** on the way in. It then wrote back out without
converting. Result: writing a single value rewrote all 67 lines of
`params.yaml`, because every line's invisible ending had changed.

Three separate things hid this:

1. **The test copied its fixture with the same translating function**, so the
   copy did not preserve the original bytes.
2. **The test compared results with the same translating function**, so both
   sides were normalised before comparison. A change to every line ending was
   literally invisible to the assertion.
3. **Git hid it too.** The repository is configured to normalise line endings
   when staging, so `git diff` reported `1 file changed, 1 insertion(+),
   1 deletion(-)` — completely reasonable-looking evidence that was
   nevertheless not evidence of the thing being claimed.

It surfaced only by copying the files with a byte-for-byte copy and comparing
with a byte-for-byte read.

The fix was one line — open the file in a mode that performs no translation, so
each line keeps its own ending exactly as found. The test fix was larger:
copy bytes, compare bytes, assert the counts of each line-ending type are
unchanged, and add synthetic test files in all three styles so the test still
works if these particular files ever change.

Then the fix was reverted on purpose to confirm the new tests fail without it —
six failures, including the two-character and mixed cases, while the
one-character case correctly stayed green. That last detail matters: it proves
the test checks *preservation*, not the presence of a particular style.

**The lesson, stated plainly:** if an assertion says "byte-identical" but the
comparison goes through a function that normalises text, the assertion is
decorative. Three independent layers of tooling agreed the code was correct.
The bytes disagreed.

### The pattern across all three

In two of the three failed rounds the implementation was fine and **the test was
the defect.** Not missing tests — present, passing, confidently green tests that
could not detect the failure they were named after. Worth carrying into future
work: when a test guards a property, ask what would have to break for it to go
red, and then go break it.

---

## 8. By the numbers

| Measure | Before | After |
|---|---|---|
| Automated tests | 116 | 159 |
| Test failures / errors | 0 | 0 |
| Design checks passing | 10 of 10 | 10 of 10 |
| New source files | — | 5 |
| New lines of production code | — | ~590 |
| New lines of test code | — | ~675 |
| New runtime dependencies | — | **0** |
| Measurable numbers with a spec row | 0 | 21 |
| Values in `params.yaml` changed by this work | — | **0** |

That last row is deliberate. This phase built the machine for changing those
numbers and did not change a single one. The guesses stay guesses until someone
picks up calipers — which is Phase 3's job, not a tool's.

Note also that test code slightly exceeds production code, and that no new
dependency was added. `pyyaml` was already present and was sufficient.

---

## 9. What this phase does *not* do

Stated plainly so nobody discovers it by surprise.

- **No browser interface.** That is Phase 2. Everything here is terminal-only.
- **It does not remove `# TODO` markers.** Deliberate: the marker records that a
  line was originally a guess, and stripping it was ruled out of scope. The
  checklist tick in `docs/measurements.md` is the record of what has actually
  been measured.
- **Five fields will always display `[TODO guess]`.** `center_plate_width`,
  `center_plate_length`, and the three battery dimensions have no matching
  checklist line, so their status is read from the `# TODO` comment — which
  never goes away. Their values are written correctly; only the status label is
  uninformative. The fix belongs in a later phase: add checklist lines for those
  measurements, which the physical build wants anyway.
- **It handles single-line YAML shapes only.** Nested blocks and multi-line lists
  are refused rather than mangled. The current files contain none, and the
  refusal is a feature.
- **It is not a general YAML editor** and should not become one. Every increase
  in what it will attempt is a decrease in what it guarantees.

---

## 10. Did it meet the roadmap's bar?

The roadmap set five exit criteria for Phase 1. All five verified, several by
running the criterion's own literal example:

| # | Criterion | Result |
|---|---|---|
| 1 | Every `TODO` has a spec row; a new `TODO` fails a test | **Met** — proven by injecting a fake `TODO` and watching the test fail |
| 2 | One value changes exactly one line, key and comment byte-identical | **Met** — 1 of 67 lines; comment count and both line-ending counts unchanged |
| 3 | Refuses anything it cannot edit surgically; never reformats | **Met** — named error; a test greps the source to prove no YAML dump exists |
| 4 | `frame set motor_bolt_circle 9.4` updates the file **and** ticks the box | **Met** — ran exactly that command; both files updated, one line each |
| 5 | A failing value is still written and the failure reported | **Met** — exit code 0, value saved, failing check printed verbatim |

The plan itself carried 25 finer-grained criteria. All 25 verified.

---

## 11. What this unblocks

The roadmap's stated milestone for this phase was *"first measurement written by
tool, not by hand — the spine works."* That is now true.

Concretely:

- **Phase 3 (measure reality) can start today.** The roadmap deliberately made
  Phase 1 independently useful: if the browser UI in Phase 2 slipped forever,
  every measurement could still be recorded from the terminal, safely. That
  property held.
- **Phase 2 (the browser UI) has its foundation.** The form will be generated
  from `fields.yaml` and will write through this same writer. No field name,
  unit, or range will need to appear in the front-end code.
- **Phase 7 (the 3D viewer)** has its `shape_hint` field waiting, unused.
- **Phase 8 (generalisation)** has the `fcc` / `frame_tools` split real and
  test-enforced rather than merely intended.

The honest summary: this phase produced no visible product and moved the drone
frame no closer to existing. What it did was make the next 21 edits to the
project's most important file safe to perform — which is the difference between
a measurement session that improves the design and one that quietly destroys the
record of where every number came from.
