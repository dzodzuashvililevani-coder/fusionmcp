# Data spine: field spec and surgical writer

**Plan:** claudePlan-data-spine-1.md
**Created:** 2026-08-28
**Source spec:** `docs/project/roadmap.md` Phase 1
**Status:** in-progress

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
   three permitted, or `min > max`.
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
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
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
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
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
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

Both must show zero failures **and zero errors** at every gate. Do not drop the
explicit `--basetemp` without re-testing. On this workstation the default
system pytest temp root is also unreadable, while the explicit
`.pytest-work-tmp` command above is the command that currently passes. See
`docs/brainstorming/decision-scope-split.md` for the earlier diagnosis and this
plan's gate report for the correction.

Baseline before this plan starts: **116 passed, 0 errors** and
**10 checks, 0 warnings, 0 failures**.

## 7. Sign-off log

_No gate reports yet. Codex appends here._
