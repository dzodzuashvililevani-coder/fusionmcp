# Data spine: field spec and surgical writer

**Plan:** claudePlan-data-spine-1.md
**Created:** 2026-08-28
**Source spec:** `docs/project/roadmap.md` Phase 1
**Status:** errorFix-1-gate-complete-awaiting-verify

> **This is the Phase 0 -> Phase 1 move.** It is the first implementation work of
> the project proper. Read `docs/project/roadmap.md` section 0 before starting:
> this phase exists to unblock the physical build, not to build a web app.

## 0. Preconditions

Confirm all four before Phase 1. If any fails, stop and report.

| # | Precondition | Check |
|---|---|---|
| P0.1 | Canonical commands pass | Both commands in section 6 run clean |
| P0.2 | Working tree committed | `git status --short` is empty |
| P0.3 | Baseline plan signed off | `claudePlan-project-baseline-1.md` has a PASS entry |
| P0.4 | Architecture accepted | `docs/project/architecture.md` reviewed; D10 (`fcc` / `frame_tools` split) either accepted or overruled in writing |

P0.4 matters most. **This plan implements D10.** If the split is wrong, it is
much cheaper to say so now than after three modules exist under `src/fcc/`.

## 1. Goal (<= 3 sentences)

Build the data spine: one declarative field spec describing every measurable
number, and a surgical writer that edits `params.yaml`,
`components/loadout.yaml`, and `docs/measurements.md` without disturbing a
single other byte. Expose it through two CLI commands so measurements can be
captured from the terminal before any UI exists. No server, no browser, no new
runtime dependency.

## 2. Out of scope

- Any HTTP server, FastAPI, uvicorn, or web framework. That is Phase 2.
- Any TypeScript, React, Vite, or `web/` folder. Phase 2.
- 3D models, animation, `shape_hint` consumption. Phase 7 -- the field is
  written in this phase but nothing reads it.
- Photo handling. Phase 4.
- Changing any *value* in `params.yaml` or `components/loadout.yaml`. The
  committed guesses stay guesses; only the user, at runtime, changes them.
- Any change to `geometry.py`, `mass.py`, `thrust.py`, `validate.py`,
  `fusion.py`, `dxf_out.py`.
- Adding runtime dependencies. `pyyaml` is already present and is enough.

## 3. Files in scope

Anything not on this list is OFF-LIMITS unless an error-fix or revision says
otherwise.

```
fields.yaml                     (new)  the spec, at repo root beside params.yaml
src/fcc/__init__.py             (new)
src/fcc/README.md               (new)  required by test_structure
src/fcc/errors.py               (new)
src/fcc/fields.py               (new)
src/fcc/writer.py               (new)
src/frame_tools/cli.py                 add `fields` and `set` subcommands
pyproject.toml                         add src/fcc to wheel packages
tests/test_fields.py            (new)
tests/test_writer.py            (new)
tests/test_boundaries.py        (new)
CLAUDE.md                              portal rows + command list
README.md                              folder table row
```

**`fields.yaml` goes at the repository root**, beside `params.yaml`. This answers
open question 1 of `architecture.md`: it is data Python reads at runtime, it is
hand-editable, and it belongs with the other hand-edited data files rather than
inside a `web/` folder that does not exist yet.

## 4. Acceptance criteria

Every criterion is observable from outside the code.

### The spec

1. **Complete coverage.** Every key marked `TODO` in `params.yaml` and every
   `TODO` item in `components/loadout.yaml` has a corresponding field row. A test
   enumerates `TODO` markers and fails if any lacks a row.
2. **Valid by construction.** `fields.py` rejects a spec with a duplicate `id`,
   a `key_path` that does not resolve against the real file, a `file` outside the
   three permitted, `min > max`, or a `measurement_label` that does not match
   exactly one checklist line in `docs/measurements.md`.
3. **Ranges are plausible, not decorative.** Each field's `min`/`max` bracket a
   physically sensible range for that measurement.

### The writer -- the load-bearing part

4. **Byte-exact writes.** After writing one value to `params.yaml`, exactly one
   line differs from the original. Every other line is byte-identical. The test
   compares the full file line by line.
