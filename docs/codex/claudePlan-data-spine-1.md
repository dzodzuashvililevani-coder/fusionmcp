# Data spine: field spec and surgical writer

**Plan:** claudePlan-data-spine-1.md
**Created:** 2026-08-28
**Source spec:** `docs/project/roadmap.md` Phase 1
**Status:** complete - all phases verified 2026-08-28

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
24. **Import direction.** *(Amended 2026-08-28, errorFix-3 section 3.5.)* No
    module under `src/frame_tools/` **other than `cli.py`** imports `fcc`.
    `cli.py` is the composition root and may import it; the domain core
    (`params`, `geometry`, `mass`, `thrust`, `validate`, `fusion`, `dxf_out`)
    may not. A test enforces the exemption **by name**, so a second module
    cannot quietly join it. This is what makes D10 real rather than
    aspirational. Until Phase 7 the stricter test stands unchanged.
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

### Phase 3 sign-off (errorFix-2 verification) - 2026-08-28

**Verdict:** **PASS.** Phase 1 is complete and verified. Phase 4 is unblocked.

**Evidence, run in Claude's environment:**

```
python -m frame_tools.cli report                  -> 10 passed, 0 warnings, 0 failures
python -m pytest -q -p no:cacheprovider           -> 133 passed, 0 errors
python -m pytest tests/test_privacy.py -q ...     -> 1 passed
```

**This is the first time both agents' environments agree on the same flag-free
command with the same number.** 133 in Codex's shell, 133 in Claude's.

**errorFix-2 acceptance criteria:**

| # | Criterion | Result |
|---|---|---|
| 1 | Canonical command runs to completion in both shells, no flag, no INTERNALERROR | **PASS** |
| 2 | 133 passed, 0 errors in Claude's shell | **PASS** — matches Codex exactly |
| 3 | Never aborts collection; warns and falls back | **PASS** — `warnings.warn`, no `raise` on the failure path |
| 4 | `frame_tools.cli report` clean | **PASS** |
| 5 | Gate report quotes commands verbatim | **PASS** |

The implementation is exactly as specified: pytest's own default is probed first
and left alone when it works, fallbacks are created with `tempfile.mkdtemp()`
rather than `Path.mkdir()`, and the project-local path is the last resort.

**One defect in this round was mine.** `test_privacy.py` failed on
`docs/codex/claudePlan-data-spine-1-errorFix-2.md` because I pasted verbatim
probe output containing absolute local user paths into it. Codex reported
privacy passing because the file was not yet tracked when it ran. The paths are
now redacted to `<TEMP>` and `<REPO>` placeholders and privacy passes. The test
did exactly its job; the fault was mine for putting local paths in a document
destined for a public repository.

**Notes:** Three rounds on temp-directory selection is more than this deserved,
and my confident wrong diagnosis in round one started the ping-pong. The
resolution is durable rather than a workaround: the conftest now adapts to
whichever environment it finds instead of encoding one agent's assumptions, and
the canonical command carries no environment-specific flag.

**Phase 1 acceptance criteria 1-3 and 22-25 are met and verified.** Criteria 4-21
belong to Phases 4 and 7 and remain open by design.

**Phase 4 (the surgical writer) is now open.** Start from
`claudePlan-data-spine-1.md` section 5, Phase 4.

### Phase 5 gate report - 2026-08-28

## Commit SHA

Base before Phase 4 implementation: `146313d`.

## Files changed

```text
M  docs/codex/claudePlan-data-spine-1-errorFix-2.md
M  docs/codex/claudePlan-data-spine-1.md
A  src/fcc/writer.py
A  tests/test_boundaries.py
A  tests/test_writer.py
```

## Test command output

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_writer.py tests\test_boundaries.py -q -p no:cacheprovider
19 passed in 1.55s

.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
152 passed in 3.96s

.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider
1 passed in 0.15s

.\.venv\Scripts\python.exe -m frame_tools.cli report
10 passed, 0 warnings, 0 failures

