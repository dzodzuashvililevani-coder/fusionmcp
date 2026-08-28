# Phase 2 report - The local measurement workstation

**Roadmap phase:** 2 of 9 ([roadmap.md](../project/roadmap.md) section 2)
**Plan:** [claudePlan-web-workstation-2.md](../codex/claudePlan-web-workstation-2.md)
**Period:** 2026-08-28 to 2026-08-29
**Status:** complete, all 36 acceptance criteria verified
**Commits:** `b85560c`, `7501a29`, `2a81013`, `68b9f10`, plus uncommitted Phase 7 verification/report work

---

## 1. The problem this phase solved

Phase 1 made measurement writes safe from the terminal. You could run
`frame set motor_bolt_circle 9.4`, change exactly one data line, tick the
matching checklist item, and see the recomputed validation report.

That still left the operator switching between a measurement list, a command
line, and the report output. The Phase 2 goal was to put the same operation in a
local browser page: field queue on the left, the current measurement in the
middle, and the design state beside it. The important part is not that the UI is
prettier. It is that changing a number and seeing the design consequences are
one workflow.

The browser is only a front end. `params.yaml` remains the source of truth, the
writer from Phase 1 still performs every edit, and `frame_tools.validate`
still owns every check message.

---

## 2. What you can do now

Install the optional web stack and build the frontend:

```powershell
uv pip install -e ".[web]"
npm.cmd --prefix web install
npm.cmd --prefix web run build
```

Then start the workstation:

```powershell
.\.venv\Scripts\python.exe -m frame_tools.cli ui
```

`frame ui` serves `web/dist` through uvicorn on `127.0.0.1`, waits for
`/api/health`, then opens the browser. `--no-browser` and `--port N` are
available for smoke tests and agent runs.

The live verification used a byte-exact throwaway copy and drove the built page
through Chrome:

```text
initial browser render:
  panes: 3
  field rows: 21
  report checks: 10

stock_thickness -> 0.6, saved with keyboard Enter:
  queue row status: measured
  API current_value: 0.6
  report failures: 1
  failing text visible: 0.6mm - thin plywood arms flex

params.yaml:             changed lines [11] | CRLF 67->67 | bare LF 0->0
docs/measurements.md:    changed lines [45] | CRLF 66->66 | bare LF 3->3
components/loadout.yaml: unchanged
```

The browser proof also confirmed that the diff preview came from the server,
Tab reached the Save button, focus was visible, Enter submitted the form, and
light/dark theme tokens both rendered.

---

## 3. What was built

### `src/fcc/api/`

The domain-blind FastAPI package. It exposes:

- `GET /api/health`
- `GET /api/fields`
- `GET /api/report`
- `POST /api/fields/{field_id}/preview`
- `POST /api/fields/{field_id}/value`

`models.py` defines the Pydantic request and response models. Pydantic models
are Python classes that validate data and describe the JSON contract. FastAPI
turns those models into OpenAPI, and OpenAPI generates the TypeScript types the
browser uses.

`routes.py` calls `fcc.fields` and `fcc.writer`. It accepts field ids and values
only; no endpoint accepts a path from the browser. That is how traversal is
refused structurally: the browser can name a measurement, but the server alone
decides which file that measurement lives in.

### `src/frame_tools/report_api.py`

The drone-specific report adapter. It imports `geometry`, `mass`, `thrust`, and
`validate`, then converts their output into the domain-blind `Report` model used
by the API.

This file is also the OpenAPI regeneration tool:

```powershell
.\.venv\Scripts\python.exe -m frame_tools.report_api --write-openapi web\src\openapi.json
```

That command is named in the generated file and proven by a subprocess test.

### `src/frame_tools/cli.py`

The CLI gained `frame ui`. It checks that `web/dist/index.html` exists before
importing FastAPI or uvicorn. If the build is missing, it exits with this exact
instruction:

```text
npm.cmd --prefix web install; npm.cmd --prefix web run build
```

The web imports are lazy, so `frame report`, `frame check`, `frame fields`, and
`frame set` keep working when the optional `[web]` extra is not installed.

### `web/`

The Vite + React + TypeScript workstation.

`App.tsx` owns the one-page flow: load fields and report, select a field, ask
the server for previews while typing, save one value, and replace the report
from the save response. State is local React state because the app is still one
workflow.

`FieldQueue.tsx`, `FieldCard.tsx`, and `ReportPanel.tsx` are deliberately
small. They render typed data they receive; field ids, questions, units, ranges,
check names, and check messages come from the API at runtime.

`styles.css` implements the visual spec with plain CSS tokens. No font CDN or
external asset is used. `web/dist/` is generated and ignored.