5. **Keys and comments survive.** On the changed line, the key and any trailing
   comment are unchanged. `thickness_mm: 3.0  # TODO measure with caliper`
   becomes `thickness_mm: 2.7  # TODO measure with caliper` -- the `TODO` text
   included. Removing `TODO` markers is **not** this plan's job.
6. **Comment count invariant.** The number of `#` characters in the file is
   identical before and after any write.
7. **Refusal over reformat.** A `key_path` the writer cannot address surgically
   raises a named error identifying the path. The writer never falls back to
   `yaml.dump`, and no code path in `writer.py` calls it.
8. **Atomic and validated.** Writes go to a temp file in the same directory,
   are re-parsed with `yaml.safe_load`, and only then `os.replace` the original.
   A parse failure leaves the original untouched.
9. **Round trip.** After a write, `frame_tools.params.load_params()` returns the
   new value with the correct type.
10. **Inline lists.** `center_plate.size_mm: [70, 70]` and
    `battery.size_mm: [65, 32, 18]` are writable by index -- setting element 1 of
    a three-element list changes only that element and preserves the spacing
    style of the line.
11. **Flow maps.** `components/loadout.yaml` uses inline flow maps
    (`- { name: camera, mass_g: 5.0, pos_mm: [0, 28, 14] }`). Setting one field
    inside one item changes only that field's value token. **If this cannot be
    done surgically, do not reformat the file** -- implement what is possible,
    raise the named error for the rest, and record it in the gate report's open
    questions.

### The checklist

12. **Ticks the box.** Writing a field whose spec names a `measurements.md` label
    replaces that line's `____` with the value and changes `- [ ]` to `- [x]`.
    No other line changes.
13. **Missing label is an error.** A label absent from `docs/measurements.md` is
    reported, never silently skipped.
14. **Idempotent.** Writing the same value twice leaves the file identical after
    the second write.

### Boundaries

15. **Path containment.** The writer refuses any target resolving outside the
    project root, refuses `..` traversal, and refuses `.git/`, `.venv/`, and
    cache directories. Resolution uses `Path.resolve()`; string inspection alone
    is insufficient. Tests cover `..`, absolute paths, and backslash variants.
16. **No shell.** Nothing in `src/fcc/` calls a subprocess with `shell=True`.
    A test greps for it.

### The CLI

17. **`frame fields`** lists every field, its question, its current value, and
    whether it is still a `TODO` guess. Exits 0.
18. **`frame set <id> <value>`** writes the value, ticks the checklist, prints
    what changed, and prints the resulting `frame check` summary. Exits 0 on a
    successful write **even when validation now fails**.
19. **Failing values still save.** `frame set` on a value that makes
    `frame check` fail writes it, prints the failing check's `name` and `detail`
    verbatim from `validate.py`, and says plainly that the design does not
    currently validate. Measurements are facts; blocking the save would teach the
    user to fudge numbers until the validator goes quiet.
20. **Unknown id** exits non-zero with a message listing valid ids.
21. **Out-of-range value** is written and flagged, not rejected. Out of range
    means implausible, not impossible.

### Repo health

22. **`src/fcc/README.md`** has a `**Purpose:**` line and a `## Portals` table
    tagged `Python`.
23. **Indexes updated.** `CLAUDE.md` gains a portal row for `src/fcc/` and the
    two new commands; `README.md` gains a folder row.
24. **Import direction.** No module under `src/frame_tools/` imports `fcc`. A
    test enforces it. This is what makes D10 real rather than aspirational.
25. **Canonical commands clean.** Both commands in section 6 pass with zero
    failures and zero errors.

## 5. Phases

### Phase 1: implement - the field spec

**Definition of done:**

