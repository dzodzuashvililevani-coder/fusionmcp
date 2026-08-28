# Error fix 3 for Data spine: field spec and surgical writer

**Targets:** Phase 4 of `claudePlan-data-spine-1.md` (criterion 4)
**Created:** 2026-08-28
**Severity:** major -- the load-bearing criterion is unmet, and its test cannot
detect the violation
**Scope:** `src/fcc/writer.py`, `tests/test_writer.py`, `src/fcc/README.md`,
this plan file

> **The writer logic is good.** I swept all 21 fields through `write_value`
> against byte-exact copies of the real project files. Every one addressed the
> correct line, wrote the correct value, round-tripped through `yaml.safe_load`,
> preserved the `#` count, and ticked the right checklist box -- including both
> lines that carry two checkboxes. Criteria 5-14 hold. **Do not rewrite the
> parser.** This fix is line endings and the test that should have caught them.

## 1. What's wrong (observed)

Criterion 4 says: *"After writing one value to `params.yaml`, exactly one line
differs from the original. Every other line is byte-identical."*

I copied the real project files byte-for-byte with `shutil.copy2` (no newline
translation) and wrote one value:

```
write_value(field_by_id("stock_thickness"), 2.7, root=<copy>)

WriteResult(file='params.yaml', line_number=11,
            old_text='  thickness_mm: 3.0          # TODO measure with caliper\n',
            new_text='  thickness_mm: 2.7          # TODO measure with caliper\n',
            checklist_ticked=True)

params.yaml:          67 of 68 raw lines differ in BYTES
                      CRLF before=67 after=0 | bare LF before=0 after=67
docs/measurements.md: 66 of 70 raw lines differ in BYTES
                      CRLF before=66 after=0 | bare LF before=3 after=69
components/loadout.yaml: UNCHANGED (bytes identical)
```

One value written; **every line in the file rewritten.** The working tree is
mixed on purpose and the writer flattens it:

```
params.yaml               CRLF=67  bare LF=0
components/loadout.yaml   CRLF=0   bare LF=16
docs/measurements.md      CRLF=66  bare LF=3
fields.yaml               CRLF=0   bare LF=275
```

`loadout.yaml` survives only because it is already LF. `params.yaml` and
`docs/measurements.md` are converted wholesale on every write.

### Why the test suite says this is fine

`tests/test_writer.py` cannot fail on this, for two independent reasons.

1. **The fixture launders the bytes.** `copy_project_data` (test_writer.py:18-26)
   copies with `read_text()` / `write_text()`. Both apply newline translation.
   The copy happens to come out CRLF on Windows, so the fixture *does* reproduce
   the defect -- but see 2.
2. **The comparison launders them back.** The `read()` helper
   (test_writer.py:40-41) uses `read_text()`, which collapses CRLF to LF on both
   sides before `changed_line_numbers` ever sees them. A wholesale CRLF-to-LF
   conversion is invisible to every assertion in the file.

So `test_scalar_write_changes_one_line_and_preserves_comment` passes while the
property it is named for is false. The plan said *"Write the byte-exactness test
first and let it drive the design"*; the test that exists is a
normalised-text-exactness test.

### Why `git diff` did not warn you

`core.autocrlf` is `true` in this repo, so git normalises on staging and reports
`1 file changed, 1 insertion(+), 1 deletion(-)` regardless. It does emit
`warning: in the working copy of 'params.yaml', LF will be replaced by CRLF the
next time Git touches it`. The gate report's `git diff --stat` was therefore
truthful and still could not surface this.

The practical damage: the user's editor shows a whole-file change, git nags on
every write, and the next checkout flips the file back to CRLF so the *next*
`frame set` rewrites all 67 lines again. Criterion 4 exists to make `frame set`
safe to run mid-build without producing a diff nobody can review. It does not
currently do that.

## 2. Why it's wrong (root cause -- verified, not guessed)

Read and write disagree about newline handling.

- `_read_target` (writer.py:121-122) calls `Path.read_text(encoding="utf-8")`.
  That opens with `newline=None`, which is *universal newline mode*: every
  `\r\n` in the file becomes `\n` in the returned string. The CR is gone before
  any parsing starts.
- `_atomic_write` (writer.py:160) opens with `newline=""`, which correctly
  performs no translation on write -- so the `\n`-only string is written out
  as `\n`-only bytes.

`newline=""` on the write side is right. `newline=None` on the read side is the
bug. The rest of the module is already CRLF-aware -- `_split_eol` handles
`\r\n`, and `_replace_measurement` uses `line.rstrip("\r\n")` -- so the machinery
is ready for line endings it is never actually given.

## 3. What to change

### 3.1 `src/fcc/writer.py` -- stop translating on read

Make the read side match the write side:

```python
def _read_target(root: Path, relpath: str) -> str:
    with _resolve_target(root, relpath).open(encoding="utf-8", newline="") as fh:
        return fh.read()
```

That is the whole fix. `splitlines(keepends=True)`, `_split_eol`,
`_replace_yaml_line_value`, and `_replace_measurement` all already carry the
line's own terminator through untouched, so a CRLF file stays CRLF, an LF file
stays LF, and a mixed file keeps each line as it found it.

Do not normalise, and do not pick a file-wide newline from the majority. Each
line keeps its own terminator. `docs/measurements.md` has three bare-LF lines
among 66 CRLF ones; after the fix it must still have exactly that.

