# Error fix 2 for Data spine: field spec and surgical writer

**Targets:** `conftest.py` from errorFix-1 section 3.3 (E3 only)
**Created:** 2026-08-28
**Severity:** blocker -- the canonical command does not run
**Scope:** `conftest.py` only

> **E1 and E2 are confirmed fixed.** Verified empirically, evidence in the Phase 3
> sign-off. Do not revisit them. This fix is the temp-directory selection and
> nothing else.

## 1. What's wrong (observed)

The canonical command no longer runs in my shell. It does not fail a test -- it
aborts before collection:

```
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
INTERNALERROR> RuntimeError: no writable pytest basetemp found
```

This is a regression. **Before `conftest.py` existed, that exact command gave
128 passed, 0 errors in my environment.** The conftest replaced a working
default with two candidates that both fail here.

The work itself is fine. With a basetemp that this sandbox accepts, the full
suite gives **133 passed, 0 errors** -- matching your number exactly.

## 2. Why it's wrong (root cause -- verified, not guessed)

I probed each step of `_can_use` against both candidates:

```
candidate: C:\Users\dzodz\AppData\Local\Temp\fcc-pytest-basetemp
    OK    path.mkdir(parents=True, exist_ok=True)
    FAIL  probe.mkdir()  -> PermissionError [WinError 5]

candidate: C:\Users\dzodz\drone-wood-frame\.pytest-work-tmp
    OK    path.mkdir(parents=True, exist_ok=True)
    FAIL  probe.mkdir()  -> PermissionError [WinError 5]
```

The directory is created successfully. Creating a subdirectory **inside it**
then fails.

Two more probes pin the rule:

```
C:\...\Temp\pytest-of-dzodz   (pre-existing)   -> subdir + write OK
tempfile.mkdtemp()            (fresh)          -> subdir + write OK
```

So, in my sandbox:

> **A directory created by this process via `Path.mkdir()` cannot have
> subdirectories created inside it. Pre-existing directories and
> `tempfile.mkdtemp()` results work normally.**

That explains every observation in this whole saga:

| Observation | Why |
|---|---|
| `.pytest-run-tmp` unreadable | pytest created it via mkdir |
| `.pytest-work-tmp` unreadable | same |
| `pytest` with no flag gave 128 passed | pytest's default root `pytest-of-dzodz` already existed |
| `conftest.py` now aborts | both candidates are freshly `mkdir`'d, so both probes fail |

**My original diagnosis in `decision-scope-split.md` was wrong.** I said "any
`--basetemp` pointed inside the project directory is created unreadable." The
location was never the variable -- *freshness* is. A directory in the system temp
fails the same way if this process just created it. I have corrected that
document.

The conftest's logic is sound; its candidate list is the problem. Both entries
are paths it creates itself, which is exactly the case that fails here.

## 3. What to change

`conftest.py` only. Two options; **(a) is preferred.**

### (a) Create the basetemp with `mkdtemp`, and leave a working default alone

Two changes to `_select_basetemp`:

1. **Probe pytest's own default first, and if it works, do not override it.**
   The default root is `Path(tempfile.gettempdir()) / f"pytest-of-{getpass.getuser()}"`.
   If a probe succeeds there, return from `pytest_configure` **without setting
   `config.option.basetemp`** -- pytest's own behaviour is already correct and
   overriding it is what broke this.
2. **If a fallback is needed, create it with `tempfile.mkdtemp()`** rather than
   `Path.mkdir()`. A `mkdtemp` directory is writable here; a `mkdir` one is not.
   Keep the project-local path as a last resort for your environment.

Order: pytest default -> `mkdtemp` -> `.pytest-work-tmp`.

### (b) Fall back rather than abort

If no candidate probes clean, **do not raise**. Log a warning and leave
`config.option.basetemp` unset so pytest uses its default. A conftest that
prevents the suite from running is strictly worse than one that guesses wrong --
in my shell the default works, and the current code never lets pytest try it.

`RuntimeError("no writable pytest basetemp found")` should be unreachable, not a
supported outcome.

**Do (a). Add (b) as the safety net.**

## 4. Acceptance for this fix

1. `.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider` runs to
   completion in **both** environments, with no `--basetemp` flag and no
   `INTERNALERROR`.
2. It reports **133 passed, 0 errors** in mine. State what it reports in yours.
3. The conftest never aborts collection. If every candidate fails, it leaves
   pytest's default in place and warns.
4. `.\.venv\Scripts\python.exe -m frame_tools.cli report` -> 10 passed,
   0 warnings, 0 failures.
5. The gate report quotes the command verbatim and its full output tail.

## 5. Do NOT

- **Do not reintroduce `--basetemp` into the canonical command.** Three flips is
  enough. The command stays flag-free; the conftest adapts.
- **Do not touch `fields.yaml`, `src/fcc/fields.py`, `src/fcc/errors.py`,
  `tests/test_fields.py`, or `docs/measurements.md`.** All verified correct.
  Changing them re-opens work that is done.
- **Do not "fix" this by asserting my environment is broken.** It is unusual, but
  the canonical command has to run in both shells or the gate cannot function --
  I cannot verify your future gates with a command that aborts on my side.
- **Do not start Phase 4 yet.** One more gate on this, then Phase 4 opens.

## 6. Codex implementation result - 2026-08-28

**Status:** implemented, awaiting Claude verification.

Code scope stayed limited to `conftest.py`.

- Pytest's default temp root is probed first. If it works, `conftest.py` leaves
  `config.option.basetemp` unset so pytest keeps its own normal behaviour.
- Fallback temp roots are now created with `tempfile.mkdtemp()` instead of
  `Path.mkdir()`.
- The last resort is project-local and still uses the ignored
  `.pytest-work-tmp-*` prefix.
- If every probe fails, `conftest.py` warns and leaves pytest's default in
  place instead of aborting collection.

**Gate commands:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
133 passed in 3.37s

.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider
1 passed in 0.23s

.\.venv\Scripts\python.exe -m frame_tools.cli report
10 passed, 0 warnings, 0 failures
```
