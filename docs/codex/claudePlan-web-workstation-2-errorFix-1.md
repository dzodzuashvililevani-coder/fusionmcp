# Error fix 1 for Web measurement workstation

**Targets:** Phase 1 of `claudePlan-web-workstation-2.md`
**Created:** 2026-08-28
**Severity:** major — one silent duplication the plan explicitly asked you to
disclose, and one instruction that does not work
**Scope:** `src/fcc/fields.py`, `src/fcc/writer.py`, `src/fcc/api/`,
`src/frame_tools/cli.py`, `tests/`, this plan file

> **The API is good.** I exercised it end to end against a byte-exact copy: the
> write endpoint changed exactly one line of `params.yaml` and one of
> `docs/measurements.md`, preserved every CRLF and every `#`, and returned the
> full report in the same response. Traversal attempts 404 structurally. The
> `frame_tools` boundary holds. Criteria 1-14 are behaviourally met.
> **Do not redesign anything.** This fix removes a duplication and repairs a
> false instruction.

## 1. What's wrong (observed)

### E1 — three copies of the same logic, and the gate report does not mention it

`src/fcc/api/routes.py` lines 124-193 reimplement, near-verbatim, four helpers
that already exist in `src/frame_tools/cli.py`:

| `routes.py` | `cli.py` | Also in |
|---|---|---|
| `_coerce_value` | `_coerce_value` | `writer._format_value` — **third copy** |
| `_is_todo` | `_is_todo_guess` | |
| `_measurement_ticked` | `_measurement_is_ticked` | |
| `_target_line` | `_target_line` | `writer._replace_params_value` / `_replace_loadout_value` locate the same line **exactly**, as their primary job |

Phase 1's "Notes for the implementer" said:

> *Reuse `fcc.fields.current_value` and the `_is_todo_guess` logic that `cli.py`
> already has. If that logic needs to be shared rather than duplicated, move it
> into `fcc/fields.py` — **and say so in the gate report**, since section 2
> forbids editing that file without a decision.*

Neither happened. The logic was duplicated, and the gate report's open questions
list four other deviations honestly while omitting this one.

**They agree today.** I checked all 21 fields, both properties, in both
implementations:

```
status: API vs `frame fields`   -> disagreements: none (21/21 agree)
line numbers: API vs writer     -> mismatches:    none (21/21 agree)
```

**That is the problem, not the reassurance.** Two implementations that agree by
coincidence of authorship, with no test tying them together, in a repository
whose stated rule is *"geometry is solved exactly once"* and whose Phase 1
report says the project's characteristic failure is a test that cannot fail.
Phase 4 builds a UI on top of one of these copies. `frame fields` and the
browser can start disagreeing about whether a value is measured, and nothing
will notice.

The line-number case is the sharpest. `_target_line` finds a line by re-parsing
the file, then `_field_line` searches for the first line whose text is equal to
it. `writer._replace_params_value` already locates that exact line by index, as
its primary job, and is the thing whose answer actually matters — it is the code
that performs the write. Two answers to "which line is this field on", and the
authoritative one is not the one the API reports.

### E2 — the "regenerate" instruction does not regenerate

`src/fcc/api/app.py` stamps every schema with:

```
Generated, do not edit. Regenerate with
.\.venv\Scripts\python.exe -m pytest tests\test_api_contract.py -q -p no:cacheprovider
```

That command does not regenerate anything. `tests/test_api_contract.py` only
compares:

```python
def test_openapi_snapshot_matches_live_app():
    expected = json.loads((ROOT / "web" / "src" / "openapi.json").read_text(...))
    assert live_schema() == expected
```

I grepped the whole repository: **nothing writes `web/src/openapi.json`.** There
is no regeneration path.

So the failure mode is: you change a Pydantic model, the contract test fails
correctly, you run the command the file itself tells you to run, it fails again
with the same message, and your only remaining option is to hand-edit a file
whose first line says *do not edit*.

Criterion 16 requires the header to name **the command that regenerates them**.
This one names a command that cannot.

## 2. Why it's wrong (root cause)

**E1** is partly my plan's fault and I am fixing my half in section 3.4. Section
2 says "stop and report" for changes to `fcc/fields.py`; the Phase 1 note says
"move it into `fcc/fields.py` and say so". Those pull in opposite directions,
and duplication was the path that violated neither prohibition. **This error-fix
is the decision that authorises the edit** — that is what the mechanism is for.
What remains squarely on the implementation side is the silence: the plan named
this exact situation and asked for a line in the gate report.

**E2** looks like a header written from intent rather than from a command that
was run. Nobody executed the instruction the file gives.

## 3. What to change

### 3.1 `src/fcc/writer.py` — expose the locator that already exists

Add one public function beside `write_value` / `preview` / `tick_measurement`:

```python
def locate(field: FieldSpec, root: Path | None = None) -> tuple[int, str]:
    """Return the 1-based line number and full text of the line this field addresses."""
```

Implement it by reusing the existing `_replace_params_value` /
`_replace_loadout_value` finders — the same code that performs a write. Do not
write a third finder. Raise `UnsurgicalEdit` for a field it cannot address,
exactly as a write would.

