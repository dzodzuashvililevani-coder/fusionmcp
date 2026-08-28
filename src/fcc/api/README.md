# src/fcc/api/

**Purpose:** Domain-blind HTTP API for FCC fields, previews, writes, and injected reports.

**Data stored here:** Python only. This package owns the FastAPI contract and
routes; project-specific report construction is injected by the caller.

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `package____` | [__init__.py](__init__.py) | Python | Public app factory export |
| `app____` | [app.py](app.py) | Python | FastAPI factory and OpenAPI metadata |
| `models____` | [models.py](models.py) | Python | Pydantic request and response models |
| `routes____` | [routes.py](routes.py) | Python | Field, preview, write, report, and health endpoints |
