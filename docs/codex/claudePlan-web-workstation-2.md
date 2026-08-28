# Web measurement workstation: API, UI, and `frame ui`

**Plan:** claudePlan-web-workstation-2.md
**Created:** 2026-08-28
**Source spec:** `docs/project/roadmap.md` Phase 2; `docs/brainstorming/idea-web-workstation.md`
**Supersedes:** `claudePlan-web-workstation-1.md` — written 2026-08-27, status
`ready-for-revision`, never implemented. See section 0.1.
**Visual spec:** https://claude.ai/code/artifact/b3cf5d12-bae1-4dbf-b289-597e83115822
**Status:** ready-for-implementation

> **This is roadmap Phase 2.** Phase 1 (the data spine) is complete and verified:
> `fcc.fields` loads the spec, `fcc.writer` performs surgical writes, and
> `frame fields` / `frame set` already work from the terminal. **This plan puts a
> browser in front of that machinery. It does not rebuild any of it.**

---

## 0. Preconditions

Confirm all five before Phase 1. If any fails, stop and report.

| # | Precondition | Check |
|---|---|---|
| P0.1 | Canonical commands pass | Both commands in section 8 run clean |
| P0.2 | Working tree committed | `git status --short` is empty |
| P0.3 | Phase 1 signed off | `claudePlan-data-spine-1.md` status is `complete - all phases verified` |
| P0.4 | Node toolchain present | `node --version` and `npm --version` both succeed |
| P0.5 | Visual spec read | Open the artifact linked above before Phase 4 |

P0.4 was checked on 2026-08-28: **Node v24.16.0, npm 11.13.0**. `pnpm` is not
installed. See decision W3.

### 0.1 Why plan 1 is superseded rather than revised

`claudePlan-web-workstation-1.md` conflicts with the repository in three ways
that a revision note cannot patch:

1. It plans to create `src/frame_tools/fields.py` and
   `src/frame_tools/writer.py`. Both now exist **in `src/fcc/`**, built and
   verified in Phase 1. Following plan 1 would rebuild Phase 1 in the wrong
   package and violate D10.
2. It specifies stdlib `http.server` and hand-written `web/app.js` +
   `web/style.css`. `architecture.md` **D4** since chose FastAPI + uvicorn and
   **D5** chose Vite + React + TypeScript, explicitly reversing plan 1's
   reasoning.
3. Its P0 section describes a `.pytest-run-tmp/` permission blocker that
   `conftest.py` resolved in `errorFix-2`.

**Action for the implementer:** set plan 1's `Status:` line to
`superseded-by-claudePlan-web-workstation-2` in Phase 1 of this plan. Change
nothing else in that file; it stays as a record.

---

## 1. Goal (<= 3 sentences)

Put a local browser UI in front of the Phase 1 data spine: a FastAPI server on
`127.0.0.1` exposing the field spec, the design report, and a write endpoint,
and a Vite + React + TypeScript page with the measurement form beside a live
report panel. Every field name, unit, range, question, and check message comes
from the server at runtime; none is written into the TypeScript. No 3D, no
photos, no chat, no outbound network call.

---

## 2. Out of scope

- **3D component models, dimension animation, WebGL, react-three-fiber.** That
  is roadmap Phase 7. The layout reserves a slot for it (criterion 27) and
  nothing more.
- **Photo upload, HEIC conversion, EXIF handling.** Roadmap Phase 4.
- **In-page chat, AI features, and any outbound network call whatsoever.** D13
  defers these. The page must work with the machine offline.
- **Any change to `geometry.py`, `mass.py`, `thrust.py`, `validate.py`,
  `fusion.py`, `dxf_out.py`, `params.py`.** The UI reads their output and never
  recomputes a dimension.
- **Any change to `fcc/fields.py`, `fcc/writer.py`, `fcc/errors.py`,
  `fields.yaml`.** Phase 1 is verified. If the API needs something they do not
  expose, **stop and report** rather than editing them — that is an error-fix
  decision, not an implementation one.
- **Changing any committed value** in `params.yaml`, `components/loadout.yaml`,
  or `docs/measurements.md`. Only the user changes those, at runtime.
- **The five permanently-`[TODO guess]` fields.** Known Phase 1 limitation,
  recorded in the Phase 1 report. The UI displays whatever status the server
  reports and does not work around it.