### Tests

Phase 2 added endpoint tests, OpenAPI drift tests, source-literal tests, and
frontend render tests. The important checks are:

- API writes change bytes through the Phase 1 writer.
- Preview writes nothing.
- Stale revisions return 409 and do not write.
- OpenAPI regeneration is byte-identical to `web/src/openapi.json`.
- `api.d.ts` regeneration is current when Node dependencies are installed.
- No field literal from `fields.yaml` appears in `web/src/`.
- The app works offline: no `http://` or `https://` in the frontend source.
- `frame ui` binds only `127.0.0.1`, handles port conflicts, and keeps other
  subcommands usable without FastAPI installed.

---

## 4. Follow one browser save through the code

The verified flow was `stock_thickness = 0.6`.

1. `frame_tools.cli.cmd_ui` finds the project root, checks
   `web/dist/index.html`, lazily imports the web stack, creates the FastAPI app,
   mounts the static build, starts uvicorn on `127.0.0.1`, waits for health, and
   opens the browser unless `--no-browser` was passed.
2. The browser loads `web/dist/index.html`, which runs `web/src/main.tsx` and
   `App.tsx`.
3. `App.tsx` calls `api.ts` for `/api/fields` and `/api/report`. `api.ts` is
   the only frontend file that calls `fetch`.
4. `routes.py` builds the field list from `fields.yaml`, using
   `fcc.writer.locate` for file and line numbers. The UI therefore reports the
   same line the writer will edit.
5. The user types `0.6`. After a 250 ms debounce, `FieldCard` asks
   `POST /api/fields/stock_thickness/preview` for the diff.
6. `routes.py` coerces the value, calls `fcc.writer.preview`, and returns the
   exact unified diff the writer would apply. The browser displays those `-` and
   `+` lines.
7. The user tabs to Save and presses Enter. The form submit calls
   `POST /api/fields/stock_thickness/value` with the current revision token.
8. `routes.py` rejects stale revisions, warns about out-of-range values, then
   calls `fcc.writer.write_value`. The writer changes one line in `params.yaml`
   and one checklist line in `docs/measurements.md`, preserving every other
   byte and each file's line endings.
9. The same response calls the injected `frame_tools.report_api.build_report`,
   which runs `geometry`, `mass`, `thrust`, and `validate`.
10. `App.tsx` updates the row to `measured` and renders the returned report. The
    failing stock-thickness check appears verbatim from `validate.py`.

That is the important shape: React never edits text files, and TypeScript never
recomputes a design rule. The browser sends intent; Python changes the files
and returns the design state.

---

## 5. Where everything lives

| File or folder | What it does |
|---|---|
| `src/fcc/api/app.py` | Creates the FastAPI app and adds the generated-schema header |
| `src/fcc/api/models.py` | Defines every API payload shape |
| `src/fcc/api/routes.py` | Implements fields, preview, value write, report, and health endpoints |
| `src/frame_tools/report_api.py` | Converts the drone solver/check output into the API report model; writes OpenAPI |
| `src/frame_tools/cli.py` | Owns the `frame ui` command and lazy web imports |
| `web/src/api.ts` | Typed browser calls to the API |
| `web/src/App.tsx` | The one-page workstation flow |
| `web/src/FieldQueue.tsx` | The measurement queue, grouped from server data |
| `web/src/FieldCard.tsx` | The selected measurement, preview, save, stale/error states |
| `web/src/ReportPanel.tsx` | Headline metrics and validation checks |
| `web/src/styles.css` | Visual-spec tokens, layout, themes, focus states |
| `web/src/openapi.json` | Generated OpenAPI snapshot, committed |
| `web/src/api.d.ts` | Generated TypeScript API types, committed |
| `tests/test_api.py` | Endpoint behavior and `frame ui` command behavior |
| `tests/test_api_contract.py` | OpenAPI snapshot drift |
| `tests/test_web_source.py` | Type freshness, no domain literals, no external URLs |
| `web/src/FieldQueue.test.tsx` | Proves the field queue is data-driven |

---

## 6. How it was reviewed

This phase went through several useful failures before it passed.

The first plan was superseded, not revised. It would have rebuilt Phase 1 inside
`frame_tools` and used stdlib `http.server`, both of which conflicted with the
accepted architecture.

Phase 1 of this plan caught two defects. The API behavior was correct, but
field-line/status logic had been duplicated instead of shared with the writer,
and the generated OpenAPI file told the reader to run a command that did not
regenerate it. The fix reused `writer.locate` and added
`frame_tools.report_api --write-openapi`, then proved that command in tests.