git -c core.excludesfile= diff --check --cached
no whitespace errors
```

## Self-assessment

Phase 4 is implemented as scoped. `src/fcc/writer.py` exposes `write_value`,
`tick_measurement`, `preview`, and `WriteResult`. The writer changes one
addressed token per data file write, preserves comments and line formatting,
uses same-directory temp files with YAML re-parse before `os.replace`, refuses
unaddressable edits instead of dumping YAML, and prepares checklist edits before
the data write so a missing checklist label cannot leave a half-applied update.

Criterion 11 is achieved surgically for the current `components/loadout.yaml`
flow-map shape: writing `mass_g` for a named item changes only that value token
on that item's line and preserves the rest of the line.

## Open questions

- Phase 6 verification is owed by Claude before Phase 7 starts.
- The Phase 7 plan contains a conflict: criterion 24 says `frame_tools` must not
  import `fcc`, but the Phase 7 CLI note says `src/frame_tools/cli.py` will
  import `fcc`. Phase 4 keeps the current import-boundary test strict; Phase 7
  should amend that rule before adding CLI imports.

### Phase 6 sign-off (writer verification) - 2026-08-28

**Verdict:** FAIL -> errorFix-3. **One defect, in criterion 4.** Criteria 5-14
are confirmed met.

**Evidence, run in Claude's environment:**

```
python -m pytest -q -p no:cacheprovider           -> 152 passed, 0 errors
python -m frame_tools.cli report                  -> 10 passed, 0 warnings, 0 failures
python -m pytest tests/test_privacy.py -q ...     -> 1 passed
```

Commit inspected: `40032ca` (base `146313d`). Working tree clean, not pushed.
Diff: 5 files, +708/-4. Exactly the Phase 4 "Touches" list plus the two plan
files. No scope drift, no deleted tests, no suppressed warnings, no dependency
added. Files inspected: `src/fcc/writer.py`, `tests/test_writer.py`,
`tests/test_boundaries.py`, `src/fcc/fields.py`, `src/fcc/errors.py`,
`src/fcc/README.md`, `fields.yaml`, the gate report.

**Sweep of all 21 fields** through `write_value` against `shutil.copy2` copies of
the real project files -- every field addressed the correct line, wrote the
correct value, round-tripped through `yaml.safe_load`, preserved the file's `#`
count, and ticked the correct checklist box. Both lines carrying two checkboxes
(`Body width` / `Mount ear spacing`, `Receiver mass` / `Antenna mass and
length`) accept sequential writes to each box independently without disturbing
the other. **Criterion 11 is achieved surgically, as claimed.**

| # | Criterion | Result |
|---|---|---|
| 4 | Byte-exact writes | **FAIL** -- 67 of 68 lines of `params.yaml` change bytes; 66 of 70 in `docs/measurements.md` |
| 5 | Keys and comments survive | **PASS** |
| 6 | Comment count invariant | **PASS** -- all 21 fields |
| 7 | Refusal over reformat | **PASS** -- named error, no `yaml.dump` in source, test greps for it |
| 8 | Atomic and validated | **PASS** -- same-dir `mkstemp`, re-parse, `os.replace`, tmp unlinked on failure |
| 9 | Round trip | **PASS** |
| 10 | Inline lists | **PASS** -- index 1 of 3 changes alone, spacing preserved |
| 11 | Flow maps | **PASS** -- surgical, no reformat, no refusal needed |
| 12 | Ticks the box | **PASS** -- all 21, including both shared lines |
| 13 | Missing label is an error | **PASS** -- raises before any data write |
| 14 | Idempotent | **PASS** |
| 15 | Path containment | **PASS** |
| 16 | No shell | **PASS** |

**The defect:** `_read_target` reads with `Path.read_text()` (universal newlines,
CRLF collapses to LF) while `_atomic_write` writes with `newline=""` (no
translation). The working tree is deliberately mixed -- `params.yaml` is 67 CRLF
lines, `loadout.yaml` is 16 LF lines, `docs/measurements.md` is 66 CRLF plus 3
bare LF. Writing one value flattens `params.yaml` and `docs/measurements.md`
entirely to LF. One line changes in meaning; every line changes in bytes.

**Why nothing caught it, including me on a first read.** `tests/test_writer.py`
copies the fixture with `read_text`/`write_text` and compares with a `read()`
helper that also uses `read_text`, so both sides are normalised before any
assertion sees them. `core.autocrlf` is `true`, so `git diff --stat` reports
`1 file changed, 1 insertion(+), 1 deletion(-)` and the gate report's evidence
was truthful while the property was false. This only surfaced under
`shutil.copy2` plus `read_bytes()`. The plan said to write the byte-exactness
test first and let it drive the design; what exists is a normalised-text test,
and it is the one place a stricter test was worth more than more code.

**Notes:** The writer itself is well built -- the refusal paths are real, the
checklist edit is computed before the data write so a bad label cannot leave a
half-applied update, and the two-checkboxes-per-line case was handled without
being asked for. The fix is one line in `_read_target` plus tests that compare
bytes. Do not rewrite the parser.

