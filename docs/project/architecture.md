# FusionControlCenter Technical Architecture

**Status:** proposed -- pending Codex review
**Created:** 2026-08-27
**Author:** Claude (planner role)
**Governs:** every implementation plan written after it is accepted
**Upstream:** `docs/project/description.md`, `docs/brainstorming/review-icm-paper.md`

---

## 0. How to read this

Every choice below is recorded in the same shape, because "why" is the part
that has to survive:

> **Options** considered · **Decision** · **Why** · **Cost** we accept ·
> **Revisit when** -- the concrete condition that would reopen it

A decision with no stated cost is a decision someone has not finished thinking
about. A decision with no revisit condition becomes dogma. Both fields are
mandatory.

**Section 4 is the direct answer to the load-balancing and database questions,**
and it is the section I would read first, because the answer is not the one the
question expects.

---

## 1. The forcing functions

Nine constraints determine almost every choice here. They are not preferences.

| # | Constraint | Consequence |
|---|---|---|
| C1 | **One user, one machine.** No tenants, no concurrent sessions | No auth, no session store, no horizontal scaling |
| C2 | **Fusion 360 is desktop software.** Its MCP server binds `127.0.0.1:27182` | The system is pinned to the user's desktop. A cloud deployment is impossible for half of it |
| C3 | **Fusion embeds its own CPython.** `adsk.*` exists only inside it | Anything running *inside* Fusion is Python. Not negotiable |
| C4 | **The solver already exists in Python**, tested -- `geometry.py`, `validate.py`, `mass.py`, `thrust.py` | Rewriting it in another language means two solvers, violating "geometry is solved exactly once" |
| C5 | **`params.yaml` is the single source of truth**, hand-edited, comments load-bearing, git-diffable | The store is the filesystem. Anything else is a cache |
| C6 | **ICM adopted:** filesystem as state machine, plain text as universal interface | Reinforces C5. Durable state is files |
| C7 | **Exported artifacts must survive decades**, and be readable by a separate project | Stable, boring formats. Optimise for readability over query speed |
| C8 | **Workshop conditions.** Possibly offline, hands dirty, screen at arm's length | Local-first, no CDN, legibility over density |
| C9 | **Trust boundaries are written and binding** (`docs/protocol/trust-boundaries.md`) | Loopback only, path containment, subprocess timeouts, no secrets in files |

---

## 2. The shape

```
   BROWSER  (localhost only)
   +--------------------------------------------------+
   |  React + TypeScript                               |
   |  measurement form | 3D component view | report    |
   |  react-three-fiber       TanStack Query           |
   +---------------------+----------------------------+
                         |  HTTP/JSON + SSE, 127.0.0.1
                         |  types generated from OpenAPI
   +---------------------v----------------------------+
   |  FastAPI + uvicorn   (single worker)              |
   |                                                   |
   |  src/fcc/          domain-blind platform          |
   |    fields.py    field spec loader                 |
   |    writer.py    surgical YAML/Markdown writer     |
   |    server.py    HTTP surface                      |
   |    photos.py    HEIC -> JPG, EXIF strip           |
   |                                                   |
   |  src/frame_tools/  drone-specific domain          |
   |    geometry validate mass thrust fusion           |
   +---------------------+----------------------------+
                         |  reads / writes
   +---------------------v----------------------------+
   |  THE FILESYSTEM  -- the actual database           |
   |  params.yaml  loadout.yaml  measurements.md       |
   |  photos/  dxf/  cad/  docs/knowledge/             |
   |  under git: history, diff, blame, backup          |
   +---------------------+----------------------------+
                         |  frame fusion -o
                         v
              fusion_scripts/frame_params.json
                         |
                         |  the user opens Fusion and runs the script
                         v
                    FUSION 360
                    (MCP :27182 for exploration only)
```

One process, one worker, one writer. The arrows are one-directional by design.

---

## 3. Decisions

### D1 -- Python core, TypeScript UI. Two languages, one boundary.

**Options.** (a) All Python, server-rendered HTML. (b) All TypeScript, port the
solver. (c) Python core + TypeScript UI.

**Decision.** (c).