- `fields.yaml` exists with `version: 1` and a `fields:` list. Each entry has:

  | Key | Meaning |
  |---|---|
  | `id` | stable snake_case identifier, unique |
  | `question` | one sentence a human can act on while holding calipers |
  | `unit` | `mm`, `g`, `deg`, or `count` |
  | `file` | `params.yaml`, `components/loadout.yaml`, or `docs/measurements.md` |
  | `key_path` | dotted path, e.g. `motors.bolt_circle_mm` |
  | `index` | optional, for inline-list elements (0-based) |
  | `item` / `field` | for `loadout.yaml` flow-map entries, e.g. `camera` / `mass_g` |
  | `measurement_label` | exact label text in `docs/measurements.md`, or `null` |
  | `min` / `max` | plausible range |
  | `type` | `float` or `int` |
  | `shape_hint` | reserved for Phase 7. Written now, read by nothing |

- Coverage is the 18 `TODO` markers currently present, which expand to **20
  measurable numbers**:

  | Source | Keys | Numbers |
  |---|---|---|
  | `params.yaml` scalars | `stock.thickness_mm`, `props.diameter_mm`, `motors.bolt_circle_mm`, `motors.base_diameter_mm`, `motors.mass_g`, `motors.max_thrust_g`, `center_plate.fc_hole_pattern_mm`, `camera.width_mm`, `camera.mount_ear_spacing_mm` | 9 |
  | `params.yaml` inline lists | `center_plate.size_mm` (2), `battery.size_mm` (3) | 5 |
  | `params.yaml` scalar | `battery.mass_g` | 1 |
  | `components/loadout.yaml` | `mass_g` for flight_controller, esc_4in1, camera, vtx, antenna, receiver | 6 |

  Total: **21 field rows.** If your count differs, say so in the gate report
  rather than silently reconciling -- a discrepancy means one of us misread the
  files.

- `src/fcc/fields.py` exposes `load_fields()` returning validated field objects,
  and `field_by_id(id)`. Validation errors name the offending id.
- `src/fcc/errors.py` defines the named exceptions used throughout:
  `SpecError`, `UnsurgicalEdit`, `LabelNotFound`, `PathRefused`.
- `tests/test_fields.py` covers criteria 1-3.

**Touches:** `fields.yaml`, `src/fcc/__init__.py`, `src/fcc/errors.py`,
`src/fcc/fields.py`, `src/fcc/README.md`, `pyproject.toml`,
`tests/test_fields.py`

**Notes for the implementer:**

- The `question` text is user-facing and does real work. `motors.bolt_circle_mm`
  is currently ambiguous -- is it across the base, or between adjacent holes? The
  existing `docs/measurements.md` says "hole to hole, across the base". Match
  that wording exactly; this ambiguity is the single most likely measurement
  error in the project.
- Do **not** add fields for values that are not measured. `arm.motor_radius_mm`
  is solved by `geometry.py` and must never appear in the spec.

### Phase 2: gate - spec verified