**Your open question is answered in errorFix-3 section 3.5.** You were right
that criterion 24 contradicts the Phase 7 CLI note; the error is mine.
Criterion 24 is amended to exempt `cli.py` as the composition root. Leave the
current boundary test untouched until Phase 7.

**Phase 7 remains gated** on errorFix-3.

### Phase 6 sign-off (errorFix-3 re-verification) - 2026-08-28

**Verdict:** **PASS.** Criterion 4 is now genuinely met. Phase 4 is complete and
verified. **Phase 7 is open.**

**Canonical commands, run in Claude's environment:**

```
python -m pytest -q -p no:cacheprovider           -> 155 passed, 0 errors
python -m frame_tools.cli report                  -> 10 passed, 0 warnings, 0 failures
python -m pytest tests/test_privacy.py -q ...     -> 1 passed
```

**errorFix-3 acceptance criteria, measured:**

| # | Criterion | Result |
|---|---|---|
| 1 | New test fails before the fix, passes after | **PASS** -- reproduced independently, see below |
| 2 | One line's bytes change in `params.yaml`, CRLF count held | **PASS** -- 1 of 68 lines; CRLF 67 -> 67 |
| 3 | Same for `docs/measurements.md`, bare-LF lines intact | **PASS** -- 1 of 70 lines; CRLF 66 -> 66, bare LF 3 -> 3 |
| 4 | `components/loadout.yaml` stays pure LF, no CR introduced | **PASS** -- CRLF 0 -> 0 |
| 5 | CRLF / LF / mixed synthetic fixtures round-trip | **PASS** |
| 6 | `writer____` portal row present | **PASS** |
| 7 | Canonical commands clean, flag-free | **PASS** |
| 8 | `test_privacy.py` passes | **PASS** |
| 9 | Only the four in-scope files touched | **PASS** -- `README.md`, `writer.py`, `test_writer.py`, this plan file. No tracked data file rewritten. |

**Injection proof, run by me rather than taken on report.** I reverted
`_read_target` to `read_text()` in place and re-ran `tests/test_writer.py`:

```
6 failed, 8 passed
  test_scalar_write_changes_one_line_and_preserves_comment
  test_inline_list_write_changes_only_target_section_element
  test_preview_returns_diff_without_writing
  test_tick_measurement_handles_second_checkbox_on_same_line
  test_params_write_preserves_per_line_terminators_in_synthetic_files[crlf-...]
  test_params_write_preserves_per_line_terminators_in_synthetic_files[mixed-...]
```

Then restored the fix and re-ran: 14 passed. **The `lf` parameter case correctly
stayed green while `crlf` and `mixed` failed** -- the test is asserting
terminator *preservation*, not the presence of CRLF, which is the distinction
that makes it durable if these files ever convert to LF.

**Independent end-to-end byte proof.** Byte-exact `shutil.copy2` copies of the
real project files, one value written through `write_value`:

```
WriteResult(file='params.yaml', line_number=11,
            old_text='  thickness_mm: 3.0          # TODO measure with caliper
',
            new_text='  thickness_mm: 2.7          # TODO measure with caliper
')

params.yaml:             1 of 68 lines differ in BYTES  | CRLF 67 -> 67, bare LF 0 -> 0
docs/measurements.md:    1 of 70 lines differ in BYTES  | CRLF 66 -> 66, bare LF 3 -> 3
components/loadout.yaml: UNCHANGED (bytes identical)
```

Compare with the same script before the fix: 67 of 68 and 66 of 70. The
`WriteResult` now carries the real terminator, which is a nice secondary
confirmation that the string never lost it.

**Full sweep, byte level.** All 21 fields written to fresh byte-exact copies:
every one changed exactly one line of its data file and exactly one line of
`docs/measurements.md`, preserved that file's CRLF count, bare-LF count, and `#`
count, and round-tripped through `yaml.safe_load` with the correct value. **0
problems across 21 fields.**

**Scope:** exactly the four files errorFix-3 named. The fix is the one line it
should be -- `writer.py` is +2/-1. No parser change, no `.gitattributes`, no
repo-wide normalisation, no Phase 7 work pulled forward. The temptations listed
in errorFix-3 section 5 were all declined.

**Plan amended.** Criterion 24 in section 4 now carries the `cli.py` exemption
from errorFix-3 section 3.5, so Phase 7 starts from a plan that does not
contradict itself. `test_frame_tools_do_not_import_fcc_before_cli_phase` is
correctly still the strict version; renaming it and adding the by-name exemption
is Phase 7 work.

**Phase 4 acceptance criteria 4-16 are met and verified.** Criteria 17-21 belong
to Phase 7 and remain open by design.

