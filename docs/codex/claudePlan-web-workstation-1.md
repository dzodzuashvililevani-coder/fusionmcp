# Web measurement workstation - spine

**Plan:** claudePlan-web-workstation-1.md
**Created:** 2026-08-27
**Source spec:** docs/brainstorming/idea-web-workstation.md
**Status:** ready-for-revision

> This plan was written before the canonical commands were amended for the local
> Windows policy state. It must be revised before implementation starts because
> `docs/project/architecture.md` now contradicts this plan on server and frontend
> technology choices.

## 0. Precondition (P0) - environment blocker

`.pytest-run-tmp/` is unreadable to its owner. `Get-ChildItem`, `Remove-Item`,
`takeown`, and `icacls` were denied on 2026-08-28. The generated
`.venv\Scripts\frame.exe` shim is also blocked by Windows Application Control,
while `python.exe -m frame_tools.cli report` succeeds.

The repository-level fix is a deliberate protocol amendment: canonical gate
commands now avoid both the locked temp path and the unsigned shim.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

Do not switch back to `frame.exe` unless the Windows policy is changed and the
protocol is amended again.

## 1. Goal (<= 3 sentences)

Build the spine of a local web UI for entering physical measurements: a single
declarative field spec, a comment-preserving writer that edits `params.yaml`,
`components/loadout.yaml`, and `docs/measurements.md` surgically, a
localhost-only HTTP server exposing them, and a minimal single-page form that
shows live `frame check` results after every save. No 3D, no photo upload, no
chat -- those are later plans that consume what this one builds.

## 2. Out of scope

- 3D component models, dimension animations, and any WebGL or Three.js.
- Photo upload, HEIC conversion, EXIF handling.
- In-page chat or any outbound network call.
- Any change to `geometry.py`, `mass.py`, `thrust.py`, `validate.py`, or
  `fusion.py`. The UI reads their output and never recomputes a dimension.
- Any change to the committed values in `params.yaml`. The file gains no new
  keys and loses none in this plan; only the writer touches its values, at
  runtime, driven by the user.
- Authentication, multi-user support, and any bind address other than
  `127.0.0.1`.
- Generalising the field spec to a second project.

## 3. Files in scope

Anything not on this list is OFF-LIMITS unless an error-fix or revision says
otherwise.

```
web/README.md                          (new)
web/fields.yaml                        (new)
web/index.html                         (new)
web/app.js                             (new)
web/style.css                          (new)
src/frame_tools/fields.py              (new)
src/frame_tools/writer.py              (new)
src/frame_tools/server.py              (new)
src/frame_tools/cli.py
tests/test_fields.py                   (new)
tests/test_writer.py                   (new)
tests/test_server.py                   (new)
tests/test_structure.py
CLAUDE.md
```

`.pytest-run-tmp/` may be deleted if the operating system allows it. It is not
part of the project state.

## 4. Acceptance criteria

Each is observable from outside the code.

1. **Byte-exact writes.** Writing a value to any key in `params.yaml` leaves
   every other byte of the file identical. A test asserts this by comparing the
   full before/after text with only the edited value's span allowed to differ.
2. **Comments survive.** The count of lines containing `#` in `params.yaml` is
   unchanged after a write, and every comment string present before is present
   after.
3. **Refusal over reformat.** Asking the writer for a key path it cannot address
   surgically raises a clear error naming the path. It never falls back to
   `yaml.dump`.
4. **Round trip.** After a write, `frame_tools.params.load_params()` returns the
   new value, and `yaml.safe_load` of the file still succeeds.
5. **Checklist update.** Writing a field whose spec names a
   `docs/measurements.md` label rewrites that line's `____` blank with the value
   and changes `- [ ]` to `- [x]`. No other line in the file changes.
6. **Missing label is an error.** If the spec names a label absent from
   `docs/measurements.md`, the write reports it. It does not silently skip.
7. **Spec is the only field list.** No field name, unit, or range literal
   appears in `app.js`, `server.py`, or `writer.py`. A test asserts every field
   the server serves comes from `web/fields.yaml`, and that every `key_path` in
   the spec resolves against the real `params.yaml`.
8. **Spec covers the TODOs.** Every key in `params.yaml` and
   `components/loadout.yaml` currently marked `TODO` has a row in the spec. A
   test enforces this, so a new `TODO` without a form field fails the build.