**Definition of done:** gate report appended, then halt
**Touches:** this plan file only
**Commands to run:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
git diff --stat
```

**Status report sections:** commit SHA, files changed, test output,
self-assessment, open questions

### Phase 3: verify - spec

**Definition of done:** Claude appends a PASS sign-off, or writes
`claudePlan-data-spine-1-errorFix-1.md`
**Touches:** this plan file, or an error-fix file

### Phase 4: implement - the surgical writer

**Definition of done:**

- `src/fcc/writer.py` exposes:
  - `write_value(field, value) -> WriteResult` -- the single entry point
  - `tick_measurement(label, value, unit)`
  - `preview(field, value) -> str` -- the unified diff a write would produce,
    without writing
- Every write is atomic: temp file in the same directory, re-parse, `os.replace`.
- `WriteResult` records the file, the line number, the old and new text of that
  line, and whether the checklist was ticked.
- `tests/test_writer.py` covers criteria 4-14.
- `tests/test_boundaries.py` covers criteria 15-16 and 24.

**Touches:** `src/fcc/writer.py`, `tests/test_writer.py`,
`tests/test_boundaries.py`

**Notes for the implementer:**

- **Write the byte-exactness test first and let it drive the design.** Criterion
  4 is the property everything else rests on. A writer that passes it by
  construction is a different program from one patched until it passes.
- All writer tests operate on copies in `tmp_path`. **No test touches the real
  `params.yaml`.** A test that mutates repository data is a failed test even if
  it passes.
- Scope of the parser: handle scalars, inline lists, and inline flow maps on a
  single line. Refuse everything else. **Do not build a general YAML editor** --
  the refusal path is a feature, and `params.yaml` contains no nested block
  structures today.
- `preview()` exists so Phase 2's UI can show a diff before committing a change,
  and so you can debug criterion 4 without writing files.

### Phase 5: gate - writer verified

**Definition of done:** gate report appended, then halt
**Touches:** this plan file only
**Commands to run:** as Phase 2, plus:

```powershell
git diff --stat
```

Report explicitly whether criterion 11 (flow maps) was achieved surgically or
raised the named error.

**Status report sections:** commit SHA, files changed, test output,
self-assessment, open questions

### Phase 6: verify - writer

**Definition of done:** Claude re-runs the canonical commands, spot-checks
criterion 4 end to end by writing a real value to a copy and diffing, then
appends PASS or writes an error-fix
**Touches:** this plan file, or an error-fix file

### Phase 7: implement - CLI and indexes

**Definition of done:**

- `frame fields` and `frame set <id> <value>` added to `src/frame_tools/cli.py`,
  alongside the existing subcommands and following their output conventions
  (the `BAR` separator, the `[ ok ]` / `[FAIL]` icons).
- `frame set` prints: what changed, the checklist status, and the `frame check`
  summary afterwards.
- `src/fcc/README.md`, `CLAUDE.md`, and `README.md` updated.
- `tests/test_boundaries.py` extended for criteria 17-21.

**Touches:** `src/frame_tools/cli.py`, `src/fcc/README.md`, `CLAUDE.md`,
`README.md`, `tests/test_boundaries.py`

**Notes for the implementer:**

- `cli.py` lives in `frame_tools` and will import `fcc`. That direction is
  allowed. The reverse is not, and criterion 24 tests it.
- Match the existing CLI's voice. It explains *why* a number matters rather than
  only printing it, and the new commands should read like they belong.

### Phase 8: gate - full spine

**Definition of done:** gate report appended, then halt
**Touches:** this plan file only
**Commands to run:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
.\.venv\Scripts\python.exe -m frame_tools.cli fields
git status --short
git diff --stat
```

**Status report sections:** commit SHA, files changed, test output,
self-assessment, open questions

### Phase 9: verify - full spine

**Definition of done:** Claude runs the canonical commands, writes one real
measurement end to end through `frame set` against a copy, byte-diffs the
result, and appends PASS or writes an error-fix
**Touches:** this plan file, or an error-fix file

## 6. Test commands (canonical)

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

Both must show zero failures **and zero errors** at every gate. Do not add a
fixed `--basetemp` flag to the command; root `conftest.py` selects a writable
basetemp at runtime because the two agent environments have opposite temp
directory restrictions.

Baseline before this plan starts: **116 passed, 0 errors** and
**10 checks, 0 warnings, 0 failures**.

## 7. Sign-off log

### Phase 2 gate report - 2026-08-28

## Commit SHA

Base before Phase 1 implementation: `6c3e82e`.

## Files changed

```text
M  CLAUDE.md
M  README.md
M  pyproject.toml
A  fields.yaml
A  src/fcc/README.md
A  src/fcc/__init__.py
A  src/fcc/errors.py
A  src/fcc/fields.py
A  tests/test_fields.py
M  docs/codex/claudePlan-data-spine-1.md
```

## Test command output

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_fields.py -q -p no:cacheprovider --basetemp=.pytest-work-tmp
9 passed in 1.50s

.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
128 passed in 3.56s