**Notes:** Three of the four rounds on this plan came back FAIL, and in two of
them the code was right and the test was the problem. That is the pattern worth
naming: this project's failure mode is not bad implementation, it is tests that
cannot fail. Both times the fix was to make the test observe what the criterion
actually claims -- real `TODO` markers rather than a hardcoded set, real bytes
rather than normalised text. Phase 7's criteria 17-21 are CLI behaviour, which
is easy to assert loosely; write those tests against real invocations and real
exit codes.

**Phase 7 (CLI and indexes) is now open.** Start from
`claudePlan-data-spine-1.md` section 5, Phase 7, with the amended criterion 24.

### Phase 8 gate report - 2026-08-28

## Commit SHA

Base before Phase 7 implementation: `40032ca`.

Phase 7 started with the verified, uncommitted errorFix-3 changes still in the
working tree. This gate report therefore covers the full current working tree,
while calling out the Phase 7 additions separately below.

## Files changed

```text
M  CLAUDE.md
M  README.md
M  docs/codex/claudePlan-data-spine-1.md
M  src/fcc/README.md
M  src/fcc/writer.py
M  src/frame_tools/cli.py
M  tests/test_boundaries.py
M  tests/test_writer.py
?? docs/codex/claudePlan-data-spine-1-errorFix-3.md
```

Phase 7 added behavior in `src/frame_tools/cli.py`, extended
`tests/test_boundaries.py`, and updated the command/index documentation in
`CLAUDE.md`, `README.md`, and `src/fcc/README.md`. `src/fcc/writer.py` and
`tests/test_writer.py` are the already verified errorFix-3 changes.

## Test command output

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_boundaries.py tests\test_writer.py -q -p no:cacheprovider
26 passed in 3.78s

.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
159 passed in 6.56s

.\.venv\Scripts\python.exe -m frame_tools.cli report
10 passed, 0 warnings, 0 failures

.\.venv\Scripts\python.exe -m frame_tools.cli fields
exits 0 and prints all 21 field ids, current values, questions, and TODO status

.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider
1 passed in 0.18s

git diff --check
no whitespace errors; only core.autocrlf working-copy warnings
```

## Self-assessment

Phase 7 is implemented as scoped. `frame fields` lists all field ids with their
current value, question, and whether the value is still a TODO guess. `frame set
<id> <value>` writes through the surgical writer, reports the changed
`file:line`, reports checklist status, warns but still saves out-of-range
values, and then prints the same pre-cut check summary used by `frame check`.

The CLI tests use real subprocess invocations: they copy a temporary mini
project, run `python -m frame_tools.cli ...` against that copy, assert real exit
codes, and byte-check the written project files. The failing-design case sets
`stock_thickness` to `0.5`, confirms exit code 0, confirms the value and
checklist were saved, and confirms the failing check name and detail are printed
from `validate.py`.

Criterion 24 is now enforced with the Phase 7 exemption: `cli.py` may import
`fcc`; every other module under `src/frame_tools/` is still forbidden from doing
so by name.

No real tracked data file changed during this phase:

```powershell
git diff -- params.yaml docs/measurements.md components/loadout.yaml
no output
```

## Open questions

- Phase 9 verification is owed by Claude before the data spine is complete.
- The current tree still contains uncommitted, verified errorFix-3 files from
  the previous round. Commit grouping is left to the user.

### Phase 9 sign-off (full spine verification) - 2026-08-28

**Verdict:** **PASS.** Criteria 17-21 are met. **The data spine is complete.**
All 25 acceptance criteria are now verified. Nothing in this plan remains open.

**Canonical commands, run in Claude's environment:**

```
python -m pytest -q -p no:cacheprovider           -> 159 passed, 0 errors
python -m frame_tools.cli report                  -> 10 passed, 0 warnings, 0 failures
python -m pytest tests/test_privacy.py -q ...     -> 1 passed
```

**Criteria 17-21, exercised as real subprocesses against a full byte-exact copy
of the project (not through the test suite):**

| # | Criterion | Result |
|---|---|---|
| 17 | `frame fields` lists id, question, value, TODO status; exits 0 | **PASS** -- all 21 fields |
| 18 | `frame set` writes, ticks, prints the change and the check summary | **PASS** |
| 19 | Failing values still save, exit 0, check name + detail verbatim | **PASS** -- see below |
| 20 | Unknown id exits non-zero listing valid ids | **PASS** -- exit 2, all 21 ids named |
| 21 | Out-of-range written and flagged, not rejected | **PASS** |

**Criterion 4 still holds through the CLI** -- the end-to-end byte diff the plan
asks for in Phase 9:

```
frame set stock_thickness 2.85        -> exit 0

