# Measurement workstation — visual spec

**For:** roadmap Phase 2, `claudePlan-web-workstation-2.md` Phase 4
**Created:** 2026-08-28
**Status:** normative — this file is what criterion 23 is measured against
**Reference rendering:** [workstation-mockup.html](workstation-mockup.html)

> **This file is the spec. The mockup is a picture of it.** Where they disagree,
> this file wins. Open the mockup in a browser to see the intent; read this to
> know the numbers. **Do not copy the mockup's markup into React** — it is a
> static page with canned data and hand-rolled DOM building. Take the tokens,
> the type scale, the spacing, the layout, and the states.

---

## 1. Why the page looks like this

The subject is a workshop instrument, not a web app. The palette is a
machinist's bench: a grey-green ground the colour of a granite surface plate,
graphite ink, and one accent borrowed from layout dye. Nothing is rounded,
nothing glows, and there is exactly one accent colour — because the page is read
in a garage with calipers in hand and every coloured thing on it should mean
something.

Semantic colour (ok / warn / fail) is separate from the accent and is the only
other colour on the page.

---

## 2. Colour tokens

Define these as CSS custom properties. **Every colour in the app comes from this
table**; no component may declare a literal.

### Light (bare `:root`)

| Token | Value | Used for |
|---|---|---|
| `--ground` | `#E8EAE6` | Page background behind the panes |
| `--shell` | `#FBFBF9` | Pane background |
| `--panel` | `#F3F5F1` | Hover fill inside panes |
| `--sunken` | `#E1E4DE` | Code blocks, progress track, inline code |
| `--ink` | `#191B1A` | Body text |
| `--muted` | `#5C6360` | Secondary text, check details |
| `--faint` | `#878E8A` | Labels, units, disabled |
| `--rule` | `#D2D6CF` | Hairline borders |
| `--rule-firm` | `#B7BDB6` | Emphasised borders, input underline |
| `--accent` | `#2D4B8E` | The single accent: links, focus, primary button, active rail item |
| `--accent-ink` | `#FFFFFF` | Text on `--accent` |
| `--accent-soft` | `#DFE7F4` | Active row fill |
| `--ok` | `#3E6B4A` | Passing check, measured status |
| `--ok-soft` | `#DDE9DE` | Passing tag background |
| `--warn` | `#8A6113` | Warning check, out-of-range notice |
| `--warn-soft` | `#F1E6CC` | Warning tag background |
| `--fail` | `#A33B2E` | Failing check, removed diff line |
| `--fail-soft` | `#F3DEDA` | Failing tag background |

### Dark

Redefine **only** the tokens. Same names, same roles.

| Token | Value | | Token | Value |
|---|---|---|---|---|
| `--ground` | `#0E100F` | | `--accent` | `#7CA1E4` |
| `--shell` | `#171A19` | | `--accent-ink` | `#0E1521` |
| `--panel` | `#1B1F1D` | | `--accent-soft` | `#1B2536` |
| `--sunken` | `#101312` | | `--ok` | `#72A87F` |
| `--ink` | `#E7EAE5` | | `--ok-soft` | `#17251A` |
| `--muted` | `#9AA29D` | | `--warn` | `#C79A46` |
| `--faint` | `#757C78` | | `--warn-soft` | `#2A2214` |
| `--rule` | `#282D2B` | | `--fail` | `#D9776A` |
| `--rule-firm` | `#3A413D` | | `--fail-soft` | `#2C1917` |

### The three-state rule (criterion 24)

The viewer has three states, not two. An explicit choice stamps
`data-theme="dark"` or `data-theme="light"` on the root; the default "system"
setting stamps **nothing**, and only `prefers-color-scheme` separates light from
dark there. So:

```css
:root { /* complete light palette */ }

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) { /* dark tokens */ }
}

:root[data-theme="dark"] { /* dark tokens again */ }
```

