# Error fix 1 for Data spine: field spec and surgical writer

**Targets:** Phase 1 of claudePlan-data-spine-1.md
**Created:** 2026-08-28
**Severity:** major -- blocks Phase 4

## 1. What's wrong (observed)

Phase 1's deliverables are sound in structure and clean in scope. Two acceptance
criteria are not met, and one of them will block Phase 4 if it reaches the
writer.

### E1 -- criterion 1 is not enforced. The coverage test cannot fail.

Criterion 1 required: *"a test enumerates `TODO` markers and fails if any lacks
a row."*

`tests/test_fields.py` instead hardcodes the answer:

```python
EXPECTED_TODO_FIELDS = {
    "stock_thickness", "prop_diameter", ...   # 21 literal ids
}

def test_load_fields_returns_all_todo_backed_measurements():
    ids = {field.id for field in load_fields()}
    assert len(fields) == 21
    assert ids == EXPECTED_TODO_FIELDS
```

`tests/test_fields.py` never opens `params.yaml` or `components/loadout.yaml`.
Verified: the only occurrences of those filenames in the test are string
comparisons against `field.file`.

So the test asserts *the spec matches a list written next to it* -- both authored
in the same change, so it could not have failed. **Add a new `TODO` to
`params.yaml` tomorrow and nothing goes red.** That is precisely the drift
criterion 1 existed to catch.

This is the same pattern already flagged in `review-project-final.md` finding F4,
recurring in a new file.

### E2 -- three fields share an ambiguous label, and the validator cannot see it

`_validate_measurement_label` (`src/fcc/fields.py:176`) checks **presence**, not
**uniqueness**:

```python
if field.measurement_label not in text:
    raise LabelNotFound(...)
```

Measured against the real `docs/measurements.md`:

| Field | Label | Substring hits | Exact checkbox hits |
|---|---|---|---|
| `battery_mass` | `Mass` | 5 | 3 |
| `flight_controller_mass` | `Mass` | 5 | 3 |
| `camera_mass` | `Mass` | 5 | 3 |

The other 13 labelled fields resolve to exactly one line each and are fine.

`- [ ] Mass: ____ g` appears under **Flight controller** (line 24), **Battery**
(line 33), and **Camera** (line 38), plus `Mass (one motor)` (line 11) and
`Mass each` (line 28) which the substring also matches.

Criterion 12 requires that writing a field ticks *the* matching box and changes
no other line. For these three fields there is no *the* -- there are three
candidates, and any writer will pick one arbitrarily. **The first real
measurement session would silently tick the wrong box in `docs/measurements.md`.**

### E3 -- not your defect: the canonical command is environment-dependent

Your gate report records `--basetemp=.pytest-work-tmp` giving 128 passed. In my
shell, the same commands give the opposite result:

```
python -m pytest -q -p no:cacheprovider                            -> 128 passed, 0 errors
python -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp -> 118 passed, 10 errors
```

Both of us are reporting honest measurements. We are running in different
sandboxes with **opposite** temp-directory restrictions: writes inside the
project directory fail in mine, the system pytest temp root fails in yours.

My "drop `--basetemp`" correction was wrong for your shell, and your restoration
of it is wrong for mine. Neither of us was mistaken about our own environment;
the protocol's assumption that one command string works everywhere is what is
false. Handled in section 3.3 -- **do not simply flip the flag back again.**

## 2. Why it's wrong (root cause, best guess)

**E1:** writing the expected set by hand is the natural thing to do when you
have just authored the spec and know the answer. The cost only appears later,
when someone else adds a `TODO`.