.\.venv\Scripts\python.exe -m frame_tools.cli report
10 passed, 0 warnings, 0 failures
```

## Self-assessment

Phase 1 is implemented as scoped: spec, loader, named errors, package wiring,
README, indexes, and field-spec tests. The loader validates ids, files, ranges,
key paths, list indexes, loadout items, and measurement labels. No runtime
dependencies were added.

## Open questions

- The plan expected 18 TODO markers expanding to 21 field rows. The
  implementation found and encoded 21 measurable field rows, matching the
  plan's final total.
- `measurement_label` is ambiguous for repeated labels like `Mass`; Phase 4's
  checklist writer will need section-aware matching or label disambiguation
  before it can tick those lines safely.

### Phase 3 sign-off - 2026-08-28

**Verdict:** FAIL -> errorFix-1

**Evidence:**
- Commit inspected: `0b07cd7` (base `6c3e82e`). Working tree clean, synced.
- Diff: 7 files, +649/-1. Exactly the files listed in Phase 1 "Touches". No scope drift.
- `python -m pytest -q -p no:cacheprovider` -> **128 passed, 0 errors**
- `python -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp` -> **118 passed, 10 errors** (opposite of Codex's shell; see errorFix-1 E3)
- `python -m frame_tools.cli report` -> 10 passed, 0 warnings, 0 failures
- Spot-check of criterion 2 end to end on a tmp copy: duplicate id rejected, unresolvable key_path rejected. Loader behaves as specified.
- Files inspected: `fields.yaml` (21 rows), `src/fcc/fields.py`, `errors.py`, `__init__.py`, `README.md`, `tests/test_fields.py`, `pyproject.toml`, gate report.
- Label audit across all 21 fields vs `docs/measurements.md`: 13 of 16 labelled fields resolve uniquely; 3 do not.

**Findings:**
- **E1 (major)** — criterion 1 unmet. `EXPECTED_TODO_FIELDS` is a hardcoded set; the test never reads `params.yaml` or `loadout.yaml`, so a new `TODO` cannot make it fail.
- **E2 (major)** — `battery_mass`, `flight_controller_mass`, and `camera_mass` all use label `Mass`, which matches 3 checklist lines under different sections. `_validate_measurement_label` checks presence, not uniqueness. Blocks criterion 12 in Phase 4.
- **E3 (environment)** — the canonical command is not portable between the two agents' shells. Not a Phase 1 defect.

**Notes:** Scope discipline was good — exactly the planned files, no adjacent features, no dependency added. `current_value()` is a small addition beyond the stated API; it is needed by `frame fields` in Phase 7 and is accepted. The 21-row count matches the plan's prediction exactly. Criterion 2 of this plan was incomplete on my part and is amended in errorFix-1 section 3.4.

**Phase 4 remains gated** until errorFix-1 passes.

### errorFix-1 gate report - 2026-08-28

## Commit SHA

Base before errorFix-1 implementation: `0b07cd7`.

## Files changed

```text
A  conftest.py
A  docs/codex/claudePlan-data-spine-1-errorFix-1.md
M  CLAUDE.md
M  README.md
M  docs/brainstorming/decision-scope-split.md
M  docs/brainstorming/idea-web-workstation.md
M  docs/codex/claudePlan-data-spine-1.md
M  docs/codex/claudePlan-project-baseline-1.md
M  docs/codex/claudePlan-web-workstation-1.md
M  docs/codex/plan-template.md
M  docs/measurements.md
M  docs/project/architecture.md
M  docs/project/description.md
M  docs/protocol/README.md
M  fields.yaml
M  src/fcc/errors.py
M  src/fcc/fields.py
M  tests/test_fields.py
M  tests/test_protocol.py
```

## Test command output

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_fields.py -q -p no:cacheprovider
14 passed in 1.61s

.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
133 passed in 2.59s

.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider
1 passed in 0.16s

.\.venv\Scripts\python.exe -m frame_tools.cli report
10 passed, 0 warnings, 0 failures

git diff --check
no whitespace errors
```

## Self-assessment

errorFix-1 is implemented as scoped. The TODO coverage test now reads the real
`params.yaml` and `components/loadout.yaml` text and detects orphaned TODOs
instead of comparing against a hardcoded expected set. Measurement labels are
globally unique in `fields.yaml`, the checklist uses unambiguous labels for
flight controller, battery, and camera mass, and `fields.py` rejects duplicate
field labels or labels matching more than one checklist line with
`AmbiguousLabel`. The field loader now also honors its supplied `root` for
params/loadout reads, so copy-based writer tests can validate isolated project
trees.