- **Authentication, multi-user, any bind address other than `127.0.0.1`,
  HTTPS, CORS.**
- **`docs/project/architecture.md`.** Claude reconciles it at Phase 9. Do not
  edit it.
- **ruff.** D14 proposes it; adopting it is its own change, not a rider on this one.
- Playwright / end-to-end tests. D14 lists them; they arrive with Phase 3's real
  usage, when there is a flow worth recording.

---

## 3. Files in scope

Anything not on this list is OFF-LIMITS unless an error-fix or revision says
otherwise.

```
pyproject.toml                            add [web] extra and httpx to [dev]
.gitignore                                add node_modules/ and web/dist/

src/fcc/api/__init__.py          (new)
src/fcc/api/app.py               (new)    app factory + report-provider injection
src/fcc/api/models.py            (new)    Pydantic models: the whole API contract
src/fcc/api/routes.py            (new)    the five endpoints
src/fcc/api/README.md            (new)    required by test_structure
src/frame_tools/report_api.py    (new)    the drone-side report provider
src/frame_tools/cli.py                    add the `ui` subcommand

web/README.md                    (new)
web/package.json                 (new)
web/package-lock.json            (new)    committed; npm, see W3
web/tsconfig.json                (new)
web/vite.config.ts               (new)
web/index.html                   (new)
web/src/README.md                (new)    required by test_structure
web/src/main.tsx                 (new)
web/src/App.tsx                  (new)
web/src/api.ts                   (new)    typed fetch wrappers
web/src/api.d.ts                 (new)    GENERATED. Never hand-edit
web/src/openapi.json             (new)    GENERATED contract snapshot. Never hand-edit
web/src/FieldQueue.tsx           (new)
web/src/FieldCard.tsx            (new)
web/src/ReportPanel.tsx          (new)
web/src/styles.css               (new)

tests/test_api.py                (new)    endpoint behaviour
tests/test_api_contract.py       (new)    schema drift
tests/test_web_source.py         (new)    no domain literals in TypeScript
tests/test_structure.py                   add TypeScript + CSS to DATA_TYPES
CLAUDE.md                                 portal rows, commands, data vocabulary
README.md                                 folder row and workflow
docs/codex/claudePlan-web-workstation-1.md    status line only
```

**`web/` stays two directories deep on purpose.** Every directory in the
repository needs a `README.md` with a `**Purpose:**` line and a `## Portals`
table, enforced by `test_structure.py`. `node_modules` is already in that test's
skip list; `web/` and `web/src/` are not, so both need one. Do **not** create
`web/src/components/` — put components directly in `web/src/` and avoid a third
index to maintain.

---

## 4. Decisions this plan makes

`architecture.md` settles the stack. These are the gaps it leaves. They are
decisions, not suggestions — implement them as written or raise an error-fix.

### W1 — `fcc/api/` must not import `frame_tools`. The report arrives by injection.

This is the load-bearing architectural decision in the plan.

`src/fcc/` is declared domain-blind (D10), and roadmap Phase 8 exists to prove
it: *"extracting `fcc/` into its own repository would be a move, not a rewrite."*
But the UI's whole value is showing the **drone report** — geometry, mass,
thrust, and the ten checks — all of which live in `frame_tools`.

The naive resolution is `fcc/api/routes.py` importing `frame_tools.validate`.
**Do not do that.** It would make the API permanently drone-shaped and turn
Phase 8 into a rewrite.

Instead, `fcc.api.app.create_app()` takes a **report provider**: a callable
returning a `Report` model. `frame_tools/report_api.py` supplies the drone one,
and `frame_tools/cli.py` wires them together at startup — the same composition
root that already wires `fcc` into the CLI:

```python
# src/fcc/api/app.py
def create_app(report_provider: Callable[[], Report], root: Path) -> FastAPI: ...

# src/frame_tools/report_api.py
def build_report() -> Report:            # imports geometry, mass, thrust, validate
    ...

# src/frame_tools/cli.py
app = create_app(report_provider=build_report, root=params.project_root())
```

A test asserts nothing under `src/fcc/api/` imports `frame_tools` (criterion 24).

**Known debt, not this plan's job:** `fcc/fields.py` and `fcc/writer.py` already
import `frame_tools.params.project_root`. That predates this plan, was accepted
at Phase 3 sign-off, and belongs to roadmap Phase 8. **Do not fix it here, and
do not add a second instance of it.**