**Why.** (b) is disqualified by C3 and C4: `fusion_scripts/` must be Python
because Fusion embeds CPython, so porting the solver to TypeScript produces two
solvers that must agree forever -- and `CLAUDE.md` states geometry is solved
exactly once. That rule is the backbone of the repo and no UI convenience is
worth breaking it. (a) is genuinely viable and would be simpler, but the
measurement UI's core idea -- a 3D component model that redraws from live
parameter values -- needs real client-side rendering, and server-rendered HTML
fights that.

So the boundary sits where it naturally belongs: **Python owns anything that
computes a physical number; TypeScript owns anything a human looks at.** No
geometry, no unit conversion, and no validation logic crosses into the frontend.
The browser renders what the server computed.

**Cost.** Two toolchains, two dependency trees, and a serialisation boundary
that can drift. D9 exists entirely to manage that drift.

**Revisit when.** Never, unless Fusion drops Python scripting.

---

### D2 -- No database as source of truth. Files are canonical.

This is the most important decision in the document and it is a deliberate
refusal.

**Options.** (a) PostgreSQL. (b) SQLite as primary store. (c) Document store.
(d) Filesystem, git-versioned.

**Decision.** (d). The design data stays in YAML and Markdown files under git.

**Why.**

1. **C5 makes it a contradiction.** `params.yaml` *is* the single source of
   truth by project rule. A database would create a second one, and the two
   would diverge the first time someone edits a file in an editor. The
   earlier analysis called this out as the failure that would quietly undo the
   project's central discipline.
2. **Git already provides what you would build a database to get.** Version
   history, per-line attribution, diffs across time, branching, atomic rollback,
   and off-machine backup. "Who changed the bolt circle, when, and why" is
   `git log -p params.yaml`. Reproducing that on top of SQLite is months of
   work for a worse result.
3. **The comments are data.** `thickness_mm: 3.0  # TODO measure with caliper`
   carries provenance in the same line as the value. Row-and-column storage
   discards it, and this project's entire thesis is that provenance is what
   makes a stored number reusable.
4. **C7 -- format longevity.** A YAML file opens in any editor in twenty years.
   A SQLite schema needs migrations, and a migration you forget to run is a
   silently wrong number driving a cutting machine.
5. **C6 -- ICM.** Every intermediate artifact is a plain-text file a human can
   open and edit between stages. A database is opaque exactly where this method
   wants transparency.
6. **Scale does not justify it.** One project has ~40 parameters. A hundred
   exported component records is a few hundred kilobytes. This is not a data
problem.

**Cost.** No transactions across files, no referential integrity, no query
language. Writes must be made atomic by hand (temp file + `os.replace`), and
cross-file consistency is enforced by `frame check` rather than by constraints.
That is a real cost and D3 is where it starts to bite.

**Revisit when.** Never for the source of truth. See D3 for the derived case.

---

### D3 -- SQLite later, as a disposable index. Never as truth.

**Options.** (a) Nothing, scan files always. (b) SQLite index rebuilt from
files. (c) Promote SQLite to primary once the library grows.

**Decision.** (b), **but not yet.**

**Why.** Linear scans over YAML are free at ten exported records and fine at a
hundred. They stop being fine when *this repository itself* needs real queries
over thousands of files -- which, with knowledge capture split out, it very
probably never will. Cross-project search belongs to the knowledge project.

The rule that keeps it safe is absolute:

> **If you delete the index, `frame reindex` reconstructs it perfectly from
> files. Nothing lives only in the database.**

SQLite specifically, not Postgres: it is in the Python standard library, needs no
server, no daemon, and no ops for a single user. Running Postgres for one person
on one machine is infrastructure cosplay.

**Cost.** A cache that can go stale. Mitigated by rebuild-on-demand and a
file-modification-time check at startup.

**Revisit when.** This repository holds more than ~500 exported records, **or** a query the
UI needs takes over 200ms by scanning. Not before. Building it now would be
optimising a problem that does not exist against a schema we have not learned
yet -- the same inversion the project already rejected when knowledge capture
was split out into its own project.

---

### D4 -- FastAPI + uvicorn. This revises my earlier recommendation.

**Options.** (a) stdlib `http.server`. (b) Flask. (c) FastAPI. (d) Litestar.

