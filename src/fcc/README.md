# src/fcc/

**Purpose:** Domain-blind FusionControlCenter support code.

**Data stored here:** Python only. This package owns field-spec loading,
validation, and later surgical file writes that are not specific to the drone
frame geometry.

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `package____` | [__init__.py](__init__.py) | Python | Package marker and public version |
| `errors____` | [errors.py](errors.py) | Python | Named exceptions for field specs and later writers |
| `fields____` | [fields.py](fields.py) | Python | `fields.yaml` loader, validator, and lookup helpers |