### W2 — The diff preview is a server call, not client-side string splicing.

The visual spec shows the exact `-`/`+` lines updating as you type. The
tempting implementation splices the line in TypeScript. That duplicates
`fcc.writer`'s line-editing logic in a second language, in a second place,
with no test tying them together — the exact failure D9 exists to prevent.

`POST /api/fields/{id}/preview` calls `fcc.writer.preview()` and returns the
diff. The client debounces at **250 ms**. It is a localhost round trip on a
millisecond-scale solver; the cost is irrelevant and the guarantee is that the
preview shows what the writer will actually do.

### W3 — npm, not pnpm.

D14 prefers pnpm and permits npm ("acceptable if you prefer one less tool").
npm 11.13.0 is already installed; pnpm is not. Use npm, commit
`package-lock.json`. One fewer tool to install on a machine that already has
Windows Application Control blocking unsigned shims.

### W4 — The contract snapshot is JSON, checked by Python.

D9 requires that committed types cannot drift from the server. Node may not be
present in every environment that runs the suite, and a drift test that silently
skips is the "test that cannot fail" failure this project has already hit twice.

So the guarantee is split:

- **`web/src/openapi.json`** is committed. `tests/test_api_contract.py`
  regenerates the schema from the FastAPI app in pure Python and fails if it
  differs. **This test never skips.** It catches the actual risk — a changed
  Pydantic model.
- **`web/src/api.d.ts`** is generated from that JSON by
  `npm run gen:types`. A second test checks it is current, and **skips with a
  clear reason when Node is absent.**

The Python test is the gate. The Node test is the convenience.

### W5 — Stale-file detection, minimum viable.

D15: *"you will edit `params.yaml` in VS Code while the UI holds a stale copy.
Handled by watching file mtimes and warning on conflict, not by locking the user
out of their own files."*

`GET /api/fields` returns a `revision` string — the modification times of the
three data files, hashed. `POST /api/fields/{id}/value` accepts that revision
and returns **409** with the current values if the files changed underneath.
The UI shows "the files changed outside the app — reload before saving" and a
reload button. No locking, no polling, no watcher.

### W6 — `unit` stays a plain string in the Pydantic models.

Do not model `unit` as an `Enum` or `Literal`. An enum would emit
`"mm" | "g" | "deg" | "count"` into the generated `api.d.ts`, which would put
domain units into the TypeScript and fail criterion 22 — correctly, because a
second project's units would then require a schema change.

---

## 5. Acceptance criteria

Every criterion is observable from outside the code.

### The API

1. **`GET /api/fields`** returns all 21 fields, each with `id`, `question`,
   `unit`, `min`, `max`, `file`, `line`, `current_value`, `status`
   (`measured` | `todo`), `measurement_label`, and `group`. Sourced from
   `fcc.fields`; no field data is defined in the API layer.
2. **`GET /api/report`** returns `headline` (a list of `{label, value, unit}`),
   and `checks` (a list of `{status, name, detail}`) with `status` in
   `ok` / `warn` / `fail`. `name` and `detail` are **verbatim** from
   `validate.py` — the API adds no wording of its own.
3. **`POST /api/fields/{id}/preview`** returns the unified diff a write would
   produce, from `fcc.writer.preview()`, and **writes nothing**. A test asserts
   the three data files are byte-identical after a preview call.
4. **`POST /api/fields/{id}/value`** writes through `fcc.writer.write_value`,
   ticks the checklist, and returns the `WriteResult` fields plus a freshly
   built report — **one round trip, one response.** Roadmap exit criterion 1.
5. **A value that fails validation is still written**, returns HTTP **200**, and
   the response carries the failing check's `name` and `detail` verbatim.
   Roadmap exit criterion 2, and the same rule `frame set` already follows.
6. **An out-of-range value** is written and flagged in a `warnings` list. Not
   rejected.
7. **Unknown field id** returns **404** with the message from `fcc.fields`'
   `SpecError`, listing valid ids.
8. **A non-numeric value** returns **422** and writes nothing.
9. **Stale revision** returns **409** with the current values, and writes
   nothing (W5).
10. **`GET /api/health`** returns `{"ok": true}` and the project root path. Used
    by `frame ui` to confirm the server is up before opening a browser.