**Decision.** (c) FastAPI on uvicorn, single worker, bound to `127.0.0.1`.

**Why.** `claudePlan-web-workstation-1.md` currently specifies stdlib
`http.server`, on the reasoning that four endpoints and a form do not justify a
dependency. That reasoning was sound for the scope it was written against. The
scope has since grown -- photo upload, streaming AI responses, long-running
Fusion operations -- and it no longer holds. Stating the reversal plainly:

| Need | stdlib | FastAPI |
|---|---|---|
| Multipart photo upload | hand-rolled parsing | `UploadFile` |
| Streaming AI responses | hand-rolled SSE | native SSE / WebSocket |
| Typed request validation | hand-rolled | Pydantic |
| **Typed client for the frontend** | **impossible** | **OpenAPI, free** |
| Concurrent slow requests | threads, by hand | async |

The fourth row is the decisive one. FastAPI emits an OpenAPI schema from the
Pydantic models it already needs, and D9 turns that schema into TypeScript
types. That converts the riskiest seam in a two-language stack -- the JSON
boundary -- from a source of silent drift into something a build step verifies.
No hand-written framework substitutes for that.

**Cost.** Three direct dependencies (`fastapi`, `pydantic`, `uvicorn`) against a
project that currently has one. Accepted, and budgeted in section 8.

**Revisit when.** If the API stays under five endpoints with no upload and no
streaming through the whole roadmap, stdlib was right and this was overkill.

---

### D5 -- Vite + React + TypeScript. Not Next.js.

You proposed TypeScript and Next.js. Taking those separately: **TypeScript yes,
emphatically. Next.js no, and here is the honest reason.**

**Options.** (a) Next.js. (b) Vite + React + TS. (c) SvelteKit. (d) Plain TS,
no framework.

**Decision.** (b).

**Why.** Next.js is a superb framework for what it is built for: server-side
rendering, file-based routing over many pages, API routes, edge deployment, SEO.
Check each against FCC:

| Next.js gives you | FCC's situation |
|---|---|
| SSR / SSG | Nothing to pre-render. All data is local and live |
| API routes | The backend is Python (D1). These would be dead weight or a second backend |
| File-based routing | Three or four views |
| Image optimisation, edge caching | No CDN, no remote images, offline (C8) |
| SEO | Bound to `127.0.0.1` (C2). Nothing will ever crawl it |
| Vercel deployment | There is no deployment. `frame ui` starts it |

Every headline feature is inert here, and each carries conventions to work
around. The Next.js dev server would also sit awkwardly beside uvicorn -- two
servers where one plus a static build suffices.

Vite gives the parts that are actually needed: fast HMR while iterating on the
3D view, first-class TypeScript, and `vite build` producing static assets
FastAPI serves directly. One server in production, a dev proxy in development.

**Keeping TypeScript is not a concession -- it is load-bearing.** With a Python
backend, TS plus generated types (D9) is the only thing standing between you and
a renamed field silently becoming `undefined` in the UI.

**Cost.** Routing, data fetching, and layout are assembled rather than given.
For four views that is an afternoon, not a project.

**Revisit when.** FCC becomes multi-user or hosted -- which contradicts C1 and
C2, so realistically: if it ever becomes a product other people install remotely.

---

### D6 -- react-three-fiber + drei + react-spring for the 3D layer.

**Options.** (a) Raw Three.js with imperative refs. (b) react-three-fiber.
(c) Babylon.js. (d) Pre-rendered images or SVG diagrams.

**Decision.** (b), with `@react-three/drei` for helpers and
`@react-spring/three` for dimension animations.

**Why.** The core idea from `idea-web-workstation.md` is that the component
model renders **from live parameter values**, so a 9mm bolt circle on a 12mm
motor base visibly draws holes hanging off the edge -- the model becomes a second
validator catching the one error class no numeric check can, measuring the wrong
dimension.

That idea is declarative by nature: the model is a pure function of the current
parameters. r3f expresses exactly that -- `<Cylinder args={[baseDia/2, ...]}/>`
re-renders when the value changes, with no imperative scene-graph bookkeeping.
Raw Three.js would mean hand-writing that reconciliation.

