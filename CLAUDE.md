# drone-wood-frame -- master index

Parametric wooden FPV drone frame cut from 250x250mm stock, built around
components salvaged from a Temu toy drone.

**`params.yaml` is the single source of truth.** Every calculation, every
validation rule, and the Fusion model all derive from it. Change a number
there, re-run `python -m frame_tools.cli report`, rebuild.

---

## Portals

Jump straight to the thing you need. Every folder also has its own `README.md`
with a finer-grained table.

| Portal | Path | Type | Holds |
|---|---|---|---|
| `params____` | [params.yaml](params.yaml) | YAML | **Start here.** All design numbers |
| `fields____` | [fields.yaml](fields.yaml) | YAML | Measurement field spec used by CLI/UI writers |
| `loadout____` | [components/loadout.yaml](components/loadout.yaml) | YAML | Component masses + positions for CG |
| `materials____` | [components/materials.yaml](components/materials.yaml) | YAML | Wood density table |
| `loader____` | [src/frame_tools/params.py](src/frame_tools/params.py) | Python | Find the project root, load YAML, screw + hole sizes |
| `geometry____` | [src/frame_tools/geometry.py](src/frame_tools/geometry.py) | Python | Arm-length solver, motor coordinates |
| `mass____` | [src/frame_tools/mass.py](src/frame_tools/mass.py) | Python | Mass budget, centre of gravity |
| `thrust____` | [src/frame_tools/thrust.py](src/frame_tools/thrust.py) | Python | Thrust-to-weight, hover throttle |
| `validate____` | [src/frame_tools/validate.py](src/frame_tools/validate.py) | Python | Pre-cut design rules |
| `fusionout____` | [src/frame_tools/fusion.py](src/frame_tools/fusion.py) | Python | Builds the Fusion payload + User Parameter table |
| `dxfout____` | [src/frame_tools/dxf_out.py](src/frame_tools/dxf_out.py) | Python | Kerf calibration coupon (the only non-Fusion DXF) |
| `cli____` | [src/frame_tools/cli.py](src/frame_tools/cli.py) | Python | `frame` command entry point |
| `fcc____` | [src/fcc/](src/fcc/README.md) | Python | Domain-blind field spec and writer support |
| `fccapi____` | [src/fcc/api/](src/fcc/api/README.md) | Python | Domain-blind FastAPI routes for the browser workstation |
| `pytestconf____` | [conftest.py](conftest.py) | Python | Shared pytest temp-root selection for agent environments |
| `project____` | [docs/project/](docs/project/README.md) | Markdown | Project identity, mission, scope, source-of-truth hierarchy |
| `brainstorm____` | [docs/brainstorming/](docs/brainstorming/README.md) | Markdown | Rough feature ideas before a plan exists |
| `knowledge____` | [docs/knowledge/](docs/knowledge/README.md) | Markdown | Export contract: what finished work hands off to a separate knowledge project |
| `protocol____` | [docs/protocol/](docs/protocol/README.md) | Markdown | Plan-Gate-Verify roles, contracts, gates, trust boundaries |
| `claude____` | [docs/claude/](docs/claude/README.md) | Markdown | Claude planner/verifier role docs |
| `codex____` | [docs/codex/](docs/codex/README.md) | Markdown | Codex implementer inbox: plans, gates, error fixes |
| `reports____` | [docs/reports/](docs/reports/README.md) | Markdown | Plain-language report per finished roadmap phase |
| `design____` | [docs/design/](docs/design/README.md) | Markdown | Visual specs and mockups. Normative for anything a human looks at |
| `measure____` | [docs/measurements.md](docs/measurements.md) | Markdown | Caliper checklist to fill in |
| `buildlog____` | [docs/build-log.md](docs/build-log.md) | Markdown | What actually happened |
| `fusion____` | [fusion_scripts/](fusion_scripts/README.md) | Python (in Fusion) | Scripts that run inside Fusion |
| `handoff____` | [fusion_scripts/frame_params.json](fusion_scripts/frame_params.json) | JSON | The generated handoff. `frame fusion -o` writes it |
| `mcp____` | [.mcp.json](.mcp.json) | JSON | Fusion MCP endpoint, picked up by Claude Code |
| `web____` | [web/](web/README.md) | TypeScript | Local browser measurement workstation |
| `editor____` | [.vscode/](.vscode/README.md) | JSON | Interpreter path, pytest, debug config |
| `cad____` | [cad/](cad/README.md) | Binary CAD | `.f3d` / `.step` exports |
| `cut____` | [dxf/](dxf/README.md) | Vector | `.dxf` files for the cutter |
| `photos____` | [photos/](photos/README.md) | Raster | Part photos + web reference images |
| `tests____` | [tests/](tests/README.md) | Python | Design invariants |
| `install____` | [install-fusion-scripts.ps1](install-fusion-scripts.ps1) | PowerShell | Register `fusion_scripts/` with Fusion, as shims back to the repo |
| `carry____` | [carry-session.ps1](carry-session.ps1) | PowerShell | Move a Claude conversation into this project's session store |

