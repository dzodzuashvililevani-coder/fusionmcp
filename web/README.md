# web/

**Purpose:** Browser workstation package, build configuration, and generated
API contract snapshots.

**Data stored here:** TypeScript, CSS, HTML, JSON package metadata, and
generated API contract files. Built assets are written to `dist/` and ignored.

## Portals

| Portal | Path | Type | Holds |
|---|---|---|---|
| `package____` | [package.json](package.json) | JSON | npm scripts and frontend dependencies |
| `lock____` | [package-lock.json](package-lock.json) | JSON | npm dependency lockfile |
| `tsconfig____` | [tsconfig.json](tsconfig.json) | JSON | TypeScript compiler settings |
| `vite____` | [vite.config.ts](vite.config.ts) | TypeScript | Vite build and dev proxy configuration |
| `index____` | [index.html](index.html) | HTML | Browser entry shell |
| `src____` | [src/](src/README.md) | TypeScript | React workstation source and generated API types |