11. **No endpoint accepts a filesystem path, filename, or directory in its
    signature.** Path traversal is refused *structurally*, not by filtering: the
    write endpoint takes a field id, and the target file comes from
    `fields.yaml`. A test inspects the OpenAPI schema and fails if any parameter
    or body field name matches `path`, `file`, `filename`, `dir`, or `root`.
    Roadmap exit criterion 4.
12. **The app binds `127.0.0.1` only.** A test asserts the value `frame ui`
    passes to uvicorn, and that no CORS middleware is installed.
13. **The API imports nothing from `frame_tools`.** A test greps
    `src/fcc/api/*.py`. See W1.

### The contract

14. **`web/src/openapi.json` matches the live app.** `tests/test_api_contract.py`
    regenerates it in Python and fails on any difference. **This test never
    skips.** Roadmap exit criterion 5.
15. **`web/src/api.d.ts` matches `openapi.json`.** Checked by regenerating with
    `npm run gen:types`; skipped with an explicit reason if Node is missing.
16. **Both generated files carry a "generated, do not edit" header** naming the
    command that regenerates them.

### The UI

17. **The form is built entirely from `GET /api/fields`.** Adding a row to
    `fields.yaml` makes a new input appear with no TypeScript change. A test
    proves the mechanism: it renders the field list from a fixture containing an
    invented field and asserts it appears.
18. **Entering a value and saving changes the file on disk and updates the
    report in one round trip.** Roadmap exit criterion 1.
19. **The live diff preview** shows the exact `-`/`+` lines from the server
    (W2), including the trailing comment, plus the `docs/measurements.md`
    checklist line where the field has one.
20. **A failing value still saves**, and the failing check's text appears
    verbatim as received. Roadmap exit criterion 2.
21. **The report panel renders whatever the server sends** — no check name,
    threshold, or message text exists in the TypeScript.
22. **No domain literal appears anywhere in `web/src/`.** `tests/test_web_source.py`
    reads `fields.yaml` and fails if any field `id`, `question`,
    `measurement_label`, `unit`, `min`, or `max` value appears in any `.ts`,
    `.tsx`, or `.css` file under `web/src/`, **including the generated
    `api.d.ts`** — no exclusions. Roadmap exit criterion 3.
23. **The three panes match the visual spec**: field queue, current measurement,
    design state. Palette, type scale, spacing, and component states as
    published. Deviations are allowed but must be listed in the gate report with
    a reason.
24. **Both themes render correctly**, following the token pattern in the spec:
    a complete light palette on bare `:root`, tokens redefined under
    `@media (prefers-color-scheme: dark)` guarded by
    `:root:not([data-theme="light"])`, and again under `:root[data-theme="dark"]`.
    No color defined only inside a media or `[data-theme]` block.
25. **Keyboard operable end to end**: tab reaches every control, Enter saves,
    focus is always visible. Measuring is a two-hands-busy activity.
26. **The page works offline.** No font CDN, no external asset, no analytics.
    Self-host or use system fonts. A test greps `web/src/` and `web/index.html`
    for `http://` and `https://`.
27. **A reserved, labelled slot exists** where the Phase 7 component viewer
    goes, so the layout is not rebuilt later.

### The command

28. **`frame ui`** starts uvicorn on `127.0.0.1`, waits for `/api/health`, and
    opens a browser. `--no-browser` and `--port N` are supported.
29. **`frame ui` with no build present** exits non-zero with the exact command
    to run (`npm --prefix web install && npm --prefix web run build`). It does
    not fail with a stack trace or serve a blank page.
30. **`frame ui --help` and every existing subcommand still work.** The new
    dependency is optional: `import fastapi` failing produces a clear
    "install the web extra" message, and **`frame report`, `frame check`,
    `frame fields`, and `frame set` keep working with the `[web]` extra
    uninstalled.** A test proves the CLI imports cleanly without FastAPI.

### Repo health

31. **`web/README.md` and `web/src/README.md` and `src/fcc/api/README.md`** each
    have a `**Purpose:**` line and a `## Portals` table.
32. **The data-type vocabulary gains `TypeScript` and `CSS`** in both
    `CLAUDE.md`'s table and `tests/test_structure.py`'s `DATA_TYPES` set, and
    CLAUDE.md's line *"There is no JavaScript in this project"* is replaced with
    what is now true. Without this, every new README fails
    `test_readme_uses_known_data_types`.
33. **`.gitignore` covers `node_modules/` and `web/dist/`.** `node_modules` is
    already skipped by `test_structure.py` but is **not** gitignored today.