---

## Data type vocabulary

Used in every folder's portal table, so the type is always unambiguous.

| Tag | Extensions | Diffable | Notes |
|---|---|---|---|
| **YAML** | `.yaml` | yes | Hand-edited data. Comments allowed and encouraged |
| **Python** | `.py` | yes | Runs in the project venv |
| **Python (in Fusion)** | `.py` | yes | Runs in Fusion's own interpreter. `adsk.*` only exists there |
| **Markdown** | `.md` | yes | Docs and indexes |
| **JSON** | `.json` | yes | Machine output only. Never hand-edit |
| **PowerShell** | `.ps1` | yes | Windows helper scripts |
| **Vector** | `.dxf`, `.svg` | text, but do not hand-edit | Generated cut geometry |
| **Binary CAD** | `.f3d`, `.step`, `.stl` | **no** | Git stores whole copies. Commit milestones only |
| **TypeScript** | `.ts`, `.tsx` | yes | Browser code. Types for the API are generated, never hand-written |
| **CSS** | `.css` | yes | Styles. Every colour comes from a token in the design spec |
| **HTML** | `.html` | yes | Page shells and design mockups |
| **Raster** | `.jpg`, `.png` | **no** | Photos and web references. Downscale before committing |

Browser code lives in `web/` and nowhere else. It is TypeScript, never plain
JavaScript, and the API types in `web/src/api.d.ts` are generated from the
server's schema rather than written by hand -- see
[docs/project/architecture.md](docs/project/architecture.md) D9.

---

## Commands

```powershell
.\.venv\Scripts\python.exe -m frame_tools.cli report      # geometry + mass + checks
.\.venv\Scripts\python.exe -m frame_tools.cli geometry    # arm length, motor coordinates
.\.venv\Scripts\python.exe -m frame_tools.cli mass        # mass budget and centre of gravity
.\.venv\Scripts\python.exe -m frame_tools.cli check       # pre-cut validation, exits nonzero on failure
.\.venv\Scripts\python.exe -m frame_tools.cli fields      # list measurement ids, current values, and TODO status
.\.venv\Scripts\python.exe -m frame_tools.cli set <id> <value>  # write one measured value, then print checks
.\.venv\Scripts\python.exe -m frame_tools.cli fusion      # resolved numbers as JSON on stdout
.\.venv\Scripts\python.exe -m frame_tools.cli fusion -o   # ...written to fusion_scripts/frame_params.json instead
.\.venv\Scripts\python.exe -m frame_tools.cli kerf-test   # write dxf/kerf_test.dxf to calibrate the cutter
.\.venv\Scripts\python.exe -m frame_tools.cli ui          # serve the local browser workstation
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Setup, once:

```powershell
uv venv
uv pip install -e ".[dev,dxf]"
uv pip install -e ".[web]"
npm.cmd --prefix web install
npm.cmd --prefix web run build
```

## Conventions

- Coordinates are **millimetres**, origin at the frame centre,
  `+x` = right, `+y` = forward (nose), `+z` = up.
- Masses are **grams**. Densities are **g/cm^3**.
- Never hardcode a dimension in Python. Add it to `params.yaml` and read it.
- **Every folder has a `README.md`** with a portal table. Add a row when you
  add a file. `pytest` fails if a folder is missing its README.
- Treat [docs/project/description.md](docs/project/description.md) as the
  mission baseline. Raw brainstorming becomes implementation truth only after
  it is promoted into a project, protocol, plan, or data file.
- **This project makes things; it does not remember them.** Knowledge capture is
  a separate project (decided 2026-08-28,
  [docs/brainstorming/decision-scope-split.md](docs/brainstorming/decision-scope-split.md)).
  Do not build an extractor, a component library, or a promotion mechanism here.
- When something is **finished**, record it in its named folder from
  `description.md` section 8, with its source and verification state attached.
  The contract lives in
  [docs/knowledge/capture-candidates.md](docs/knowledge/capture-candidates.md).
  Writing the label is in scope; acting on it is not.
- **`params.yaml` as committed must pass `frame check`.** A repo whose default
  numbers fail its own validator teaches you to ignore the validator. If a
  constraint can be *solved for*, solve it in `geometry.py` rather than only
  reporting it in `validate.py`.
- **Geometry is solved exactly once**, in `geometry.py`. Fusion and the DXF
  consume `frame fusion` output; nothing downstream recomputes a dimension.
- Inside Fusion, **every API length is centimetres** regardless of document
  units. Convert at the boundary with `_common.mm()` / `to_mm()`.
- For multi-agent work, start rough ideas in
  [docs/brainstorming/](docs/brainstorming/README.md), follow the shared
  [docs/protocol/](docs/protocol/README.md), have Claude write plans into
  [docs/codex/](docs/codex/README.md), and verify with
  [docs/claude/](docs/claude/README.md). Plans and sign-offs are files, gates
  are hard halts, and the planner is not the implementer.