### 3.2 `tests/test_writer.py` -- make the test able to fail

Byte-exactness is a claim about bytes. Test bytes.

- `copy_project_data` must copy verbatim: `shutil.copy2(ROOT / relpath, tmp_path / relpath)`.
  No `read_text` / `write_text` anywhere in the fixture.
- Add a `read_bytes` helper and compare with it. `changed_line_numbers` should
  split on `b"\n"` and compare `bytes`, so a changed terminator counts as a
  changed line.
- Add explicit terminator assertions to the scalar test and to a
  `docs/measurements.md` test:

  ```python
  assert after.count(b"\r\n") == before.count(b"\r\n")
  assert after.count(b"\n") == before.count(b"\n")
  ```

- Add one test that is not hostage to the repo's current state or to the host
  platform: build a small YAML fixture in `tmp_path` written with explicit
  `newline=""` in each of CRLF, LF, and mixed form, write a value into each, and
  assert only the target line's bytes changed. The three existing files could
  all become LF tomorrow; this test must still fail if `_read_target` regresses.
- The existing `read()` helper may stay for the assertions that are genuinely
  about text content (the `in after_measurements` substring checks), but every
  assertion that is about *what changed* moves to bytes.

**Prove the new test fails first.** Write the byte-level test, run it against
the current unfixed `writer.py`, and paste the failure into the gate report.
Then apply 3.1 and paste the pass. A test for a property that was already
silently violated is worth nothing until it has been seen to fail --
errorFix-1's E1 was accepted on exactly this standard.

### 3.3 `preview()` will change shape -- update its test

Once CRLF survives the read, `difflib.unified_diff` emits diff lines ending in
`\r\n`. The current assertions at test_writer.py:115-116 expect `...\n` and will
fail. Update them to match the file's real terminator rather than papering over
it by re-normalising inside `preview`. `preview` should show the diff of what
would actually be written.

### 3.4 `src/fcc/README.md` -- add the missing portal row

`writer.py` was added without a row. CLAUDE.md's rule is standing, not
phase-scoped: *"Every folder has a `README.md` with a portal table. Add a row
when you add a file."* Add:

```
| `writer____` | [writer.py](writer.py) | Python | Surgical single-line writes to params, loadout, and the checklist |
```

The Phase 7 README work in the plan stays as it is; this is the one row that
should have landed with the file.

### 3.5 Plan amendment -- criterion 24 vs Phase 7 (your open question, answered)

You were right that these conflict. Criterion 24 says no module under
`src/frame_tools/` may import `fcc`; the Phase 7 note says `cli.py` will. My
error. The intent of D10 is that the *domain core* stays independent of `fcc`,
not that the CLI does -- `cli.py` is the composition root and is the one place
allowed to depend on both sides.

**Criterion 24 is amended to:** *No module under `src/frame_tools/` other than
`cli.py` imports `fcc`. `cli.py` is the composition root and may import it. A
test enforces the exclusion by name, so a second module cannot quietly join it.*

Do not act on this in errorFix-3. `test_frame_tools_do_not_import_fcc_before_cli_phase`
stays exactly as it is until Phase 7, where it is renamed and given the `cli.py`
exemption. It is recorded here so Phase 7 starts from a plan that does not
contradict itself.

## 4. Acceptance for this fix

1. A byte-level test in `tests/test_writer.py` fails against the current
   `writer.py` and passes after the fix. Both outputs quoted in the gate report.
2. Writing one value to a byte-exact copy of the real `params.yaml` changes
   **exactly one line's bytes**, and `after.count(b"\r\n") == before.count(b"\r\n")`.
3. Same for `docs/measurements.md`, including its three bare-LF lines.
4. `components/loadout.yaml` stays pure LF -- no CR introduced. The fix must not
   trade one direction of the bug for the other.
5. Mixed / CRLF / LF synthetic fixtures all round-trip with their terminators
   intact.
6. `src/fcc/README.md` has the `writer____` row.
7. Canonical commands, unchanged and flag-free:

   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
   .\.venv\Scripts\python.exe -m frame_tools.cli report
   ```

   Zero failures, zero errors. `report` still `10 passed, 0 warnings, 0 failures`.
8. `.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider`
   passes -- no absolute local paths in anything you write into `docs/`.
9. No tracked data file's bytes changed by this work. `git status --short` shows
   only the four files in scope.

## 5. Do NOT

- **Do not normalise the repository instead of fixing the writer.** Adding
  `.gitattributes` with `* text=auto eol=lf`, or converting the three files to
  LF, would make the tests green while leaving the bug in place: `autocrlf=true`
  restores CRLF on the next checkout and the writer flattens it again. The
  writer must preserve whatever it is handed.
- **Do not keep comparing normalised text and call it byte-exact.** If the
  assertion goes through `read_text()`, it is not testing criterion 4.
- **Do not pick one newline for the whole file.** Per-line preservation, so the
  three bare-LF lines in `docs/measurements.md` stay bare LF.
- **Do not touch the parser, the refusal paths, the checklist matcher, or the
  atomic-write sequence.** All verified working. This is a read-mode fix and a
  test fix.
- **Do not widen scope to Phase 7.** No CLI, no `frame set`, no import-boundary
  change. Section 3.5 is a note for later, not work for now.
