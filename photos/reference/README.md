# photos/reference/

**Purpose:** Images pulled from the internet -- pinouts, wiring diagrams,
datasheet pages, build references.

**Data stored here:** Raster (`.jpg`, `.png`), plus one Markdown source ledger.

## Portals

| Portal | File | Type | Holds |
|---|---|---|---|
| `sources____` | [SOURCES.md](SOURCES.md) | Markdown | **Required ledger** -- one row per image, with URL |
| `pinout____` | `*_pinout.png` | Raster | Flight controller / ESC pinouts |
| `wiring____` | `*_wiring.png` | Raster | Wiring diagrams |
| `datasheet____` | `*_datasheet.png` | Raster | Datasheet pages for identified parts |

## Every file needs a row in SOURCES.md

No exceptions. Two reasons:

1. **Attribution** -- these are someone else's images. Unsourced diagrams are a
   copyright problem if this repo goes public.
2. **Verification** -- a pinout for a *similar* board will destroy your flight
   controller. The URL is how you re-check that it matches your board revision.

Treat everything here as **unverified until matched against a photo in
[`../own/`](../own/README.md)**. Salvaged Temu hardware is frequently an
unlabelled clone of something else.
