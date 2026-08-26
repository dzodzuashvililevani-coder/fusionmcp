# src/frame_tools/

**Purpose:** The calculation engine. Reads `params.yaml`, solves the frame,
checks it is buildable.

**Data stored here:** Python only, runs in the project venv (`.venv/`).
These modules **cannot** import `adsk.*` -- Fusion's API only exists inside
Fusion. Scripts that need it go in [`fusion_scripts/`](../../fusion_scripts/README.md).

## Portals

| Portal | File | Type | Responsibility | Depends on |
|---|---|---|---|---|
| `params____` | [params.py](params.py) | Python | Find the project root, load + resolve YAML | pyyaml |
| `geometry____` | [geometry.py](geometry.py) | Python | Arm-length solver, motor coordinates | `params` |
| `mass____` | [mass.py](mass.py) | Python | Mass budget, centre of gravity, wood mass estimate | `params`, `geometry` |
| `thrust____` | [thrust.py](thrust.py) | Python | Thrust-to-weight, hover throttle | -- |
| `validate____` | [validate.py](validate.py) | Python | Ten pre-cut design rules | all of the above |
| `fusionout____` | [fusion.py](fusion.py) | Python | Build the `frame fusion` payload + User Parameter table | all of the above |
| `dxfout____` | [dxf_out.py](dxf_out.py) | Python | The kerf coupon. Only DXF that does not come from Fusion | `params`, ezdxf |
| `cli____` | [cli.py](cli.py) | Python | `frame` command, all output formatting | all of the above |

## Dependency direction

```
params  ->  geometry  ->  mass  ->  validate  ->  fusion  ->  cli
                            \        /                          ^
                             thrust                             |
params  ------------------>  dxf_out  ------------------------- +
```

Strictly one-way. Nothing imports `cli`. Adding a cycle means the layering
is wrong.

`ezdxf` is an **optional** dependency and is imported inside the function that
needs it, not at module top level -- so `frame report` still works on a machine
that only installed the base dependency.

## Rules

- **No hardcoded dimensions.** If a number describes the drone, it belongs in
  `params.yaml`. If it describes physics or a rule of thumb, a module constant
  is fine -- comment where it came from.
- **Calculation and printing stay separate.** Modules return dataclasses.
  Only `cli.py` prints.
- Every new rule in `validate.py` needs a one-line reason in its `detail`
  string. A check that fails without explaining why is useless at the bench.
  Write the reason as a *statement of the rule*, not an instruction -- the same
  `detail` is printed when the check passes.
- A constraint the solver can satisfy belongs in `geometry.py`, not only in
  `validate.py`. Shipping a `params.yaml` that fails its own validator makes
  the validator noise that people learn to ignore.

## Adding a calculation

1. New module, or extend an existing one. Return a dataclass.
2. Wire it into `cli.py` `_build_all()`.
3. If it constrains the build, add a `validate.py` check.
4. Add a test to [`tests/`](../../tests/README.md).
5. Add a row to the table above.