**This is the point of the fix:** the line number the API reports becomes, by
construction, the line the writer will actually edit.

### 3.2 `src/fcc/fields.py` — one home for field status and coercion

Add:

```python
def coerce_value(field: FieldSpec, value: str | int | float) -> int | float:
def is_todo_guess(field: FieldSpec, root: Path | None = None) -> bool:
```

Move the bodies from `cli.py`; keep the behaviour **byte-identical**, including
the `# TODO` fallback for the five fields with no `measurement_label`. Phase 1's
14 `test_fields.py` tests and the CLI tests are your regression net — if any of
them change, you have changed behaviour, which this fix does not authorise.

`writer._format_value` stays as it is. It formats *for writing*; `coerce_value`
parses *user input*. They are allowed to remain separate, but `coerce_value`
must be the only parser the CLI and the API use.

### 3.3 Delete the copies

- `src/fcc/api/routes.py`: delete `_coerce_value`, `_is_todo`,
  `_measurement_ticked`, `_target_line`, `_field_line`. Call `fields.coerce_value`,
  `fields.is_todo_guess`, and `writer.locate`.
- `src/frame_tools/cli.py`: delete `_coerce_value`, `_is_todo_guess`,
  `_measurement_is_ticked`, `_target_line`. Call the same three.
- `_group()` stays in `routes.py`. It is presentation, it has no second copy,
  and it is not worth moving.

### 3.4 A test that makes the two surfaces agree by proof, not by luck

New test — put it in `tests/test_boundaries.py`, beside the other cross-surface
checks. For **every one of the 21 fields**, assert that `frame fields` and
`GET /api/fields` report the same `status` and the same line number, against the
same temp project.

Parametrise per field so a failure names the field. This is the test whose
absence is the actual defect; write it and watch it fail against the current
duplicated code first, then make it pass.

### 3.5 A regeneration command that exists

Add a real entry point that **writes** `web/src/openapi.json`. Your choice of
shape; it must satisfy all four:

1. It is runnable as a single command on Windows PowerShell.
2. Its output is byte-identical to what `test_api_contract.py` compares against
   — same JSON serialisation, same key order, same trailing newline, same line
   endings. If the test compares parsed JSON, it must **also** compare raw bytes,
   or the regeneration is only approximately right.
3. `GENERATED_HEADER` names **that** command.
4. A test runs the regeneration into a temp path and asserts the result equals
   the committed file. The named command is then proven, not asserted.

The obvious shape is a `__main__` in a small module — for example
`python -m frame_tools.report_api --write-openapi` — since schema generation
needs a report provider and `frame_tools` is where that lives. Do not add a
`frame` subcommand for this; `frame ui` is Phase 7's and this is a developer
tool, not a user one.

### 3.6 Not in scope for this fix

- Do not touch `fcc/errors.py` or `fields.yaml`.
- Do not change any endpoint's URL, status code, or payload shape. The contract
  snapshot should come out of this fix **unchanged**; if `openapi.json` changes,
  something drifted and you should say so in the gate report.
- Do not start Phase 4.

## 4. Acceptance for this fix

1. `grep -c "_target_line\|_is_todo\|_coerce_value" src/fcc/api/routes.py
   src/frame_tools/cli.py` finds **no definitions** of these in either file —
   only calls into `fcc`.
2. The new cross-surface test fails against the current code and passes after
   the fix. **Quote both outputs in the gate report.**
3. All 21 fields agree on status and line between `frame fields` and
   `GET /api/fields`.
4. `web/src/openapi.json` is **byte-identical** to its current committed
   content. `git diff -- web/src/openapi.json` is empty.
5. The regeneration command runs, writes the file, and a test proves its output
   matches the committed one.
6. Every Phase 1 test still passes **unmodified** — `test_fields.py`,
   `test_writer.py`, `test_boundaries.py`'s existing cases, `test_api.py`. If you
   had to edit an existing assertion, behaviour changed; stop and report.
7. Canonical commands, flag-free:

   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
   .\.venv\Scripts\python.exe -m frame_tools.cli report
   ```

   Zero failures, zero errors. The external `StarletteDeprecationWarning` may
   remain; see section 5.
8. `.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider`
   passes.
9. `git diff -- params.yaml components/loadout.yaml docs/measurements.md
   fields.yaml` is empty.

## 5. Do NOT

- **Do not suppress the `StarletteDeprecationWarning`** with a `filterwarnings`
  entry. It is external, it is honest, and hiding it sets the precedent that
  warnings get muted rather than read. Leaving it visible is the correct
  outcome for now. If you want it gone, the fix is a dependency change with its
  own reasoning — not a filter.
- **Do not "fix" E1 by having `fcc/api/` import `frame_tools.cli`.** That
  inverts W1 and is worse than the duplication.
- **Do not make `writer.locate` a fourth finder.** If you find yourself writing
  new line-searching code, you have missed the point of 3.1.
- **Do not change behaviour while de-duplicating.** Identical results, one
  implementation. If the CLI and the API genuinely differ somewhere today, say
  so in the gate report rather than picking a winner silently.
- **Do not touch `web/` beyond nothing.** The frontend is Phase 4.
