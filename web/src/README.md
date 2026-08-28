# web/src/

**Purpose:** React source and generated API contract files for the browser
measurement workstation.

**Data stored here:** TypeScript components and fetch wrappers, CSS tokens, and
generated JSON/TypeScript API contract snapshots.

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `main____` | [main.tsx](main.tsx) | TypeScript | React entry point |
| `app____` | [App.tsx](App.tsx) | TypeScript | Workstation state orchestration |
| `apiwrap____` | [api.ts](api.ts) | TypeScript | Typed fetch wrappers for the local API |
| `queue____` | [FieldQueue.tsx](FieldQueue.tsx) | TypeScript | Field list grouped from API data |
| `fieldcard____` | [FieldCard.tsx](FieldCard.tsx) | TypeScript | Current measurement form, diff preview, and save states |
| `report____` | [ReportPanel.tsx](ReportPanel.tsx) | TypeScript | Live design report rendering |
| `styles____` | [styles.css](styles.css) | CSS | Workstation visual tokens, layout, and component states |
| `queuetest____` | [FieldQueue.test.tsx](FieldQueue.test.tsx) | TypeScript | Dynamic field-list render test |
| `apitypes____` | [api.d.ts](api.d.ts) | TypeScript | Generated API TypeScript definitions |
| `openapi____` | [openapi.json](openapi.json) | JSON | Generated OpenAPI contract snapshot |