params.yaml:             1 of 67 lines differ -> [11]
                         CRLF 67->67, LF 67->67, '#' 39->39
  -   thickness_mm: 3.0          # TODO measure with caliper
  +   thickness_mm: 2.85          # TODO measure with caliper

docs/measurements.md:    1 of 69 lines differ -> [45]
                         CRLF 66->66, LF 69->69, '#' 21->21
  - - [ ] Actual thickness (measure, do not trust the label): ____ mm
  + - [x] Actual thickness (measure, do not trust the label): 2.85 mm

components/loadout.yaml: UNCHANGED
```

**Criterion 19 in full, live:**

```
frame set stock_thickness 0.5         -> exit 0
  [warn] stock_thickness is outside the expected 1..8 mm range. Value saved anyway.
  [FAIL] stock thickness
         0.5mm - thin plywood arms flex and cause gyro noise; 3mm+ recommended
  9 passed, 0 warnings, 1 failures
  >> This design does not currently validate. The measurement was saved; fix the design next.
```

Value and checklist tick both persisted. This is the behaviour the criterion was
written for: the measurement is a fact and it lands, the design being wrong is a
separate sentence.

**Also checked live, beyond the criteria:** a loadout-file write
(`vtx_mass 4.4` -> `loadout.yaml:12`, one token, flow map intact), a
non-numeric value (exit 2, named error), an idempotent repeat
(`checklist  already current`), and a `fields` re-run after a write showing
`stock_thickness  2.85 mm  [measured]`.

**Scope:** `cli.py`, `tests/test_boundaries.py`, `CLAUDE.md`, `README.md`,
`src/fcc/README.md` -- exactly the Phase 7 "Touches" list. `git diff` on
`params.yaml`, `components/loadout.yaml`, `docs/measurements.md`, and
`fields.yaml` is empty: no tracked data file was changed by this work, which was
section 2's hard line. `_print_checks` was extracted from `cmd_check` rather
than duplicated, and the new CLI tests run real `subprocess` invocations against
byte-copied projects and assert real exit codes -- which is what I asked for at
the end of the Phase 6 sign-off.

**Criterion 24 as amended is correctly enforced.**
`test_only_cli_imports_fcc_from_frame_tools` exempts `cli.py` by name and also
asserts `cli.py` *does* import `fcc`, so the exemption cannot silently become
dead. That is stronger than the amendment required.

### Known limitation, recorded not fixed -- my gap, not Codex's

Five of the 21 fields have no `measurement_label`, because
`docs/measurements.md` has no checklist line for battery L/W/H or centre-plate
size: `center_plate_width`, `center_plate_length`, `battery_length`,
`battery_width`, `battery_height`. For those, `frame fields` falls back to
reading the `# TODO` comment on the params line -- and the writer never removes
`TODO` markers, correctly, because criterion 5 forbids it. **So those five
report `[TODO guess]` forever, even once measured:**

```
frame set battery_width 34.0          -> writes params.yaml:43 correctly
frame fields                          -> battery_width  34 mm  [TODO guess]
```

The value is right, the write is surgical, the checks re-run. Only the status
column is dead, for 5 of 21 fields.

This is a gap in the field spec I signed off in Phase 3, not a Phase 7
implementation defect -- there is no in-scope fix, since both alternatives
(stripping `TODO` markers, or adding a measured-state store) are explicitly out
of this plan. **No error-fix is warranted.** The clean resolution, for whoever
plans the next phase: add checklist lines to `docs/measurements.md` for battery
dimensions and centre-plate size, and give those five fields labels. That also
gives the physical build somewhere to write those numbers down, which it
currently lacks.

**Two cosmetic notes, neither worth changing now:** a new value of a different
character width shifts the trailing comment's column
(`thickness_mm: 2.85          # TODO`) -- the comment text is untouched, so
criterion 5 holds, but the file's alignment drifts as measurements land. And an
idempotent repeat still prints `changed  params.yaml:11` above two identical
`-`/`+` lines; `checklist  already current` is the line carrying the truth.

**Plan closed.** Nothing was recorded in
`docs/knowledge/capture-candidates.md`: that contract takes finished *products*
whose build has happened, and no frame has been cut. The first entries still
arrive after the first physical build, as that file says.

**What the next plan starts from:** a working `frame fields` / `frame set` loop
against the real files, `fields.yaml` as the spec, and `src/fcc/` holding the
domain-blind half. Roadmap Phase 2 (the HTTP layer) is unblocked; so is simply
picking up the calipers, which was the point.
