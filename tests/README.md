# tests/

**Purpose:** Guard the design invariants -- the things that must stay true no
matter what numbers end up in `params.yaml`.

**Data stored here:** Python, pytest. Runs in the project venv.

## Portals

| Portal | File | Type | Asserts |
|---|---|---|---|
| `geomtest____` | [test_geometry.py](test_geometry.py) | Python | Props clear, plate clears, motors symmetric, mass/thrust consistent |
| `fusiontest____` | [test_fusion.py](test_fusion.py) | Python | The Fusion payload and the kerf DXF -- where numbers leave for a machine |
| `scripttest____` | [test_fusion_scripts.py](test_fusion_scripts.py) | Python | Runs `fusion_scripts/` against a fake Fusion |
| `stub____` | [fusion_stub.py](fusion_stub.py) | Python | The fake `adsk` package. Not a test -- a fixture |
| `doctest____` | [test_structure.py](test_structure.py) | Python | Every folder has a README with a portal table |
| `privacytest____` | [test_privacy.py](test_privacy.py) | Python | No committed secrets, emails, or local machine paths |
| `protocoltest____` | [test_protocol.py](test_protocol.py) | Python | Plan-Gate-Verify folders and templates keep their contracts |

## Run

```powershell
pytest -q
```

## Testing code that needs Fusion

`fusion_scripts/` imports `adsk`, which exists only inside Fusion, so those
files can never be imported by the venv directly. `fusion_stub.py` installs a
fake `adsk` into `sys.modules` first, implementing only the API surface the
scripts actually touch.

That catches what usually breaks: a payload key that no longer exists, a format
string with the wrong field, a centimetre where a millimetre was meant. It
cannot tell you whether Fusion behaves the way the script assumes -- so a green
run means "it will not crash", not "the model is right". One careful pass in
Fusion on a throwaway design is still owed.

## What belongs here vs in validate.py

They look similar. They are not.

| | `validate.py` | `tests/` |
|---|---|---|
| Checks | *This specific design* is buildable | *The code* is correct |
| Fails when | Your numbers are bad | A calculation is broken |
| Fix by | Editing `params.yaml` | Editing the Python |
| Run by | `frame check`, at the bench | `pytest`, after a code change |

One test spans both: `test_shipped_design_passes_its_own_validator` asserts the
committed `params.yaml` has zero failures. It is a *test*, not a check, because
a repo whose default numbers do not pass is a broken repo, not a bad design.

"TWR is 1.4" is a `validate.py` failure -- the math is fine, the drone is too
heavy. "Motors are not equidistant from the centre" is a test failure -- the
solver has a bug.