drei supplies orbit controls, `<Line>`, and `<Html>` labels for caliper-style
dimension callouts. react-spring drives the tilt-and-highlight animation when a
field gains focus, and suits continuous physical motion better than keyframes.

**Cost.** ~600KB of Three.js, vendored. Acceptable offline; irrelevant on
localhost.

**Revisit when.** If static SVG diagrams turn out to disambiguate measurements
just as well -- they capture perhaps 70% of the value for 10% of the effort, as
already noted. The staging in section 6 of the master plan is deliberately built
so this can be answered with evidence instead of taste.

---

### D7 -- Tailwind CSS + shadcn/ui.

**Options.** (a) Plain CSS modules. (b) Tailwind. (c) MUI / Mantine.
(d) styled-components.

**Decision.** (b) Tailwind, with shadcn/ui components copied in as source.

**Why.** C8 sets the real requirement: legible at arm's length, dense report
panels, dark by default in a workshop. Tailwind iterates on that quickly with
zero runtime cost. shadcn/ui is copied into the repo rather than installed, so
components are editable source under git rather than an opaque dependency --
which fits a repo whose whole ethos is inspectable artifacts. Radix primitives
underneath give keyboard and focus behaviour for free.

Full component libraries (c) impose a design language and are heavy to override.

**Cost.** Verbose class strings. Managed by extracting components, not by
fighting the tool.

**Revisit when.** If a designer joins and prefers a token-based system.

---

### D8 -- TanStack Query for server state. No global store yet.

**Options.** (a) `useState` + `fetch`. (b) TanStack Query. (c) Redux Toolkit.
(d) Zustand.

**Decision.** (b) for everything crossing the network. Local UI state stays in
component state until proven otherwise.

**Why.** The central interaction is: save a measurement, then immediately show
the recomputed report. That is cache invalidation, which is precisely what
TanStack Query does well -- mutation, invalidate, refetch, with loading and error
states handled. Hand-rolling it produces the same code, worse.

Redux is unnecessary: there is very little client state, and nearly everything
on screen is server-derived.

**Cost.** One dependency, one concept to learn.

**Revisit when.** Genuine cross-view client state appears -- an undo stack, or
multi-step wizard state that must survive navigation. Then add Zustand, not
Redux.

---

### D9 -- One schema, generated types. The seam is enforced, not trusted.

**Decision.** Pydantic models are the single definition of every API payload.
FastAPI emits `/openapi.json`. `openapi-typescript` generates `web/src/api.d.ts`.
A test fails if the committed types differ from freshly generated ones.

**Why.** This is the whole reason D4 chose FastAPI. In a two-language stack the
most likely bug is not a crash -- it is a field renamed on one side, arriving as
`undefined` on the other, rendering blank, and being noticed three days later.
Making that a **build failure** rather than a **runtime blank** is the single
highest-leverage decision in the frontend stack.

It also mirrors a rule the project already follows: geometry is solved once and
consumed downstream; here, the contract is defined once and consumed downstream.

**Cost.** A generation step in the dev loop and a CI check.

**Revisit when.** Never. If this is dropped, drift is a matter of time.

---

### D10 -- Split the package: `fcc/` is domain-blind, `frame_tools/` is the drone.

**Decision.** New package `src/fcc/` holds the field spec, the writer, the
server, and photo ingest. `src/frame_tools/` keeps geometry, validation, mass,
thrust, and the Fusion payload. `fcc` may import `frame_tools` through a narrow
adapter; **`frame_tools` never imports `fcc`.**

**Why.** `description.md` commits to extracting FCC on the second project and to
extraction being "a move, not a rewrite". That is only true if the domain-blind
code is domain-blind from the first line. Writing the server inside
`frame_tools` and untangling it later is precisely the rewrite that was ruled
out.

The one-directional import rule is what makes the boundary real rather than
aspirational, and it is mechanically testable -- a test can assert that no module
under `frame_tools` imports `fcc`.

**Cost.** An adapter layer, and the discipline to notice when drone knowledge
leaks into `fcc`.

**Revisit when.** At extraction. The rule's job is to make that day boring.

---

### D11 -- Fusion stays user-driven. MCP explores; scripts execute.

