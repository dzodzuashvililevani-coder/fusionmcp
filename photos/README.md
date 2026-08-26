# photos/

**Purpose:** Visual reference. What the salvaged parts actually look like,
and any diagrams pulled from the web.

**Data stored here:** **Raster** -- `.jpg`, `.png`. Binary, not diffable.
Downscale to ~1500px before committing; a phone photo is 4MB and git keeps
every version forever.

## Portals

| Portal | Folder | Type | Holds | Source |
|---|---|---|---|---|
| `myphotos____` | [own/](own/) | Raster | Your photos of the actual parts | Your camera |
| `refs____` | [reference/](reference/) | Raster | Pinouts, wiring diagrams, datasheet pages | **Downloaded** -- see below |

## own/ -- photograph the real parts

Always include a **ruler or caliper in frame**. A photo without scale is
almost useless when you are trying to recall a dimension three weeks later.

```
motor_base.jpg          bolt pattern, ruler alongside
fc_top.jpg              board with mounting holes visible
fc_bottom.jpg           solder pads -- you will need this for wiring
battery.jpg             with dimensions visible
wood_grain.jpg          grain direction of your stock
assembly_step3.jpg      progress shots, referenced from the build log
```

Link them from [`docs/build-log.md`](../docs/build-log.md) and
[`docs/measurements.md`](../docs/measurements.md).

## reference/ -- images from the internet

**Every downloaded file needs a source line.** Add it to `reference/SOURCES.md`
with the same filename:

```markdown
| File | Source URL | Retrieved | Note |
|---|---|---|---|
| betaflight_pinout.png | https://... | 2026-08-24 | F411 board, matches mine |
```

Two reasons this matters:

1. **Attribution.** These are someone else's images. If this repo ever goes
   public, an unsourced diagram is a copyright problem.
2. **Verification.** A pinout diagram for the *nearly* right board will destroy
   your flight controller. The URL is how you re-check that it actually matches.

Never put a downloaded image in `own/`. The whole point of the split is knowing
which images you can trust as ground truth about *your* hardware.