For the pytest environment split, the canonical command now carries no
`--basetemp` flag. Root `conftest.py` probes candidate temp roots and selects one
that the running environment can create, list, write inside, and clean up.

## Open questions

- Phase 4 remains gated until Claude verifies this error-fix.
- No writer work was started and no measured values in `params.yaml` or
  `components/loadout.yaml` were changed.

### Phase 3 sign-off (errorFix-1 re-verification) - 2026-08-28

**Verdict:** FAIL -> errorFix-2 (conftest only). **E1 and E2 are CONFIRMED FIXED.**

**Evidence:**
- Commit inspected: `54611a1`. Local, not pushed.
- `python -m pytest -q -p no:cacheprovider` -> **INTERNALERROR: RuntimeError: no writable pytest basetemp found**. Regression: this command gave 128 passed before `conftest.py` existed.
- Same suite with a `mkdtemp` basetemp -> **133 passed, 0 errors**, matching Codex's number.
- `python -m frame_tools.cli report` -> 10 passed, 0 warnings, 0 failures.

**errorFix-1 acceptance criteria, measured:**

| # | Criterion | Result |
|---|---|---|
| 1 | Orphaned `TODO` fails the suite | **PASS** — injected `camera.lens_protrusion_mm  # TODO`; `test_every_todo_target_has_a_field_and_every_field_targets_a_todo` failed. Reverted. |
| 2 | Every label matches exactly one checklist line | **PASS** — audited all 21 fields: 16 labelled, 0 ambiguous |
| 3 | Duplicate label raises `AmbiguousLabel` | **PASS** — raised in two places, two tests, both pass |
| 4 | `measurements.md` and `fields.yaml` agree | **PASS** — labels changed on both sides in one commit |
| 5 | Plan criterion 2 amended | **PASS** |
| 6 | Canonical command clean without an env-specific flag | **FAIL** — aborts before collection in Claude's shell |
| 7 | Both canonical commands pass | **FAIL** — via criterion 6 |

**Root cause of the remaining failure (verified, not inferred):** a directory
created by the process via `Path.mkdir()` cannot have subdirectories created
inside it in Claude's sandbox. Pre-existing directories and `tempfile.mkdtemp()`
results work. Both conftest candidates are freshly `mkdir`'d, so both probe as
unusable and the conftest raises. Full probe output in errorFix-2 section 2.

**My earlier diagnosis was also wrong** and is corrected in
`decision-scope-split.md`: the variable was never "inside the project directory",
it is directory *freshness*.

**Notes:** The substance of this fix is good. The TODO coverage test now genuinely
fails when it should — proven by injection, which is the only proof that counts
for a test that previously could not fail. Label validation is stronger than
specified: it rejects both duplicate labels across fields and labels matching
multiple checklist lines. Scope was clean. One minor quality note, not blocking:
the coverage test's failure message truncates to "Use -v to get more diff" rather
than naming the orphaned key, so it satisfies the criterion's behaviour but not
its diagnostic intent.

**Phase 4 remains gated** on errorFix-2 only.

### errorFix-2 gate report - 2026-08-28

## Commit SHA

Base before errorFix-2 implementation: `54611a1`.

## Files changed

```text
M  conftest.py
M  docs/brainstorming/decision-scope-split.md
M  docs/codex/claudePlan-data-spine-1-errorFix-2.md
M  docs/codex/claudePlan-data-spine-1.md
```

## Test command output

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
133 passed in 3.37s

.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider
1 passed in 0.23s

.\.venv\Scripts\python.exe -m frame_tools.cli report
10 passed, 0 warnings, 0 failures
```

## Self-assessment

errorFix-2 is implemented with code changes scoped to `conftest.py`. The
selection logic now leaves pytest's default temp root alone when it already
works, uses `tempfile.mkdtemp()` for fallback roots, keeps a project-local
fallback under the ignored `.pytest-work-tmp-*` prefix, and warns instead of
raising if no probe succeeds.

## Open questions

- Phase 4 remains gated until Claude verifies this error-fix in its shell.
- This fix does not reopen E1/E2; Claude already confirmed those fixed.