**Decision.** Unchanged from `fusion_scripts/README.md`, now binding
architecture: **the MCP server is for exploration; proven steps are promoted
into committed scripts; the user launches Fusion and runs them.** FCC prepares
`frame_params.json` and the scripts. It never drives Fusion behind the user's
back.

**Why.** Three reasons, in increasing order of importance. The manifesto states
it directly: for every change the user opens Fusion themselves. MCP calls are
not reproducible and not in git, so anything load-bearing must become a script.
And Fusion has no undo across a script boundary -- automated CAD mutation with no
rollback, against a design a human has not looked at, is a bad trade for a system
whose entire value is trustworthy artifacts.

On extending the third-party MCP server: the first question is always whether
the capability belongs in `fusion_scripts/`, which we own, which are in git, and
which are already tested against a fake `adsk`. Fork the server only for what
scripts genuinely cannot do.

**Cost.** Some manual steps remain manual.

**Revisit when.** A round trip becomes so repetitive it is transcription rather
than judgment -- and even then it becomes a script, not a background automation.

---

### D12 -- Photo pipeline: Pillow + pillow-heif, EXIF stripped at ingest.

**Decision.** `pillow` and `pillow-heif` behind a `photos` extra. Ingest
converts HEIC to JPG, strips **all** EXIF, downscales to ~1500px, renames to the
`photos/own/` convention. `test_privacy.py` gains a check that fails on any
tracked image carrying EXIF GPS.

**Why.** All three problems are concrete: HEIC is unreadable to every tool here;
iPhone EXIF carries the GPS coordinates of wherever the photo was taken, which is
exactly what `test_privacy.py` exists to prevent but cannot see because it scans
text files only; and a 4MB phone photo enters git history permanently.

Stripping all EXIF rather than only GPS is deliberate -- an allowlist is a
maintenance burden and orientation can be baked into the pixels at ingest.

**Cost.** `pillow-heif` carries a native `libheif` wheel. Isolated in an optional
extra so the core stays pure.

**Revisit when.** If EXIF capture time turns out to be worth keeping. Then
extract it into the sidecar note file first, and still strip the image.

---

### D13 -- In-app AI: deferred, and specified so it is not improvised later.

**Decision.** Not built until plans 1-4 land. When built: Anthropic Python SDK
server-side, SSE to the browser, API key from the OS keychain via `keyring`,
never from a file or an env var in the repo.

**Why deferred.** The genuine gap in-app chat fills is *co-location* -- talking
about the design without losing sight of the numbers. Most of that is delivered
by putting the live `frame check` panel and a notes field on the same page, at a
fraction of the cost. Building the chat first would mean an API key store, an
agent loop, conversation persistence, and a new outbound trust boundary, to reach
a weaker version of the Claude Code session already in use.

**When it is built:** default to Sonnet 5 (`claude-sonnet-5`) for interactive
turns, Opus 5 (`claude-opus-5`) for design deliberation where reasoning depth
matters more than latency. Keys never touch the repo -- C9.

**Revisit when.** After plan 4, with a written note on what the notes panel still
failed to give you. That note is the requirements document.

---

### D14 -- Tooling.

| Layer | Tool | Why |
|---|---|---|
| Python env + deps | **uv** | Already the project's tool per `CLAUDE.md`. Fast, lockfile-backed |
| Python lint + format | **ruff** | One tool replacing flake8 + isort + black. Not yet in the repo; propose adding |
| Python tests | **pytest** | Already in use. 116 tests |
| Node package manager | **pnpm** | Content-addressed store, strict by default. npm acceptable if you prefer one less tool |
| Frontend build | **vite** | D5 |
| Frontend tests | **vitest** + React Testing Library | Shares Vite's config and transform |
| End-to-end | **Playwright** | Two or three flows only: enter a measurement, assert the file changed |
| Type generation | **openapi-typescript** | D9 |

**Deliberately absent:** Docker (cannot reach desktop Fusion, adds friction on
Windows for zero isolation benefit), and any CI runner beyond local hooks until
there is a second machine.

---

### D15 -- Process model: one worker, one writer, in-process jobs.