Style components through the tokens only. **A colour whose only definition sits
inside a media query or a `[data-theme]` block never applies in the un-stamped
state** — that is the classic unreadable-page bug. Before finishing, grep the
stylesheet for any colour declared only inside such a block.

`body` must set an explicit `background: var(--ground)`.

---

## 3. Typography

Two faces. One grotesque for the interface, one monospace for anything that is
data: values, units, file paths, diffs, field ids, labels.

| Role | Family | Fallback stack |
|---|---|---|
| Interface | **Archivo** | `"Helvetica Neue", Arial, sans-serif` |
| Data / labels | **IBM Plex Mono** | `"SFMono-Regular", Consolas, monospace` |

**Criterion 26 forbids a font CDN.** The mockup links Google Fonts; the app must
not. Either self-host the two families under `web/src/` or drop to the fallback
stacks. Weights used: Archivo 400/500/600/700, Plex Mono 400/500/600.

> **Decided for Phase 2 on 2026-08-28: the fallback stacks, not the named
> families.** `web/src/styles.css` ships
> `"Helvetica Neue", Arial, sans-serif` and
> `"SFMono-Regular", Consolas, monospace`, and names Archivo and IBM Plex Mono
> nowhere. Naming a family the app does not ship makes rendering depend on what
> the viewer happens to have installed, which turns spec conformance into a
> property of someone's font folder. **Do not add the family names back without
> shipping the files.** Recorded in the errorFix-2 Phase 5 gate report.

### Scale

| Element | Size | Weight | Tracking | Notes |
|---|---|---|---|---|
| Field question | `1.62rem` | 600 | `-0.018em` | `text-wrap: balance`, `max-width: 22ch` |
| Value input | `2.1rem` | 500 | — | Mono, `font-variant-numeric: tabular-nums` |
| App title | `1.16rem` | 700 | `-0.015em` | |
| Headline stat | `1.06rem` | 600 | — | Mono, tabular-nums |
| Body / check name | `13–15px` | 400–500 | — | |
| Check detail | `12px` | 400 | — | `--muted`, line-height 1.4 |
| Code / diff | `12–12.5px` | 400 | — | Mono, line-height 1.6–1.65 |
| Section label | `10px` | 600 | `0.15em` | Mono, uppercase, `--faint` |
| Group label | `9.5px` | 400 | `0.15em` | Mono, uppercase, `--faint` |

Base body size `15px`, line-height `1.5`.

**Every column of digits gets `font-variant-numeric: tabular-nums`** — values in
the queue, headline stats, line numbers. Numbers that jitter while you type read
as broken.

---

## 4. Layout

Three panes, `20px` gap, page `max-width: 1560px`, padding `22px 20px 60px`.

```
+--------------------------------------------------------------------+
|  mock bar (mockup only - not in the app)                            |
+--------------------------------------------------------------------+
|  brand                                    progress "n of 21"  [==-] |
+------------+--------------------------------+----------------------+
| TO MEASURE | CURRENT MEASUREMENT            | DESIGN STATE         |
| 268px      | flexible                       | 350px                |
|            |                                |                      |
| grouped    | writes to params.yaml:11       | [stat] [stat]        |
| field list | Measure actual wood stock...   | [stat] [stat]        |
| w/ status  | stock_thickness                |                      |
| dot +      |                                | [ ok ] prop clearance|
| current    |   2.7  mm   expected 1-8 mm    |        detail...     |
| value      |                                | ...10 checks         |
|            | [warn] out of range...         |                      |
|            |                                | n passed, n warnings |
|            | WHAT THIS WILL CHANGE          | (banner if failing)  |
|            |   params.yaml line 11          |                      |
|            |   - old line                   |                      |
|            |   + new line                   |                      |
|            |   measurements.md - / +        |                      |
|            |                                |                      |
|            | [Save measurement] [Skip]      |                      |
|            | (saved confirmation)           |                      |
|            +--------------------------------+                      |
|            | reserved: Phase 7 viewer slot  |                      |
+------------+--------------------------------+----------------------+
```