34. **Indexes updated:** `CLAUDE.md` gains portal rows for `web/` and
    `src/fcc/api/` plus the `frame ui` command; `README.md` gains a folder row
    and the command.
35. **Canonical commands clean.** Both commands in section 8 pass with zero
    failures and zero errors.
36. **No tracked data file changed.** `git diff -- params.yaml
    components/loadout.yaml docs/measurements.md fields.yaml` is empty at every
    gate.

---

## 6. Phases

### Phase 1: implement — the API

**Definition of done:**

- `pyproject.toml` gains `web = ["fastapi>=0.115", "uvicorn>=0.30", "pydantic>=2.7"]`
  and `httpx>=0.27` in `[dev]` (FastAPI's `TestClient` requires it).
- `src/fcc/api/models.py` defines every payload as a Pydantic model. These
  models *are* the API contract — nothing is returned as a bare dict.
- `src/fcc/api/app.py` exposes `create_app(report_provider, root)` per W1.
- `src/fcc/api/routes.py` implements the five endpoints of criteria 1-10.
- `src/frame_tools/report_api.py` builds the `Report` from `geometry`, `mass`,
  `thrust`, and `validate`, including the four headline values shown in the
  visual spec: arm radius, all-up weight, thrust-to-weight, CG offset.
- `src/fcc/api/README.md` exists.
- `tests/test_api.py` covers criteria 1-13 against `TestClient`, on **byte-exact
  copies** of the data files in `tmp_path`. No test touches the real files.
- `tests/test_api_contract.py` covers criterion 14 and writes the first
  `web/src/openapi.json`.
- Plan 1's status line is set to `superseded-by-claudePlan-web-workstation-2`.

**Touches:** `pyproject.toml`, `src/fcc/api/*`, `src/frame_tools/report_api.py`,
`tests/test_api.py`, `tests/test_api_contract.py`, `web/src/openapi.json`,
`docs/codex/claudePlan-web-workstation-1.md`

**Notes for the implementer:**

- **Write the "API does not import frame_tools" test first** and let it
  constrain the design, exactly as criterion 4 drove Phase 1's writer. It is
  much cheaper than discovering the coupling at the gate.
- Reuse `fcc.fields.current_value` and the `_is_todo_guess` logic that
  `cli.py` already has. If that logic needs to be shared rather than duplicated,
  move it into `fcc/fields.py`— **and say so in the gate report**, since section
  2 forbids editing that file without a decision.
- `writer.write_value` raises `FccError` subclasses. Map each to a status code
  deliberately: `SpecError` → 404, `UnsurgicalEdit` → 409, `PathRefused` → 400,
  `LabelNotFound` / `AmbiguousLabel` → 500 (a spec bug, not a user error).
- Do not add a `/api/params` or any endpoint that returns raw file contents. The
  API's surface is fields, report, preview, write, health. Nothing else.

### Phase 2: gate — API verified

**Definition of done:** gate report appended, then halt
**Touches:** this plan file only
**Commands to run:**

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_api.py tests\test_api_contract.py -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
git diff --stat
git diff -- params.yaml components/loadout.yaml docs/measurements.md fields.yaml
```

**Status report sections:** commit SHA, files changed, test output,
self-assessment, open questions. State explicitly whether anything under
`src/fcc/` outside `api/` had to change, and why.

### Phase 3: verify — API

**Definition of done:** Claude runs the canonical commands, exercises the write
endpoint end to end against a byte-exact copy and byte-diffs the result,
confirms the `frame_tools` import boundary, then appends PASS or writes
`claudePlan-web-workstation-2-errorFix-1.md`.

### Phase 4: implement — the React workstation

**Definition of done:**

- `web/` scaffolded with Vite + React + TypeScript; `npm --prefix web install`
  and `npm --prefix web run build` both succeed and `package-lock.json` is
  committed.
- `npm run gen:types` produces `web/src/api.d.ts` from `web/src/openapi.json`.
- `vite.config.ts` proxies `/api` to the uvicorn port in dev; `vite build`
  outputs to `web/dist`.
- `App.tsx` composes the three panes; `FieldQueue`, `FieldCard`, and
  `ReportPanel` implement the visual spec (criterion 23).
- `styles.css` implements the token system of criterion 24.
- Criteria 17-27 met.
- `tests/test_web_source.py` covers criteria 22 and 26.
- `.gitignore`, `tests/test_structure.py` DATA_TYPES, and the three new READMEs
  are updated — criteria 31-33. **Do this first in the phase, not last:** the
  suite fails the moment `web/` exists without them.

**Touches:** everything under `web/`, `tests/test_web_source.py`,
`tests/test_structure.py`, `.gitignore`

**Notes for the implementer:**

- **The visual spec is a spec, not a suggestion.** Palette, type scale, spacing,
  and the three-pane layout come from it. Where the browser makes something
  impossible or ugly, deviate — and list every deviation in the gate report.
- The spec is a static mockup: its interactivity is illustrative. The real
  behaviour is criteria 17-21.
- Keep state simple. This is one page with one selected field; TanStack Query
  appears in `architecture.md`'s diagram but is not required by this plan and
  should not be added without a reason in the gate report.
- `api.ts` is the only file that calls `fetch`. Components receive typed data.

### Phase 5: gate — UI verified

**Definition of done:** gate report appended, then halt
**Touches:** this plan file only
**Commands to run:** as Phase 2, plus:

```powershell
npm --prefix web install
npm --prefix web run build
npm --prefix web run gen:types
git status --short
```

Report explicitly: every deviation from the visual spec and why; whether both
themes were checked; whether `web/dist` and `node_modules` are correctly ignored.

### Phase 6: verify — UI

**Definition of done:** Claude builds the frontend, starts the server, enters a
real value in a browser against a copied project, byte-diffs the result,
confirms the report updated in one round trip, checks both themes and keyboard
operation, then appends PASS or writes an error-fix.

### Phase 7: implement — `frame ui` and the indexes

**Definition of done:**

- `frame ui` added to `cli.py` per criteria 28-30, following the existing
  subcommand conventions (the `BAR` separator, the `[ ok ]` / `[FAIL]` icons).
- FastAPI is imported lazily inside `cmd_ui`, so the other commands work without
  the `[web]` extra (criterion 30).
- `CLAUDE.md` and `README.md` updated (criterion 34), including the data-type
  vocabulary change from criterion 32 if Phase 4 did not already make it.
- `tests/test_api.py` extended for criteria 28-30.

**Touches:** `src/frame_tools/cli.py`, `tests/test_api.py`, `CLAUDE.md`,
`README.md`

### Phase 8: gate — full workstation

**Definition of done:** gate report appended, then halt
**Touches:** this plan file only
**Commands to run:** as Phase 5, plus:

```powershell
.\.venv\Scripts\python.exe -m frame_tools.cli ui --no-browser --port 8765
.\.venv\Scripts\python.exe -m frame_tools.cli fields
.\.venv\Scripts\python.exe -m pytest tests\test_privacy.py -q -p no:cacheprovider
```

### Phase 9: verify — full workstation

**Definition of done:** Claude runs every canonical command, writes one real
measurement end to end through the browser against a copy, byte-diffs it,
confirms roadmap Phase 2's five exit criteria one by one, then appends PASS or
writes an error-fix. On PASS, Claude also reconciles
`docs/project/architecture.md` (its diagram says `fcc/server.py`; this plan
builds `fcc/api/`) and writes `docs/reports/phase-2-workstation.md` per the
Reporting Rule in `docs/claude/behaviour.md`.

---

## 7. Roadmap exit criteria — the bar this plan is measured against

From `docs/project/roadmap.md` Phase 2. Verified at Phase 9.

| # | Roadmap criterion | Covered by |
|---|---|---|
| 1 | A value entered in the browser changes the file and updates the report in one round trip | 4, 18 |
| 2 | A failing value still saves; the failing check's text appears verbatim from `validate.py` | 5, 20 |
| 3 | No field name, unit, or range literal appears anywhere in the TypeScript | 22 |
| 4 | Binds `127.0.0.1` only; path traversal refused; a test proves both | 11, 12 |
| 5 | Regenerating types from the running server produces no diff | 14, 15 |

---

## 8. Test commands (canonical)

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

Both must show zero failures **and zero errors** at every gate. Do not add a
fixed `--basetemp` flag; root `conftest.py` selects a writable basetemp at
runtime.

Baseline before this plan starts: **162 passed, 0 errors** and **10 checks,
0 warnings, 0 failures**.

---

## 9. Sign-off log

_(Empty. Codex appends gate reports; Claude appends sign-offs.)_