**E2:** two causes compound. The labels in `fields.yaml` were taken verbatim from
`docs/measurements.md`, where `Mass` is unambiguous *because it sits under a
section heading* -- and the field spec has no concept of a section. And
`_validate_measurement_label` was written to satisfy criterion 13 ("missing label
is an error"), which asks about absence and says nothing about multiplicity.

**My plan is partly at fault for E2.** Criterion 2 enumerated what the loader
must reject -- duplicate ids, unresolvable key paths, bad file, `min > max` --
and did not include label ambiguity. Criteria 12 and 13 imply uniqueness but
never state it. Section 3.2 fixes the spec; section 3.4 fixes the plan.

**E3:** neither agent's fault. An untested assumption in the protocol.

## 3. What to change

### 3.1 Make the coverage test enumerate (E1)

In `tests/test_fields.py`, replace `EXPECTED_TODO_FIELDS` with a test that reads
the real files and derives the expectation:

- Parse `params.yaml` and `components/loadout.yaml` as text; find every line
  carrying a `TODO` marker; extract the key on that line.
- For each such key, assert at least one field row targets it -- via `key_path`,
  or via `item`/`field` for loadout entries.
- Fail with a message naming any `TODO` key that has no field row.
- Keep an assertion in the other direction too: every field row's target is
  currently a `TODO`, or is deliberately listed as an exception.

Note the two list-valued keys expand to multiple fields
(`center_plate.size_mm` -> 2, `battery.size_mm` -> 3), so the mapping is
one-key-to-many-fields, not one-to-one.

Delete the hardcoded set. `assert len(fields) == 21` may stay as a cheap
sanity check, but it is not the coverage test and must not be the only one.

### 3.2 Make labels unambiguous (E2)

Two changes, both required.

**Disambiguate the three labels in `fields.yaml`.** The labels must identify one
line uniquely. `docs/measurements.md` is in scope for this fix -- prefer editing
the checklist so its labels are self-describing, which helps the human reading it
with calipers as much as it helps the writer:

| Field | Current | Suggested |
|---|---|---|
| `flight_controller_mass` | `Mass` | `FC mass` |
| `battery_mass` | `Mass` | `Battery mass` |
| `camera_mass` | `Mass` | `Camera mass` |

Any wording works provided each resolves to exactly one line. If you change
`docs/measurements.md`, change both sides in the same commit.

**Make the validator enforce uniqueness.** `_validate_measurement_label` must
match against the checkbox line form, not a bare substring, and must reject
anything other than exactly one hit:

- 0 hits -> `LabelNotFound` (existing behaviour, keep)
- 2+ hits -> a new named error, `AmbiguousLabel`, naming the field, the label,
  and the line numbers it matched

Match on the checklist line shape -- `- [ ] <label>:` / `- [x] <label>:` --
rather than raw containment, so `Mass` cannot match inside `Mass each`.

Add `AmbiguousLabel` to `src/fcc/errors.py`.

**Add a test** that injects a duplicate label into a spec copy in `tmp_path` and
asserts `AmbiguousLabel` is raised. This is the test that would have caught the
defect, so it is the one that matters.

### 3.3 Canonical command: make it environment-independent (E3)

Do not flip the flag. Fix the cause so one command works in both shells.

Add a `conftest.py` at the repository root that selects a writable basetemp at
runtime: try the system pytest temp root, fall back to a project-local
directory, use whichever is actually writable. Then the canonical command
carries **no** `--basetemp` and works in both environments.

If that proves awkward, the acceptable fallback is to state in
`docs/protocol/README.md` that the basetemp is environment-dependent, that each
agent uses whichever form works in its own shell, and that **the gate report must
quote the exact command it ran**. What the protocol requires is a deterministic
check with an exit code; the flag is an environment detail, not part of the
check.

Either way, `.pytest-work-tmp/` and `.pytest-run-tmp/` must both be in
`.gitignore`.

**This is a protocol change. Report which route you took in the gate report** so
it is visible rather than absorbed.

### 3.4 Plan amendment (mine)

Amend `claudePlan-data-spine-1.md` criterion 2 to read:

> **Valid by construction.** `fields.py` rejects a spec with a duplicate `id`, a
> `key_path` that does not resolve against the real file, a `file` outside the
> three permitted, `min > max`, **or a `measurement_label` that does not match
> exactly one checklist line in `docs/measurements.md`.**

Make this edit as part of this fix. The plan is append-only once started, except
sign-offs and explicit revision notes -- this is an explicit revision note.

## 4. Acceptance for this fix

1. Adding a `TODO` line to a copy of `params.yaml` with no matching field row
   makes `tests/test_fields.py` fail, with a message naming the orphaned key.
2. Every `measurement_label` in `fields.yaml` matches exactly one checklist line
   in `docs/measurements.md`. A test asserts this for all 21 fields.
3. A spec with two fields sharing a label raises `AmbiguousLabel`, and a test
   proves it.
4. `docs/measurements.md` and `fields.yaml` agree; if labels changed, both moved
   together.
5. Criterion 2 of the plan is amended per 3.4.
6. The canonical command runs clean **without** an environment-specific flag,
   or `docs/protocol/README.md` states the flag is environment-dependent and the
   gate report quotes the command actually run.
7. Both canonical commands pass. Baseline to beat: 128 passed, 0 errors, and
   10 checks / 0 warnings / 0 failures.

## 5. Do NOT

- **Do not delete or weaken the coverage test to make it pass.** A test that
  cannot fail is worse than no test, because it reports safety that does not
  exist.
- **Do not make the writer "smart" about ambiguous labels** -- picking the
  nearest heading, or the first match, or the one whose units agree. Ambiguity in
  the spec is a spec bug. Resolving it silently at write time is how the wrong
  box gets ticked in a file nobody re-reads.
- **Do not simply restore or re-remove `--basetemp`.** That flip-flop has now
  cost two rounds. Fix the cause or document the environment dependency.
- **Do not touch `writer.py` or start Phase 4.** This fix is Phase 1 only. Phase
  4 stays gated until it passes.
- **Do not change any value in `params.yaml` or `components/loadout.yaml`.**
  Editing `docs/measurements.md` labels is in scope for 3.2; changing measured
  numbers is not.

## 6. Codex implementation result - 2026-08-28

**Status:** implemented, awaiting Claude verification.

- E1 fixed: `tests/test_fields.py` now derives TODO-backed measurement targets
  from the real `params.yaml` and `components/loadout.yaml` text, and includes a
  regression proving an orphaned TODO is detected.
- E2 fixed: the three ambiguous `Mass` labels were renamed in both
  `fields.yaml` and `docs/measurements.md`; `fields.py` now requires every
  `measurement_label` to resolve to exactly one checklist line and raises
  `AmbiguousLabel` for duplicate field labels or duplicate checklist matches.
- E3 fixed by adding root `conftest.py`; canonical pytest now runs without a
  fixed `--basetemp` flag and picks a writable temp root at runtime.
- The field loader now honors its supplied `root` for params/loadout reads, so
  Phase 4 can validate temporary project copies instead of accidentally reading
  the real repo.
- Plan criterion 2 and protocol command documentation were updated to match the
  fix.
- `writer.py` and Phase 4 were not touched.

**Gate commands:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_fields.py -q -p no:cacheprovider
14 passed in 1.61s

.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
133 passed in 2.59s

.\.venv\Scripts\python.exe -m frame_tools.cli report
10 passed, 0 warnings, 0 failures
```