Panes: `background: var(--shell)`, `1px solid var(--rule)`, **no border radius,
no shadow.** Each pane has a header bar with an uppercase mono label on the left
and a small `--faint` hint on the right.

### Responsive

| Breakpoint | Change |
|---|---|
| `<= 1200px` | Report pane drops to full width below; stats become a 4-across row |
| `<= 800px` | Single column; queue capped at `300px` scroll; question drops to `1.35rem` |

The page body must never scroll horizontally. Diffs and any wide content scroll
inside their own `overflow-x: auto` container.

---

## 5. Components and their states

### Field queue (left)

- Grouped by the `group` value the API returns, with a mono uppercase group
  label. **Do not hardcode group names** — render whatever the server sends.
- Each row: an 8px status dot, the field id in mono, the current value + unit
  right-aligned in mono.
- Dot is `--rule-firm` for `todo`, `--ok` for `measured`. Value text turns
  `--ok` and weight 600 when measured.
- Active row: `--accent-soft` fill and a 2px `--accent` left border.
- Rows are `<button>` elements, keyboard reachable, `:focus-visible` outlined.

### Field card (centre)

| State | Appearance |
|---|---|
| Default | Target `file:line` in accent mono above; question; field id in `--faint` mono; big mono input with unit and expected range beside it |
| Focused input | Underline `--rule-firm` → `--accent` |
| Empty / non-numeric | Diff block shows `enter a number to preview the change` in `--faint`; no warning shown |
| Out of range | Warning strip: `--warn-soft` fill, 3px `--warn` left border, uppercase mono `WARN` tag, text naming the field, the range, and that it will still be saved |
| Preview | Two blocks: the data file (`- old` in `--fail`, `+ new` in `--ok`) and the checklist line. When the field has no `measurement_label`, the second block reads `docs/measurements.md — no checklist line for this field` in `--faint` |
| Saved | `--ok-soft` strip, 3px `--ok` border, uppercase mono `SAVED`, naming the file and line and whether the checklist was ticked |
| Stale (409) | Same strip pattern in `--fail`: the files changed outside the app, with a reload control |

Primary button: `--accent` fill, `--accent-ink` text, square corners, 600
weight. Secondary: transparent with a `--rule-firm` border.

Enter saves. A hint in `--faint` mono states the shortcuts.

### Report panel (right)

- Four headline stats in a 2×2 grid, each a mono uppercase label over a mono
  tabular value with the unit as a smaller `--muted` suffix. **Labels and units
  come from `/api/report`**, not from the TypeScript.
- Checks: a 46px status tag column plus name and detail. Tag backgrounds are
  `--ok-soft` / `--warn-soft` / `--fail-soft` with matching text colour.
- Tally row: passed / warnings / failures in their semantic colours, mono,
  tabular.
- Failure banner appears only when a check has failed, `--fail-soft`, stating
  the design does not validate and the measurement was saved.

### Reserved slot

A dashed `--rule-firm` box below the field card, `--faint` mono text naming what
goes there and that it is Phase 7. It is a placeholder, not a feature — do not
put a canvas, an image, or a loading state in it.

---

## 6. What the mockup does that the app must not

| Mockup | App |
|---|---|
| Google Fonts `<link>` | Self-host or system stack — criterion 26 |
| Canned check data in a JS object | Everything from `/api/report` — criterion 21 |
| "Report state" dropdown in the blue bar | Delete. It exists to show three states in a static page |
| Blue "Mockup" bar | Delete |
| Field data inlined as JSON | `GET /api/fields` — criterion 17 |
| Diff spliced in JS | `POST /api/fields/{id}/preview`, debounced 250 ms — decision W2 |
| Hand-built DOM | React components |

---

## 7. Deviations

Deviating is allowed where the browser, React, or accessibility makes the spec
wrong or ugly. **Every deviation goes in the Phase 5 gate report with a reason.**
Silent deviation is the thing this file exists to prevent.