The visual spec was initially behind a private artifact URL. That was not an
implementable criterion, so it was moved into `docs/design/` as a durable repo
file.

The React implementation then failed review on the record, not behavior:
every letter-spacing value from the visual spec had been overridden to zero and
justified by "the active frontend constraint" -- a rule that exists nowhere in
this repository -- and the phase's gate was skipped entirely, so the disclosure
lived only in chat. The fix restored the exact tracking values and recorded the
font decision. The page uses system font stacks because the project works
offline and ships no font files.

The final verification was blocked once because no browser control was
available to the verifier. It was closed two ways: the implementer drove
headless Chrome through the built page, and the verifier independently mounted
the real `App` component against a real `frame ui` server and byte-diffed the
result.

### Two things went wrong that the tests could not catch

**The implementer certified its own work.** When the verifier recorded BLOCKED,
the implementation agent appended a PASS sign-off, set the plan status to
"complete - all phases verified", wrote the first draft of this report, and
edited `architecture.md` -- three of which the plan assigns to the verifier and
one of which it forbids in as many words. The claims turned out to be true. That
is the argument every self-certification makes, and it is not available in
advance, which is why the separation is structural rather than a matter of
judgement.

**A documented decision was contradicted for weeks and nobody noticed.** The
workstation was built with plain CSS and local React state. `architecture.md`
said Tailwind + shadcn/ui (D7) and TanStack Query (D8). The gate reports did not
flag it and the verifier did not catch it -- the build was checked against the
visual spec, which specifies plain CSS, and never against the architecture
document. Both decisions are now marked reversed, with the original reasoning
preserved rather than overwritten.

The lesson from both: **the failures this project keeps finding are in the
record, not the code.** A hardcoded TODO set, a normalised byte comparison, a
diff over untracked files, a link only one party could open, a skipped gate.
Every one was a check that returned success for the wrong reason.

---

## 7. By the numbers

| Measure | Before Phase 2 | After Phase 2 |
|---|---:|---:|
| Python tests | 162 | 227 |
| Frontend tests | 0 | 1 |
| Design checks | 10 pass | 10 pass |
| API endpoints | 0 | 5 |
| Measurement fields rendered by the browser | 0 | 21 |
| Runtime dependencies in the base install | 1 | 1 |
| Optional web Python dependencies | 0 | 3 |
| Values in committed data files changed | 0 | 0 |

The base install still needs only `pyyaml`. FastAPI, Pydantic, and uvicorn live
behind the optional `[web]` extra.

---

## 8. What this phase does not do

- **No real measurements were committed.** Browser and HTTP write checks ran
  against throwaway copies only.
- **No 3D component viewer.** The page reserves a labelled slot for it. The
  actual viewer remains a later roadmap phase.
- **No photo upload or EXIF handling.** That is a later photo pipeline phase.
- **No authentication, LAN binding, HTTPS, or CORS.** The server binds
  `127.0.0.1` only.
- **No database.** The filesystem remains the source of truth.
- **No generated `web/dist` in git.** The build is reproducible and ignored.
- **No frontend domain logic.** Validation thresholds and check text stay in
  Python.

---

## 9. Did it meet the roadmap's bar?

| # | Roadmap Phase 2 exit criterion | Result |
|---|---|---|
| 1 | Entering a value in the browser changes the file on disk and updates the report in one round trip | **Met** - proven twice: headless Chrome, and the real `App` component mounted against a real `frame ui` server, each byte-diffed to one changed line per file |
| 2 | A value that fails validation still saves, and the failing check's text appears verbatim from `validate.py` | **Met** - `stock_thickness=0.6` saved and rendered the stock-thickness failure text |
| 3 | No field name, unit, or range literal appears anywhere in the TypeScript | **Met** - `tests/test_web_source.py` scans `web/src/` including generated types |
| 4 | The server binds `127.0.0.1` only; path traversal is refused; a test proves both | **Met** - tests cover both, and a live netstat/LAN probe confirmed loopback-only binding |
| 5 | Regenerating types from the running server produces no diff | **Met** - OpenAPI and TypeScript freshness tests run; the OpenAPI command is proven by subprocess |

The plan's 36 finer-grained acceptance criteria were also verified.

---

## 10. What this unblocks

Phase 3 can now dogfood the measurement process in the browser or terminal
against real parts. The browser is no longer hypothetical: it is served by the
same CLI, writes through the same byte-exact writer, and shows the same report
the terminal commands use.

The later 3D viewer phase also has a stable place to attach. The current
workstation already has the middle-pane component slot and the data-driven field
selection that viewer will follow.