**Decision.** `uvicorn --workers 1 --host 127.0.0.1`. Long-running work
(photo batches, DXF generation) runs as asyncio tasks tracked in an in-process
job registry the UI polls or subscribes to.

**Why.** Multiple workers would be actively harmful, not merely unnecessary:
separate processes racing to write `params.yaml` is the one failure mode capable
of corrupting the source of truth. **The concurrency limit here is not CPU or
traffic -- it is that there must be exactly one writer.**

External edits are the real concurrency problem: you will edit `params.yaml` in
VS Code while the UI holds a stale copy. Handled by watching file mtimes and
warning on conflict, not by locking the user out of their own files.

**Cost.** No parallelism across requests for CPU-bound work. The solver runs in
milliseconds; irrelevant.

**Revisit when.** A single operation blocks the event loop for more than a
second. Then move that one operation to a thread pool -- not the server to
multiple workers.

---

## 4. What this project does not get, and why

Direct answers to the infrastructure questions, with the trigger that would
change each.

### Load balancing -- no, and adding it would break the system

Load balancing distributes traffic across replicas of a **stateless** service.
FCC is a **stateful single-instance desktop tool** whose state is the filesystem
of the machine Fusion runs on (C1, C2). Two replicas would mean two processes
writing `params.yaml`, which is D15's corruption case with extra steps.

**What you may actually be reaching for.** If the underlying wish is *"use this
from a tablet at the workbench while the desktop runs Fusion"* -- that is a real
and reasonable want, and the answer is not load balancing. It is: bind to the LAN
interface instead of loopback, put it behind Tailscale or a reverse proxy with
TLS, and add authentication **at that moment**, because C1 and C9 both stop
holding the instant it leaves loopback. One process still, reached from
elsewhere.

**Trigger:** you want bench access from a second device. Then we plan network
exposure and auth as one change, deliberately.

### PostgreSQL / MySQL -- no

A database server, a daemon, a connection pool, migrations, and backup strategy,
for one user and a few hundred kilobytes of design data that must stay
human-readable (C5, C7). See D2. SQLite may arrive later as a disposable index
(D3).

### ORM (SQLAlchemy, Prisma) -- no

There is no relational store to map. Pydantic covers validation and
serialisation, which is the part actually needed.

### Redis / Celery / RabbitMQ -- no

Background jobs run in-process (D15). A message broker for a single-user desktop
tool is infrastructure without a problem.
**Trigger:** a job must survive a server restart. Then the queue is a directory
of JSON files before it is Redis -- consistent with C6.

### Docker -- no

It cannot reach desktop Fusion, adds meaningful friction on Windows, and
isolates nothing that matters when there is one user on one machine. `uv` and
`pnpm` already give reproducible environments.
**Trigger:** a second contributor on a different OS.

### Authentication -- no, while it stays on loopback

Loopback binding is the access control. Adding a login screen to a single-user
localhost tool is theatre that trains you to click past it.
**Trigger:** the same one as load balancing. They arrive together or not at all.

### Cloud hosting -- structurally impossible

C2. Fusion runs on the desktop; its MCP server is on loopback. The half of the
system that matters cannot leave the machine.

---

## 5. Repo layout after this lands

```
drone-wood-frame/
  params.yaml                  <- source of truth (C5)
  components/                  loadout, materials
  src/
    fcc/                (new)  DOMAIN-BLIND platform
      __init__.py
      fields.py                field spec loader + validation
      writer.py                surgical YAML / Markdown writer
      photos.py                HEIC -> JPG, EXIF strip, downscale
      api/
        __init__.py
        app.py                 FastAPI application
        models.py              Pydantic schemas -> OpenAPI -> TS
        routes_fields.py
        routes_report.py
        routes_photos.py
      adapters/
        frame_adapter.py       the ONLY module importing frame_tools
    frame_tools/        (existing, unchanged)  DRONE-SPECIFIC
      geometry.py validate.py mass.py thrust.py fusion.py params.py
      cli.py                   gains `frame ui`
  web/                  (new)
    README.md                  required by test_structure
    fields.yaml                the one field spec (D9 sibling)
    package.json  pnpm-lock.yaml  vite.config.ts  tsconfig.json
    src/
      main.tsx  App.tsx
      api.d.ts               <- GENERATED. Never hand-edited
      components/
        MeasurementForm.tsx
        ReportPanel.tsx
        ComponentView.tsx    <- react-three-fiber
        DimensionCallout.tsx
      models/                parametric primitives
        Motor.tsx  Battery.tsx  FlightController.tsx  Prop.tsx
    dist/                    <- built assets, gitignored
  tests/
    test_fields.py  test_writer.py  test_server.py  test_boundaries.py
  docs/  photos/  dxf/  cad/  fusion_scripts/
```

