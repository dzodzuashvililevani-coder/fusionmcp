# docs/design/

**Purpose:** Visual specifications for anything a human looks at. Decided before
implementation, not during it.

**Data stored here:** Markdown specs and self-contained HTML mockups. A spec in
this folder is **normative** — an implementation plan can point at it and make
"matches the spec" an acceptance criterion. A mockup beside it is a reference
rendering of that spec, never the source of truth and never code to copy.

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `wsspec____` | [workstation-visual-spec.md](workstation-visual-spec.md) | Markdown | Phase 2 measurement workstation: colour tokens, type scale, layout, component states |
| `wsmock____` | [workstation-mockup.html](workstation-mockup.html) | HTML | Reference rendering of that spec. Open it in a browser |

## Rules

- **The Markdown is the spec; the mockup is a picture of it.** Where they
  disagree, the Markdown wins. Numbers live in the Markdown so they can be
  reviewed in a diff.
- **A spec lives in the repository, not behind a link.** A plan that points at
  a URL an implementer cannot open is a blocked plan — that happened once, on
  2026-08-28, and is why this folder exists.
- **Mockups are self-contained and offline.** No CDN, no external asset. If a
  mockup uses something the shipped app may not, say so inside the file.
- **Do not copy mockup markup into the app.** Take the tokens, the scale, the
  spacing, and the states.
- Deviations from a spec are allowed and must be recorded in the gate report of
  the phase that deviated.
