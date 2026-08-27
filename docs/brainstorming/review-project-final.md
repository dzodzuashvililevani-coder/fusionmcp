# Final review: FusionControlCenter baseline

> **SUPERSEDED IN PART -- 2026-08-28.** Knowledge capture is no longer this
> project's responsibility. It moved to a separate project; this repository only
> deposits finished products into named folders. Anything below that argues for
> building capture, promotion, component cards, or an extractor **here** no
> longer applies. See
> [`decision-scope-split.md`](decision-scope-split.md) for the authority.

**Created:** 2026-08-27
**Reviews:** Codex's `docs/project/`, `docs/knowledge/`, and index changes of 2026-08-27
**Also folds in:** `review-user-1.md`, `review-icm-paper.md`, `idea-web-workstation.md`
**Author:** Claude (verifier role, `docs/claude/verification-checklist.md`)
**Verdict:** **CONDITIONAL PASS** -- content accepted, two process findings must be cleared

---

## 0. Verification evidence

Run against working tree at `496a839` + uncommitted changes. Nothing committed.

| Check | Result |
|---|---|
| `pytest -q --basetemp=.pytest-run-tmp` (**canonical**) | **111 passed, 5 errors** |
| `pytest -q` (default basetemp) | 116 passed, 0 errors |
| `frame report` | 10 passed, 0 warnings, 0 failures, exit 0 |
| `git diff --stat` | 5 files, +56 / -3 |
| Untracked | 10 files across `docs/brainstorming/`, `docs/codex/`, `docs/knowledge/`, `docs/project/` |
| Files inspected | all 10 new files, all 5 diffs, `.pytest-run-tmp` ACL state |

---

## 1. What Codex got right

Real credit, stated plainly before the findings.

- **The sequencing argument was absorbed rather than deflected.** Section 5's
  in-scope/out-of-scope split, and the explicit exclusion of "a permanent
  reusable component library before real build data exists", is exactly the
  correction `review-user-1.md` section 4.1 argued for. The temptation to say
  yes to everything was refused.
- **The verification-state ladder is better than what I proposed.**
  `unverified -> measured -> tested -> verified -> rejected` is a genuine
  improvement on my binary verified flag. `tested` (used in a model or a cut,
  not yet proven) and `rejected` (kept for history, never reused) are both
  states I missed, and both are states hardware work actually produces.
- **The source-of-truth layering in section 3 is the right instinct**, and it
  independently reaches for the same distinction the ICM paper formalises.
  See finding F5.
- **`docs/knowledge/` as a staging area rather than a knowledge base** is the
  correct answer to "prepare for the extractor without building it".
- **The index discipline held.** Five index files updated in the same change,
  new folders documented, portal tables extended. Nothing was left dangling.
- **Codex disclosed that it did not commit.** Good.

The substance is sound. Everything below is refinement or process.

---

## 2. Findings

Ordered by severity. F1 and F2 are the conditions on the pass.

### F1 -- blocker -- the canonical gate command still fails, and the reported number came from a different command

Codex reported `pytest -q --basetemp=.pytest-run-tmp: 116 passed`.

Measured just now:

```
pytest -q --basetemp=.pytest-run-tmp   ->  111 passed, 5 errors
pytest -q                              ->  116 passed, 0 errors
```

The 116 is a real number. It came from the run **without** the `--basetemp`
flag. With the flag -- which is the canonical command in
`docs/protocol/README.md` and in every plan -- five tests still error with
`PermissionError [WinError 5]` during temp-directory setup, in
`tests/test_fusion.py` and `tests/test_fusion_scripts.py`.

`.pytest-run-tmp/` remains unreadable to its own owner; `Get-ChildItem` on it is
denied. This is the same P0 blocker recorded in `idea-web-workstation.md`
section 8 and in `claudePlan-web-workstation-1.md`, unchanged.

Two consequences, and the second matters more than the first:

1. The environment still needs fixing:
   `Remove-Item -Recurse -Force .pytest-run-tmp`, with `takeown` / `icacls` or
   an elevated shell if that is denied.