`web/fields.yaml` sits with the frontend because it describes the *form*; it is
read by Python at runtime. If that placement feels wrong to Codex, moving it to
the repo root is a one-line change and worth arguing about now rather than later.

---

## 6. Data flows

### Saving one measurement (the core loop)

```
1. User focuses "Motor bolt circle"
2. ComponentView tilts the motor, highlights the bolt circle   (react-spring)
3. User types 9.4, presses Enter
4. POST /api/value  {id: "motor_bolt_circle", value: 9.4}      (typed, D9)
5. fcc.writer:
     - resolves id -> params.yaml key path via fields.yaml
     - rewrites ONLY that value's character span
     - writes temp file, re-parses with yaml.safe_load, os.replace
     - ticks the matching box in docs/measurements.md
6. fcc.adapters.frame_adapter: geometry.solve -> mass.build
                            -> thrust.build -> validate.run
7. Response carries the full recomputed report
8. TanStack Query updates the report panel; failing checks shown verbatim
9. A value that FAILS validation is still saved, and shouted about
```

Step 9 is a rule, not an oversight. Measurements are facts about physical
objects; blocking the save teaches you to fudge numbers until the validator goes
quiet, which is the exact failure `frame check` exists to prevent.

### Photo ingest

```
Drop .HEIC -> POST /api/photos (multipart, allowlist + size cap)
  -> pillow-heif decode -> strip ALL EXIF -> downscale 1500px
  -> photos/own/<convention>.jpg + sidecar note
  -> test_privacy.py enforces: no tracked image carries EXIF GPS
```

### Fusion handoff (unchanged)

```
frame fusion -o -> fusion_scripts/frame_params.json
  -> USER opens Fusion, runs sync_params.py            (D11)
  -> hole_pattern -> nest_parts -> mass_check -> export_dxf -> dxf/
```

---

## 7. Trust boundaries, mapped

Every rule in `docs/protocol/trust-boundaries.md` gets a mechanism.

| Rule | Mechanism |
|---|---|
| No writes outside project root | `Path.resolve()`, assert root is a parent, before every open. String checks are insufficient |
| Refuse `..` traversal | Same resolve-and-contain check. Tests cover `..%2f` and backslash forms |
| Refuse `.git/`, `.venv/`, caches | Explicit denylist checked after resolution |
| Subprocess: args not shell strings | No `shell=True` anywhere. A test greps for it |
| Subprocess: timeout on every call | Wrapper enforces a default; calling without one is an error |
| No secrets in files | API keys via `keyring` only (D13). `test_privacy.py` already scans tracked text |
| Local tool state out of git | `.gitignore`: `web/dist/`, `node_modules/`, `.venv/`, `.pytest-run-tmp/`, `.pytest-work-tmp/` |
| Upload safety | Extension allowlist, size cap, content-type sniff, never trust the filename |
| Bind loopback only | `host="127.0.0.1"` asserted by test. Never `0.0.0.0` |

---

## 8. Dependency budget

The project has one runtime dependency today. Growth, stated openly:

| Extra | Adds | Justification |
|---|---|---|
| core | `pyyaml` | Existing |
| `[ui]` | `fastapi`, `pydantic`, `uvicorn` | D4. The typed contract (D9) is the return |
| `[photos]` | `pillow`, `pillow-heif` | D12. Isolated: core stays pure |
| `[dxf]` | `ezdxf` | Existing |
| `[dev]` | `pytest`, `ruff`, `httpx` | `httpx` for the FastAPI test client |
| `[ai]` | `anthropic`, `keyring` | D13, deferred |
| frontend | react, three, @react-three/fiber, @react-three/drei, @react-spring/three, @tanstack/react-query, tailwindcss, vite, typescript | D5-D8 |

