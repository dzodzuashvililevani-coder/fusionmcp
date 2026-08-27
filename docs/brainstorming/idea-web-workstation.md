# Idea: web measurement + design workstation

**Created:** 2026-08-27
**Status:** ready-for-plan
**Author:** Claude (planner), from a brief by the user
**Routed to:** `docs/codex/claudePlan-web-workstation-1.md`

## Problem

Getting a real measurement into this project costs four context switches: read
the caliper, find the right blank in `docs/measurements.md`, find the matching
key in `params.yaml` (13 `TODO`s) or `components/loadout.yaml` (6 `TODO`s), then
run `frame report` in a terminal and read the result. Nothing tells you *which*
dimension a key means -- is `bolt_circle_mm` measured hole-centre to hole-centre
across the base, or between adjacent holes? -- so the highest-risk step in the
whole build is a human mapping an ambiguous label onto a physical part from
memory.

Three consequences follow:

- **Mis-mapping is invisible.** A wrong-but-plausible number passes every check
  in `validate.py`, because the validator tests relationships between numbers,
  not whether a number describes the thing its name claims.
- **The feedback loop is too slow to explore with.** Changing a prop diameter to
  see what it does to arm radius means editing YAML and re-running a command.
- **Photos are inert.** `photos/own/` exists and has a "ruler in frame" rule,
  but nothing connects an image to the parameter it is evidence for.

## Desired outcome

One local page, open on a second monitor while the calipers are in hand, that:

1. asks for one measurement at a time, in plain language;
2. shows a 3D model of that component with the exact dimension being asked for
   highlighted and animated, so the label is unambiguous;
3. writes the answer into `docs/measurements.md`, `params.yaml`, and
   `components/loadout.yaml` without destroying the hand-written comments;
4. re-runs validation on every save and shows the consequence immediately;
5. accepts phone photos with a note per photo, filed against the parameter they
   evidence;
6. supports a conversation about the design once the numbers are in.

## Rating

**Core (measurement capture + live validation + photo intake): 8/10.**
**"Workstation for everything I ever create": 4/10 as stated.**

### What is genuinely strong

- **It targets the real defect, not a cosmetic one.** The weak link in this repo
  is the human-to-YAML transcription step, and it is weak precisely because it
  is the one step with no machine check on it. A UI that shows the dimension
  while asking for it is not a convenience -- it is the missing validation layer
  for the class of error `validate.py` structurally cannot catch.
- **The architecture already has a slot for it.** `CLAUDE.md` says a browser
  tool goes in a new `web/` folder with its own README. This is an anticipated
  extension, not a graft.
- **Live validation makes the design explorable.** `frame check` takes about a
  second but costs a context switch. Rendered next to the input, the same
  numbers become a design tool: change prop diameter, watch arm radius and TWR
  move. That is a different activity from checking, and it is the single
  highest-value item on the list.
- **The 3D model can do double duty.** See "The idea inside the idea" below.

### What is weaker than it sounds

- **The 3D models are the expensive half and the softer value.** Component
  viewers with animated dimension callouts are most of the build effort and
  deliver, at bottom, one thing: disambiguation of a label. A well-drawn static
  SVG diagram per measurement delivers perhaps 70% of that for perhaps 10% of
  the effort. Worth building -- just not first, and worth knowing what it buys.
- **In-UI chat duplicates a tool that already exists.** You already talk to
  Claude in this repo, with filesystem access and the ability to run
  `frame report`. A chat box in the web UI needs an API key, a key store, an
  agent loop, a conversation history, and a new outbound trust boundary -- to
  arrive at a strictly weaker version of the session you are already in. The
  genuine gap it fills is *co-location*: talking about the design without losing
  sight of the numbers. That gap is better closed by putting the live validation
  output and a design-notes field on the same page, and letting the real
  conversation stay in the terminal.
- **"My workstation for everything I create" is a different product.** What
  makes this repo good is that `params.yaml` is a single source of truth and
  every number downstream is derived from it and validated against physics. A
  generic creation workstation has no `params.yaml`, no domain validator, and no
  equivalent of `frame check` -- it is a file manager with a chat box. The parts
  that generalise are the *method*, not the UI. See "Generalisation" below.

### The idea inside the idea