2. **A gate report quoted a passing number produced by a non-canonical
   command.** That is the exact failure mode
   `docs/protocol/README.md` legislates against -- "No agent opinion replaces
   these commands." The number was not wrong; the command was. If a gate can be
   satisfied by a nearby command that happens to pass, the gate is decorative.

**Required:** clear the directory, re-run the canonical command verbatim, and
report its output. If the directory cannot be removed, that is a blocker to
escalate -- not a reason to change the canonical command.

### F2 -- major -- this change bypassed the protocol it was defining

There is no plan in `docs/codex/` for this work. No `claudePlan-<slug>-N.md`, no
phases, no gate report appended to a plan, no sign-off log, no Claude
verification before the work was declared final.

`docs/codex/README.md` allows small one-line fixes to skip the protocol and
requires it "when the change needs phased work, durable handoff, or independent
verification." This change created two folders, wrote the project's
source-of-truth document, added two test functions, and edited five index files.
It is squarely on the protocol side of that line.

The irony is worth naming: **the change that defines the project's mission is
the one change that skipped the project's method.** Not a disaster -- the output
is good -- but if the protocol is optional when the work feels obvious, it will
be skipped precisely when it matters, because important work always feels
obvious to whoever is doing it.

**Required:** either a retroactive plan documenting what was done and this
document as its sign-off, or an explicit written decision that mission documents
are exempt from Plan-Gate-Verify. I would accept either. What I would not accept
is leaving it ambiguous, because the next agent will read the precedent, not the
rule.

### F3 -- major -- the invariants cannot do the job invariants were introduced to do

This is the most important content finding.

`review-user-1.md` gap 3 introduced invariants for one specific purpose: to turn
the minor-vs-major change classifier from an open-ended AI judgment into a
**lookup**. Does the change touch a declared invariant? Major. Only free
variables? Minor.

For that to work, invariants must be *specific, physical, and checkable*.
Section 7's current invariants are none of those:

> - Real build evidence is stronger than guesses, assumptions, or web data.
> - Generated outputs are not hand-edited.
> - Raw measurements are preserved even after conversion into YAML.

These are excellent, and they are **method invariants** -- rules about how the
project works. They are not **artifact invariants** -- rules about what the
thing being built must remain true to. No AI can classify "make the arms 2mm
narrower to save weight" against "real build evidence is stronger than guesses",
because the two are not about the same category of thing.

The artifact invariants for the current build exist and are knowable today:

- Must be cut from a single 250x250mm sheet (it is the stock that is owned)
- Must fly on the salvaged Temu motors (it is a salvage project; buying new
  motors makes it a different project)
- Must be cuttable on a laser in one pass (no CNC access)
- Must carry the FC stack and battery already on hand

Each has a *why*, and the why is what makes it an invariant rather than a
preference. Without those, section 7 reads as a philosophy statement and the
classifier has nothing to look up.

**Fix applied:** I have split section 7 into method invariants and artifact
invariants, and added the classification rule that consumes them. See section 4.

### F4 -- minor -- the new tests pin prose written in the same change, by the same author

`test_project_description_defines_fusion_control_center_scope` asserts ten exact
strings from `description.md` -- headings, and two full sentences:

```
"current repository remains the first concrete case study"
"Internet sourced component data must be treated as unverified"
```

Two problems.

First, the test and the text it tests were written together, so the test could
never have failed. It documents an intention rather than verifying a property --
`docs/codex/behaviour.md` forbids Codex marking a verify phase PASS, and a test
that asserts your own prose back to you is a soft version of the same move.

Second, it is brittle in a way that will bite. Pinning full sentences means any
legitimate rewording breaks the suite, which trains whoever hits it to edit the
test until it passes -- and a test edited to pass is worse than no test. I hit
this immediately: updating `description.md` per this review required working
around all ten pinned strings.