**Rule:** `frame report`, `frame check`, `frame geometry`, `frame mass`, and
`frame fusion` must keep working with **core only**. The CLI never depends on
the UI. If the whole web stack is uninstalled, the project still cuts wood.

---

## 9. Structural changes this requires

Adding `web/` breaks two existing rules and both must be fixed in the same
change or `test_structure.py` fails the gate:

1. `CLAUDE.md` states "There is no JavaScript in this project." Correct it to
   describe the rule now in force.
2. `DATA_TYPES` in `tests/test_structure.py` has no tag for web assets. Add
   **`Web`** (`.ts`, `.tsx`, `.css`, `.html`) and **`Generated`** (`api.d.ts`,
   lockfiles -- never hand-edited).
3. Add both tags to the CLAUDE.md data-type vocabulary table.
4. Add a `web____` portal row to the CLAUDE.md portal table.
5. Write `web/README.md` with a `**Purpose:**` line and a `## Portals` table.
6. `.gitignore`: `node_modules/`, `web/dist/`, `.vite/`.

---

## 10. What this document changes from earlier decisions

Recorded explicitly so the reversal is visible rather than silent:

| Earlier | Now | Why |
|---|---|---|
| stdlib `http.server` (`claudePlan-web-workstation-1.md` phase 4) | FastAPI + uvicorn | Scope grew to include upload and streaming; and the OpenAPI-to-TypeScript contract (D9) is unavailable from stdlib. See D4 |
| "plain ES modules, no build step" (phase 7) | Vite + React + TS | A two-language stack without generated types drifts. D5, D9 |
| Server code inside `frame_tools` | New `src/fcc/` package | `description.md` commits to extraction being a move, not a rewrite. D10 |

**`claudePlan-web-workstation-1.md` must be revised before Codex starts it.**
It is unstarted, so revision is free -- but it currently contradicts D4, D5, and
D10, and the older document must not be the one Codex reads.

---

## 11. Open questions for Codex review

1. **`web/fields.yaml` placement** -- with the frontend, or at the repo root
   since Python reads it at runtime? Section 5.
2. **pnpm or npm** -- pnpm is better; npm is one less tool to install. Preference?
3. **Is `ruff` welcome?** The repo has no linter today. Adding one is a
   formatting churn commit before it is a benefit.
4. **Commit `web/dist/` or build on demand?** Gitignoring it is cleaner;
   committing it means `frame ui` works on a clean checkout with no Node
   installed. This one genuinely cuts both ways and I do not have a strong view.
5. **Does the `fcc` / `frame_tools` split (D10) hold under scrutiny?** It is the
   decision most likely to be wrong, because domain-blindness is easy to declare
   and hard to keep.
6. **Is the D4 reversal accepted**, or is stdlib still preferred with upload and
   streaming hand-rolled?

### Codex review - 2026-08-28

Accepted for Phase 1:

- **D10 holds.** The `src/fcc/` / `src/frame_tools/` split is the right boundary
  for the data spine. `src/fcc/` owns domain-blind field specs and surgical
  writes; `frame_tools` remains the drone-specific solver and CLI entry point.
- **`fields.yaml` belongs at the repository root** for Phase 1, beside
  `params.yaml`, because Python reads it before any `web/` folder exists.
- The no-database/files-as-truth decisions stay binding for the data spine.

Deferred:

- D4/D5 web stack decisions are accepted as architecture direction, but not
  implemented in Phase 1.
- Package manager and built-asset questions remain Phase 2 decisions.

---

## 12. Next steps

1. Codex reviews this document and returns findings.
2. On acceptance, it becomes binding on every plan and
   `claudePlan-web-workstation-1.md` is revised to match (section 10).
3. Claude writes the **master plan** -- the full sequence from here to a flown
   frame and a captured component library.
4. Claude writes **phase 1** as `docs/codex/claudePlan-<slug>-1.md`.

The locked `.pytest-run-tmp` directory and blocked `frame.exe` shim are handled
by the protocol-level canonical commands:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
.\.venv\Scripts\python.exe -m frame_tools.cli report
```