9. **Server binds locally only.** `frame ui` serves on `127.0.0.1`. A test
   asserts the bind address is never `0.0.0.0` or empty. The command exits
   non-zero with a clear message if the port is in use.
10. **Path refusal.** A GET for a static path containing `..`, an absolute path,
    or anything resolving outside `web/` returns 403 or 404 and does not read
    the file. Tests cover `..%2f` and backslash variants.
11. **Failing values still save.** Submitting a value that makes `frame check`
    fail returns HTTP 200, writes the value, and includes the failing check's
    `name` and `detail` verbatim from `validate.py` in the response.
12. **Live check payload.** A `GET` on the report endpoint returns the same
    numbers `frame report` prints: solver output, mass, TWR, and every check
    with its status. It calls `geometry.solve` / `validate.run` in-process; it
    does not shell out to the `frame` executable.
13. **Structure tests pass.** `web/README.md` has a `**Purpose:**` line and a
    `## Portals` table tagged with a data type present in both `DATA_TYPES` in
    `tests/test_structure.py` and the CLAUDE.md vocabulary table.
14. **Index updated.** `CLAUDE.md` has a portal row for `web/`, its "no
    JavaScript in this project" line is corrected, and the new data type is in
    its vocabulary table.
15. **Canonical commands clean.** `python.exe -m pytest -q -p no:cacheprovider`
    passes with zero errors, and `python.exe -m
    frame_tools.cli report` exits 0.

## 5. Phases

### Phase 1: implement - field spec and surgical writer

**Definition of done:**
- `web/fields.yaml` exists, with one row per measurable parameter. Each row
  carries: `id`, `question` (human sentence), `unit`, `file` (which of the three
  files it targets), `key_path` (dotted path, e.g. `motors.bolt_circle_mm`),
  `measurement_label` (the exact `docs/measurements.md` label, or `null`),
  `min` / `max` plausible range, and `shape_hint` (a string reserved for the
  later 3D plan; unused now, present so plan 3 adds no schema change).
- `src/frame_tools/fields.py` loads and validates the spec: every `key_path`
  resolves against the real file, every `file` is one of the three, ranges are
  ordered, ids are unique.
- `src/frame_tools/writer.py` exposes a small API:
  `write_param(key_path, value)`, `write_loadout(item_name, field, value)`,
  `tick_measurement(label, value)`. Each locates its target line, edits only the
  value span, and writes atomically via a temp file plus `os.replace`. Before
  the swap it re-parses the candidate with `yaml.safe_load` (for the two YAML
  files) and aborts if parsing fails.
- Every function raises a named error rather than reformatting, and refuses any
  path outside the project root.
- `tests/test_fields.py` and `tests/test_writer.py` cover acceptance criteria
  1-8. The writer tests must operate on a copy in `tmp_path`, never the real
  `params.yaml`.

**Touches:** `web/fields.yaml`, `src/frame_tools/fields.py`,
`src/frame_tools/writer.py`, `tests/test_fields.py`, `tests/test_writer.py`

**Notes for the implementer:**
- The byte-exactness property in criterion 1 is the load-bearing one. Write that
  test first, and let it drive the writer's design.
- `params.yaml` is currently flat scalars and short inline lists
  (`size_mm: [250, 250]`). Handle the scalar and inline-list cases and refuse
  everything else. Do not build a general YAML editor.
- Preserve the inline trailing comment on an edited line. `thickness_mm: 3.0
  # TODO measure with caliper` must keep its comment when the value changes; the
  `TODO` word may be dropped from that comment only if the spec says so
  explicitly, and this plan does not say so. Keep it.
- `components/loadout.yaml` uses inline flow maps
  (`- { name: camera, mass_g: 5.0, pos_mm: [0, 28, 14] }`). Editing one field
  inside a flow map on one line is the harder case; if it cannot be done
  surgically, say so in the gate report's Open questions rather than
  reformatting the file.

### Phase 2: gate - writer verified in isolation

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

### Phase 3: verify - writer

**Definition of done:** Claude appends a PASS sign-off, or writes
`claudePlan-web-workstation-1-errorFix-1.md`
**Touches:** this plan file, or an error-fix file if verification fails

### Phase 4: implement - local server

**Definition of done:**
- `src/frame_tools/server.py` uses `http.server` from the standard library. No
  new dependency.