The right shape is to assert *structure* -- that the required sections exist,
that invariants and free variables are both present and non-empty, that every
verification state named in `capture-candidates.md` is defined. Those are
properties a future edit can violate meaningfully.

**Not fixed.** I have deliberately left the test alone and preserved all ten
pinned strings in my edit, because rewriting Codex's test would be me
implementing in a change I am verifying. It should be fixed by Codex, under a
plan.

### F5 -- major -- the ICM layer model is absent, and it is the missing vocabulary

`description.md` section 3 builds a source-of-truth ladder, and section 8 builds
a table of where capturable data goes. Both are good. Neither names the thing
they are circling.

`review-icm-paper.md` section 7 established it: ICM separates **Layer 3**
(stable reference, absorbed as constraints, unchanged across runs) from
**Layer 4** (per-run working material, processed as input) -- and

> **Knowledge capture is the promotion of a Layer 4 artifact into Layer 3.**

Section 8's table currently answers *where things live*. It does not answer
*how something moves from being this build's data to being every future build's
reference*, which is the entire purpose of the system. `capture-candidates.md`
has the states but not the transition: it says a candidate is promoted "after
the physical project gives enough evidence", and nothing defines enough.

**The trigger is definable and it is not vague: a completed build is a promotion
event.** When the frame is cut and the motor bolts on, the bolt-circle
measurement stops being build-001 data and becomes reference. When a part
fails, the same event writes a `rejected` candidate. Both directions run off the
same trigger.

**Fix applied:** section 8 now names the layer split and defines the promotion
event. See section 4.

### F6 -- minor -- provenance is tracked per candidate, not per number

`capture-candidates.md` attaches one verification state to a whole candidate.
That works for a lesson or a Fusion trick. It breaks for a component.

A motor card carries perhaps eight dimensions. The bolt circle is caliper-
measured, the KV rating is a vendor claim, the max thrust is measured on a
kitchen scale, the stator size is read off a stamp. One `verification state`
field for the card is a lie about at least three of them -- and it is exactly the
mechanism by which UC2's internet-sourced numbers would eventually contaminate
UC1's measured ones, which section 4 of `description.md` correctly says must not
happen.

Per-dimension provenance, as in `review-user-1.md` gap 1, is the fix. It does not
need building now, but the candidate template should stop implying that one
state per record is sufficient.

### F7 -- minor -- transient content in a permanent document

`description.md` section 9 is a review of `review-user-1.md`. A mission baseline
should not contain a review of a brainstorming note -- brainstorming is upstream
of the mission, and once absorbed, the absorption is the record. In a year that
section will be archaeology inside the one document that most needs to stay
current.

Constrained by F4 (the string `review-user-1.md` is pinned by the test), I have
rewritten the section as a short provenance note pointing at the brainstorming
documents, rather than deleting it.

### F8 -- minor -- two overlapping review documents now exist

`idea-fusion-control-center-manifesto-review.md` (Codex, 11.3 KB) and
`review-user-1.md` (mine) review the same manifesto and reach compatible
conclusions. Two files, one job.

Codex's file is named `idea-*` but contains a review, which crosses the
`docs/brainstorming/README.md` convention (`idea-<slug>.md` for notes,
`review-<slug>.md` for analysis -- a row I added yesterday, so the collision is
partly mine for adding the pattern late).

Not urgent. Worth resolving before commit so the folder has one obvious entry
point per topic.

### F9 -- minor, and quietly important -- the manifesto has no durable home

`docs/brainstorming/idea-user-1.md` is **still 0 bytes**. Your manifesto exists
in this conversation and in two agents' summaries of it. It is not in the repo.

`docs/protocol/trust-boundaries.md` opens with "keep durable state in repo files,
not chat", and the source document for the entire project direction is currently
chat-only. Everything downstream -- `description.md`, both reviews, this file --
is a derivative of a source that would not survive losing this session.

**Save that file.** It is the smallest item here and the one with the worst
failure mode.

---

## 3. The finalized definition

Consolidating the manifesto, both reviews, the ICM paper, and Codex's baseline
into one statement I believe all four support:

