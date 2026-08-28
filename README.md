# drone-wood-frame

A parametric wooden FPV drone frame, cut from 250x250mm stock, using salvaged
components (motors, ESCs, flight controller, camera) from a Temu toy drone.

`params.yaml` is the single source of truth. Everything else - the calculators,
the validation, the Fusion model, the DXF cut files - is derived from it.

## Setup

```powershell
uv venv
uv pip install -e ".[dev,dxf]"
```

`dev` gives you `pytest`, `dxf` gives you `ezdxf` for the kerf coupon. The base
install needs only `pyyaml`.

Check it worked:

```powershell
.\.venv\Scripts\python.exe -m frame_tools.cli report      # must end "0 failures"
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

Then register the Fusion-side scripts, once:

```powershell
.\install-fusion-scripts.ps1
```

That does not copy them -- it installs shims that call back into
[`fusion_scripts/`](fusion_scripts/README.md), so editing a script and
re-running it in Fusion picks up the change with no restart and no second copy
to keep in sync.

## Use

```powershell
.\.venv\Scripts\python.exe -m frame_tools.cli report      # geometry + mass + checks (start here)
.\.venv\Scripts\python.exe -m frame_tools.cli geometry    # arm length, motor coordinates
.\.venv\Scripts\python.exe -m frame_tools.cli mass        # mass budget and centre of gravity
.\.venv\Scripts\python.exe -m frame_tools.cli check       # pre-cut validation - exits nonzero if something is wrong
.\.venv\Scripts\python.exe -m frame_tools.cli fields      # measurement ids, current values, and TODO status
.\.venv\Scripts\python.exe -m frame_tools.cli set <id> <value>  # write a measured value, then print checks
.\.venv\Scripts\python.exe -m frame_tools.cli fusion      # resolved numbers as JSON, for the Fusion MCP
.\.venv\Scripts\python.exe -m frame_tools.cli fusion -o   # ...written to fusion_scripts/frame_params.json instead
.\.venv\Scripts\python.exe -m frame_tools.cli kerf-test   # write dxf/kerf_test.dxf, to measure your cutter's kerf
```

The shorter `frame ...` commands work when Windows allows the generated
`.venv\Scripts\frame.exe` shim. This workstation currently blocks that shim, so
the Python module entry point is the reliable command form.

## Workflow

1. Run `fields` to see the measurement ids and which values are still TODO guesses
2. Measure a part, then run `set <id> <value>` so the data file and checklist update together
3. Run the report command until every check passes
4. Run `kerf-test`, cut the coupon, put the measured kerf back in `params.yaml`
5. Run `fusion -o`, then run `frame_sync_params` in Fusion to load the parameters
6. Model the plate and arms against those parameters, naming cut sketches `CUT_*`
7. `frame_nest_parts` and `frame_mass_check` in Fusion, then `frame_export_dxf` -> `dxf/`
8. Cut, assemble, and log what actually happened in `docs/build-log.md`

Steps 5-7 are the [`fusion_scripts/`](fusion_scripts/README.md) run order.
Step 4 before step 7, not after: an uncalibrated kerf means every motor screw
hole comes out oversized, and a loose motor mount on a wooden arm does not stay
tight.

## Fusion MCP

Fusion -> Preferences -> General -> API -> enable **Fusion MCP Server** (port 27182).

The endpoint is already committed in [`.mcp.json`](.mcp.json), so Claude Code
picks it up from this folder -- approve the server when it prompts, then run
`/mcp` to confirm it connected. Nothing else to configure.

**Use `127.0.0.1`, not `localhost`.** The server checks the Host header and
answers `403 Forbidden` to anything else, including `localhost:27182`, which is
the same address by any other measure. Verified against a live server on
2026-08-24: `127.0.0.1` initializes and lists four tools
(`fusion_mcp_read`, `fusion_mcp_update`, `fusion_mcp_execute`,
`fusion_mcp_electronics_read`); `localhost` is refused before the handshake.

To register it globally instead of per-project:

```powershell
claude mcp add --transport http fusion http://127.0.0.1:27182/mcp
```

Fusion must be **open, with a design active**, or the tools connect but have
nothing to act on.

**MCP explores; scripts repeat.** Use the MCP conversationally to try things,
then lock whatever worked into a script in `fusion_scripts/` so the next frame
does not need the conversation again.

## Finding things

**[CLAUDE.md](CLAUDE.md) is the master index** - portal table for the whole
project plus the data-type vocabulary. Start there.

Every folder then has its own `README.md` with a finer-grained portal table
saying what it holds and in what format:

| Folder | Holds | Data type |
|---|---|---|
| [components/](components/README.md) | Part masses, positions, wood densities | YAML |
| [fields.yaml](fields.yaml) | Measurement field spec for writer/UI inputs | YAML |
| [conftest.py](conftest.py) | Pytest temp-root selection for agent environments | Python |
| [src/frame_tools/](src/frame_tools/README.md) | The calculation engine | Python |
| [src/fcc/](src/fcc/README.md) | Domain-blind field spec and writer support | Python |
| [tests/](tests/README.md) | Design invariants | Python |
| [fusion_scripts/](fusion_scripts/README.md) | Scripts that run *inside* Fusion | Python (in Fusion) |
| [docs/](docs/README.md) | Measurements in, lessons out | Markdown |
| [docs/project/](docs/project/README.md) | Mission, scope, and source-of-truth hierarchy | Markdown |
| [docs/knowledge/](docs/knowledge/README.md) | Export contract for a separate knowledge project | Markdown |
| [docs/brainstorming/](docs/brainstorming/README.md) | Feature ideas before planning | Markdown |
| [docs/protocol/](docs/protocol/README.md) | Plan-Gate-Verify method | Markdown |
| [docs/claude/](docs/claude/README.md) | Claude planner/verifier docs | Markdown |
| [docs/codex/](docs/codex/README.md) | Codex plans, gates, error fixes | Markdown |
| [cad/](cad/README.md) | Fusion exports | Binary CAD |
| [dxf/](dxf/README.md) | 2D cut files | Vector |
| [photos/](photos/README.md) | Part photos + sourced web references | Raster |

`pytest` fails if a folder is missing its README or its portal table, so the
index cannot silently rot.