- Endpoints:
  - `GET /` and static assets from `web/`, with the path refusal of criterion 10.
  - `GET /api/fields` - the validated spec plus each field's current value.
  - `GET /api/report` - solver output, mass, thrust, and all checks, built by
    calling `geometry.solve`, `mass.build`, `thrust.build`, `validate.run`
    in-process.
  - `POST /api/value` - `{id, value}`, writes through `writer.py`, returns the
    fresh `/api/report` payload in the same response so the UI updates in one
    round trip.
- Values outside a field's declared range are accepted and flagged in the
  response, not rejected. Non-numeric input for a numeric field is rejected with
  HTTP 400 and a clear message.
- `frame ui` is added to `cli.py` alongside the existing subcommands, with
  `--port` (default 8765) and `--no-browser`. It prints the URL and exits
  non-zero if the port is taken.
- `tests/test_server.py` covers criteria 9-12, driving the handler directly or
  over a loopback socket on an ephemeral port. No test may leave a server
  running.

**Touches:** `src/frame_tools/server.py`, `src/frame_tools/cli.py`,
`tests/test_server.py`

**Notes for the implementer:**
- `docs/protocol/trust-boundaries.md` governs this phase. Resolve every static
  path with `Path.resolve()` and confirm `web/` is a parent before opening.
  Rejecting on the raw string is not sufficient.
- There is no subprocess call in this phase by design; criterion 12 requires
  in-process calls. If a subprocess becomes necessary anyway, the trust-boundary
  rules apply: argument lists, never shell strings, and a timeout on every call.

### Phase 5: gate - server verified

**Definition of done:** gate report appended, then halt
**Touches:** this plan file only
**Commands to run:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
.\.venv\Scripts\python.exe -m frame_tools.cli ui --no-browser --port 8765
git diff --stat
```

Run `frame ui` long enough to confirm it binds and prints its URL, then stop it
and record what it printed.

**Status report sections:** commit SHA, files changed, test output,
self-assessment, open questions

### Phase 6: verify - server

**Definition of done:** Claude appends a PASS sign-off, or writes an error-fix
**Touches:** this plan file, or an error-fix file if verification fails

### Phase 7: implement - minimal page and index updates

**Definition of done:**
- `web/index.html`, `web/app.js`, `web/style.css`: one page, two panes. Left
  pane is the measurement form built entirely from `/api/fields`. Right pane
  shows the live report -- solver numbers, mass, TWR, and every check with its
  status icon -- refreshed from the response to each save.
- No build step, no package manager, no CDN, no external asset. Plain ES
  modules, loaded directly.
- The form marks which fields still hold `TODO` defaults so the remaining work
  is visible at a glance.
- `web/README.md` with a `**Purpose:**` line and a `## Portals` table listing
  every file in the folder.
- `tests/test_structure.py`: add the new data type tag to `DATA_TYPES`.
- `CLAUDE.md`: add the `web/` portal row, add the new tag to the data type
  vocabulary table, and correct the "There is no JavaScript in this project"
  line to describe the actual rule now in force.

**Touches:** `web/index.html`, `web/app.js`, `web/style.css`, `web/README.md`,
`tests/test_structure.py`, `CLAUDE.md`

**Notes for the implementer:**
- Criterion 7 applies to `app.js`. If a field label, unit, or range is typed
  into the JavaScript, this phase has failed regardless of how the page looks.
- Keep the page plain. Legibility beside a workbench beats visual polish, and
  plans 3 and 4 will rework this surface anyway.

### Phase 8: gate - full feature

**Definition of done:** gate report appended, then halt
**Touches:** this plan file only
**Commands to run:**

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
.\.venv\Scripts\python.exe -m frame_tools.cli ui --no-browser --port 8765
git status --short
git diff --stat
```

**Status report sections:** commit SHA, files changed, test output,
self-assessment, open questions

### Phase 9: verify - full feature

**Definition of done:** Claude runs the canonical commands, spot-checks at least
one acceptance criterion end to end (a real value written through the UI and
byte-diffed in `params.yaml`), and appends PASS or writes an error-fix
**Touches:** this plan file, or an error-fix file if verification fails

## 6. Test commands (canonical)

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

Both must be clean at every gate. `pytest` must show zero errors as well as zero
failures.

## 7. Sign-off log

_No gate reports yet. Codex appends here._