> **FusionControlCenter is a local-first system for developing hardware in
> Fusion 360 with AI assistance, whose distinguishing property is that every
> project leaves behind verified, reusable knowledge instead of dissolving into
> chat history.**
>
> It has two entry modes: measuring hardware you hold (UC1), and designing from
> a mission you have written down (UC2). It stores what a build taught as
> reference material for the next build, and it never lets an unverified number
> pass as a measured one.
>
> `drone-wood-frame` is its first instance and its only current source of real
> data. FCC becomes a separate thing on the second project, not before.

Three commitments that follow, and that everything else should be checked
against:

1. **Concrete before general.** Build for the drone, extract on the second
   project. One data point does not define an interface.
2. **Provenance before reuse.** No number becomes reusable knowledge until its
   source and verification state are recorded. This is what keeps UC2 from
   poisoning UC1.
3. **Physical truth outranks everything.** Calipers beat datasheets, datasheets
   beat AI inference, and a completed build beats all three.

---

## 4. Changes I made to `description.md`

Per your instruction to update it from this review. All ten test-pinned strings
preserved; the canonical commands still pass exactly as before the edit.

| # | Change | From finding |
|---|---|---|
| 1 | Section 3 gains an ICM layer column mapping each truth layer to L0-L4 | F5 |
| 2 | Section 7 split into **method invariants** and **artifact invariants**, with the frame's four physical invariants stated and justified | F3 |
| 3 | Section 7 gains the **change classification rule** -- invariant touched means major, free variables only means minor | F3 |
| 4 | Section 8 gains the **promotion event**: a completed build promotes Layer 4 to Layer 3, in both directions | F5 |
| 5 | Section 8 notes that component records need per-dimension provenance, not one state per record | F6 |
| 6 | Section 9 rewritten from a review-of-a-review into a short provenance note | F7 |
| 7 | Section 10 roadmap reconciled with `claudePlan-web-workstation-1.md` and the P0 blocker | F1 |
| 8 | Section 11 open decisions updated -- three answered by the reviews, two sharpened | -- |

I did not touch `tests/test_protocol.py`, `capture-candidates.md`, or any index
file. Those are Codex's, and F4 and F6 should be fixed under a plan.

---

## 5. Verdict and conditions

**CONDITIONAL PASS.**

The content is accepted. The direction is right, the scope discipline is real,
and the verification-state ladder is a genuine improvement on what I proposed.

Two conditions before this baseline is committed:

1. **F1** -- clear `.pytest-run-tmp`, re-run the canonical command verbatim,
   report its actual output. If it cannot be cleared, escalate rather than
   substituting a command that passes.
2. **F2** -- either a retroactive plan with this document as its sign-off, or a
   written exemption for mission documents. Ambiguity here sets the precedent.

Recommended before commit, not blocking: F8 (merge the duplicate reviews) and
**F9 (save `idea-user-1.md`)**.

To fix under their own plans, not now: F4 (make the prose tests structural) and
F6 (per-dimension provenance).

---

## 6. Routing

Three plans are now ready to be written, in this order. None should start until
F1 clears, since no gate can pass.

| Order | Plan | Covers |
|---|---|---|
| 1 | `claudePlan-web-workstation-1.md` | Already written. Blocked on P0 (= F1) |
| 2 | `claudePlan-knowledge-schema-1.md` | F4 and F6: structural tests, per-dimension provenance, the component-card shape |
| 3 | `claudePlan-protocol-deliberation-1.md` | The deliberation half of `docs/protocol/`, reconciled with ICM's `CONTEXT.md` rather than inventing a third contract format |

Two questions from `review-icm-paper.md` remain open and shape plan 3:

- **Does Omnissiah already implement ICM concretely?** If so FCC mirrors its
  skeleton rather than inventing a parallel one.
- **ICM stages for the process only, or the whole repo restructured?** I argued
  for the first in `review-icm-paper.md` section 6.3. Your call.