The strongest thing in the brief is not stated as a feature: **the 3D model and
the parameter file should be the same object.** If the component model is drawn
*from the current parameter values* rather than being a pre-made static asset,
then typing a 9 mm bolt circle on a 12 mm motor base draws four holes hanging
off the edge of the base, and the error is visible before it is ever saved. The
model stops being an illustration and becomes a second validator, catching
exactly the errors the numeric one cannot.

This costs less than pre-made models, not more: a motor is a cylinder plus a
bolt circle, a battery is a box, an FC is a plate with four holes. All are
primitives driven by numbers already in `params.yaml`.

## Gaps I am filling

Decisions the brief did not specify that must be settled before implementation.

### 1. Writing back to `params.yaml` will destroy it, unless handled

`src/frame_tools/params.py` reads with `yaml.safe_load`. There is no writer. The
obvious implementation -- load, mutate, `yaml.dump` -- silently deletes every
comment in the file. Those comments are load-bearing documentation:
`TODO measure with caliper`, `laser ~0.15-0.25, CNC = endmill dia`, the prop
size conversions. Losing them makes the file materially worse than before the
feature existed.

**Decision: a surgical line-level writer, not a YAML round trip.** Locate the
key's line, replace only the value on that line, leave every other byte
untouched. Zero new dependencies, and it yields a hard, testable property:
*every byte of the file outside the edited value is unchanged*. It must refuse
loudly on anything it cannot address surgically rather than falling back to a
reformat. (`ruamel.yaml` is the fallback only if a nested case appears;
`params.yaml` is currently flat scalars and short inline lists, so none exists.)

### 2. A saved measurement that fails validation must still save

Tempting rule: block a save that makes `frame check` fail. Wrong rule.
Measurements are facts about physical objects. If the real motor produces a TWR
of 1.8, the file must record 1.8 and the UI must say loudly that the design is
unflyable. Blocking the save teaches the user to fudge numbers until the
validator goes quiet, which is the precise failure mode `frame check` exists to
prevent. **Save the fact, shout about the consequence.**

### 3. One field spec, or the UI forks the source of truth

If the UI hardcodes its own list of fields, units, and ranges, then
`params.yaml` is no longer the single source of truth -- there are two, and they
drift. **Decision: one declarative spec** that owns, per measurement: the human
question, the units, the `params.yaml` key path, the matching label in
`docs/measurements.md`, a plausible range, and which 3D dimension it drives. The
form, the writer, the checklist updater, and the 3D highlight all read that one
spec. Adding a parameter later means adding one row.

### 4. `docs/measurements.md` is a checkbox document, not a data file

Its lines look like `- [ ] Bolt circle (hole to hole, across the base): ____ mm`.
Filling one in means finding the label, rewriting the blank, and ticking the
box. If a label is not found the writer must report it, never skip silently. The
field spec from gap 3 owns that label mapping.

### 5. Adding `web/` breaks two structural rules

`CLAUDE.md` states "There is no JavaScript in this project", and
`tests/test_structure.py` enforces a `DATA_TYPES` vocabulary with no tag for web
assets. A `web/` folder therefore requires, in the same change: a new type tag
in the CLAUDE.md vocabulary table, the same tag added to `DATA_TYPES`, the "no
JavaScript" line updated, a `web/README.md` with a Purpose line and a Portals
table, and a new row in the CLAUDE.md portal table. Miss any one and the gate
fails on `test_structure.py`.

### 6. Trust boundaries apply directly

`docs/protocol/trust-boundaries.md` was written for exactly this. A web UI that
writes files and accepts uploads must: bind `127.0.0.1` only, never `0.0.0.0`;
refuse `..` traversal and any write outside the project root; refuse `.git/`,
`.venv/`, and local tool directories; pass user input to subprocesses as
arguments, never as shell strings; and set a timeout on every subprocess call.
Photo upload additionally needs an extension allowlist and a size cap.

### 7. iPhone photos need an ingest step, not a copy step

All three problems from the earlier photo analysis still apply. `.HEIC` is
unreadable by the tools here and must be converted to JPG. EXIF carries the GPS
coordinates of wherever the photo was taken, which is precisely what
`tests/test_privacy.py` exists to keep out of the repo but cannot see, because
it scans text files only. And a 4 MB phone photo lands in git history
permanently. Ingest must convert, strip EXIF, downscale, and rename to the
`photos/own/README.md` convention -- and `test_privacy.py` should grow a check
that fails on any tracked image still carrying EXIF GPS.

