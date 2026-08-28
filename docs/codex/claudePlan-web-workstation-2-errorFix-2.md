# Error fix 2 for Web measurement workstation

**Targets:** Phases 4 and 5 of `claudePlan-web-workstation-2.md`
**Created:** 2026-08-28
**Severity:** major — a normative spec was overridden for an unnamed reason, and
the gate that would have recorded it was not written
**Scope:** `web/src/styles.css`, the plan file, and one disclosure decision

> **The app is well built.** `npm.cmd --prefix web run build` succeeds (9.6 kB
> CSS, 205 kB JS), the render test genuinely proves criterion 17 by rendering an
> invented field with an invented unit, `api.ts` is the only file that touches
> `fetch`, the 250 ms preview debounce from W2 is there, Enter saves via a real
> form submit, and the Phase 7 viewer slot is reserved. **Do not redesign
> anything.** This fix is two items.

## 1. What's wrong (observed)

### E1 — every letter-spacing value in the spec was overridden to `0`

`docs/design/workstation-visual-spec.md` section 3 tabulates tracking as part of
the type scale. `web/src/styles.css` sets `letter-spacing: 0` in all six places
that carry it:

| Selector | Spec | Built |
|---|---|---|
| `.field-card h2` (field question) | `-0.018em` | `0` |
| `.topline h1` (app title) | `-0.015em` | `0` |
| `.section-label` (10px uppercase mono) | `0.15em` | `0` |
| `.field-group h3` (9.5px uppercase mono) | `0.15em` | `0` |
| `.notice strong` (uppercase mono tag) | `0.12em` | `0` |
| line 214 | per its role | `0` |

The stated reason was *"to satisfy the active frontend constraint."*

**No such constraint exists in this project.** I searched the plan, the visual
spec, `docs/project/architecture.md`, `CLAUDE.md`, and `docs/protocol/`. There is
no rule about letter-spacing anywhere in the repository.

The two uppercase-monospace label cases are not cosmetic. Letterspacing small
uppercase text is a legibility measure — at 9.5px and 10px, set in a monospace
face, in all caps, tracking is what keeps the label readable rather than a grey
bar. Those labels are the section headers of every pane in a tool meant to be
read across a workbench.

Criterion 23 permits deviation: *"Deviations are allowed but must be listed in
the gate report with a reason."* Two things went wrong against that. There is no
gate report (E2). And "the active frontend constraint" is not a reason a reader
can evaluate — it names no rule, cites no source, and cannot be checked.

**This is not a complaint about the value chosen. It is about a normative
document being overridden by an unnamed one.** If a constraint outside this
repository governs the code in it, the repository has to know about it, or every
future spec is written against rules its author cannot see.

### E2 — Phase 5 never happened

The plan's Phase 5 is a hard halt:

> **Definition of done:** gate report appended, then halt

No `### Phase 5 gate report` section exists. The plan's status line still reads
`phase-4-open`. Every command output, every count, and the deviation disclosure
itself currently exist **only in chat**.

`docs/protocol/trust-boundaries.md` opens with *"Keep durable state in repo
files, not chat."* `docs/claude/behaviour.md` forbids me from skipping a gate.
This is the same class of mistake I made by putting the visual spec behind a
private URL, and it has the same fix: write it down where the next person can
read it.

## 2. Why it's wrong (root cause)

**E1:** an external rule was applied silently in place of the project's own. The
honest failure is not the flattening — it is that a reader of `styles.css` has
no way to learn why it disagrees with the spec it is measured against.

**E2:** the implementation ran past its gate. The work was done and verified;
the record was not written.

## 3. What to change

### 3.1 Restore the spec's tracking, or name the constraint

Pick one. Both are acceptable; silence is not.

**Option A — restore.** Set the six declarations to the values in the spec's
type-scale table. This is the default and needs no further justification.

**Option B — the constraint is real.** Then name it: what rule, imposed by what,
applying to what. Record it as a decision in the gate report **and** amend
`docs/design/workstation-visual-spec.md` so the spec and the code agree. A
normative document that the code silently contradicts is worse than no document.

If Option B, also say whether the constraint permits `letter-spacing` at all or
only certain values — because if uppercase micro-labels cannot be tracked, the
right answer is to stop setting them in uppercase at 9.5px, not to keep an
unreadable label.

**Do not split the difference.** Either the spec's values or a named rule.

### 3.2 Decide the font question and record it

`styles.css` declares `Archivo` and `IBM Plex Mono` but ships neither, so the
page renders in the fallback stack on most machines and in the named faces on
machines that happen to have them installed. That is **inconsistent rendering of
a page whose conformance is an acceptance criterion**.

Criterion 26 is satisfied either way — there is no external URL, and
`test_web_source_and_shell_have_no_external_urls` proves it. But pick one and
say so:

- **Self-host** both families under `web/src/` and add `@font-face`. Consistent
  everywhere, costs repository weight.
- **Drop the family names** and commit to the fallback stacks. Consistent
  everywhere, costs the intended look.

Keeping the current state is the only option that must be ruled out, because it
makes "matches the spec" depend on what the viewer has installed.

### 3.3 Write the Phase 5 gate report

Append it to the plan with the sections the plan requires: commit SHA, files
changed, test output, self-assessment, open questions. It must include, verbatim:

- `npm.cmd --prefix web install`, `run gen:types`, `run build`, `test`
- both canonical commands and `tests/test_privacy.py`
- `git status --short` and `git diff --stat`
- `git diff -- params.yaml components/loadout.yaml docs/measurements.md fields.yaml`
- **every deviation from the visual spec, with a reason** — the tracking
  decision from 3.1, the font decision from 3.2, and anything else
- whether both themes were checked, and how
- whether `web/dist` and `node_modules` are correctly ignored

Then set the plan status and halt.

### 3.4 Not in scope

- Do not touch the components, `api.ts`, the tests, or `api.d.ts`.
- Do not start Phase 7.
- Do not change the token values, the layout, or the breakpoints. They match.

## 4. Acceptance for this fix

1. Every `letter-spacing` declaration in `web/src/styles.css` either matches the
   spec's type-scale table, or the gate report names the constraint that
   prevents it **and** the spec is amended to agree.
2. The font question is decided, implemented, and stated in the gate report.
3. A `### Phase 5 gate report` section exists in the plan with all the content
   listed in 3.3.
4. `npm.cmd --prefix web run build` succeeds; `npm.cmd --prefix web test` passes.
5. Canonical commands clean:

   ```powershell
   .\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
   .\.venv\Scripts\python.exe -m frame_tools.cli report
   ```

6. `tests/test_privacy.py` passes.
7. `git diff -- params.yaml components/loadout.yaml docs/measurements.md fields.yaml`
   is empty.

## 5. Do NOT

- **Do not silently follow an unnamed rule again.** If something outside this
  repository constrains the code in it, that belongs in the gate report the
  first time it bites, not in a chat message.
- **Do not delete the letter-spacing lines** to make the question go away.
  `letter-spacing: 0` and no declaration at all are the same rendering and the
  same problem.
- **Do not weaken the spec to match the code.** Amending the spec is allowed
  only as Option B, with the constraint named.
- **Do not add a CDN font link.** Criterion 26, and a test enforces it.
- **Do not skip the gate again.** The halt is the point of the gate.