### 8. There is a live blocker in the environment

`.pytest-run-tmp/` is currently unreadable to its own owner. `Get-Acl`,
`Get-ChildItem`, `Remove-Item`, `takeown`, and `icacls` are denied. Windows
Application Control also blocks the generated `.venv\Scripts\frame.exe` shim.

The protocol now uses canonical Python module commands that avoid both
environment faults:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

## Constraints

- `params.yaml` stays the single source of truth. The UI is an editor for it,
  never a second store.
- Geometry is solved exactly once, in `geometry.py`. The UI displays solver
  output; it never recomputes a dimension.
- Comments and formatting in the three hand-edited data files survive every
  write.
- Committed defaults keep passing `frame check`.
- Minimal dependencies. The project has one runtime dependency (`pyyaml`).
  Prefer `http.server` from the standard library over a web framework, and
  vendored assets over a package manager.
- Local only. Single user, no auth, no external binding.
- `test_structure`, `test_privacy`, and `test_protocol` must keep passing, and
  the new folder must satisfy them.

## Candidate acceptance checks

- `frame ui` serves on `127.0.0.1` and exits non-zero if the port is taken.
- Submitting a measurement changes exactly one value in `params.yaml`; a byte
  comparison of the rest of the file shows no other difference.
- Every comment present in `params.yaml` before a write is present after it.
- Submitting a measurement ticks the matching box in `docs/measurements.md` and
  writes the value into its blank.
- A measurement whose label is missing from `docs/measurements.md` is reported
  as an error, not skipped.
- A value that makes `frame check` fail is still written, and the UI shows the
  failure text from `validate.py` verbatim.
- After a full round of inputs, `grep -c TODO params.yaml` returns 0 and
  `python -m frame_tools.cli report` exits 0.
- A request for a path outside the project root is refused.
- An uploaded `.HEIC` becomes a downscaled `.jpg` in `photos/own/` with no EXIF.
- `python -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp`
  passes with the new `web/` folder present.

## Generalisation: the honest version of "workstation for everything"

The ambition is right; the framing needs one correction. What generalises is not
a UI that handles any project -- it is this project's *shape*:

```
typed parameter file -> solver -> validator -> generated handoff -> CAD/CAM
```

`drone-wood-frame` is one instance. A second instance is a different
`params.yaml`, a different `geometry.py`, a different `validate.py` -- and the
same UI, the same writer, the same field-spec mechanism, the same gate protocol.

So the path to a general workstation is: build it *concretely* for the drone
frame first, then extract the parts that turn out to have had no drone in them.
Anything built generically before it has been made to work once will generalise
to the wrong thing. Concretely: the field spec, the surgical writer, the photo
ingest, and the server are written domain-blind from the start, while the 3D
primitives and the field list stay drone-specific until a second project proves
what they share.

Fusion 360 output already works this way: `frame fusion` writes
`frame_params.json`, `sync_params.py` consumes it. A future 3D-printer path is
another consumer of the same handoff, not a new source of truth -- which is what
makes it plausible.

## Proposed plan sequence

| Plan | Slug | Delivers | Depends on |
|---|---|---|---|
| 1 | `web-workstation` | Field spec, surgical writer, local server, minimal form, live `frame check` panel | env blocker cleared |
| 2 | `web-photo-ingest` | Upload with a note per photo, HEIC to JPG, EXIF strip, downscale, privacy test extension | 1 |
| 3 | `web-3d-viewer` | Parametric component primitives, animated dimension highlight per field | 1 |
| 4 | `web-design-notes` | Design-intent capture and a change journal on the same page | 1 |
| 5 | `web-chat` | In-page conversation, only if plans 1-4 leave a real gap | 1, 4 |

Plan 1 is the spine: every later plan consumes its field spec and its writer. It
is scoped deliberately narrow so the first gate is small and the writer's
byte-exactness property is verified before anything is built on top of it.

## Next routing step

Plan 1 is written: `docs/codex/claudePlan-web-workstation-1.md`. Plans 2-5 stay
unwritten until plan 1 reaches a PASS sign-off, per `docs/claude/behaviour.md`
(one plan per feature).
