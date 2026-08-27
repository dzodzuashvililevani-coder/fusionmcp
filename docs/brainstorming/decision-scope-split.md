# Decision: split knowledge capture out of this project

**Created:** 2026-08-28
**Decided by:** the user
**Status:** accepted -- binding on all documents and plans
**Supersedes:** the knowledge-capture responsibilities described in
`review-user-1.md`, `review-icm-paper.md`, and `review-project-final.md`

---

## The decision

**FusionControlCenter is a creation tool. It is not a knowledge system.**

Knowledge capture -- extraction, promotion, deduplication, ranking, cross-project
memory -- moves to a separate project that does not exist yet.

This repository's remaining obligation to that future project is narrow and
mechanical: **deposit finished products into pre-named folders in a documented
shape, so the knowledge project can collect them later without guessing.**

## What changed, precisely

| | Before | After |
|---|---|---|
| This repo's job | Create hardware **and** capture reusable knowledge | Create hardware. Deposit finished products |
| Promotion decisions | Made here, via a verification ladder | Made by the knowledge project |
| Component cards | Designed and built here | Consumed here at most; designed there |
| `docs/knowledge/` | Staging ledger of candidates awaiting promotion | **Handoff contract**: what gets exported, in what shape |
| Verification states | A workflow this repo runs | **Labels this repo records** on what it produces |
| Extraction, dedup, linking | Deferred, but eventually here | Never here |
| The ICM Layer 4 -> Layer 3 promotion | This repo's central mechanic | Happens in the other project. This repo produces Layer 4 and marks what is finished |

**Only finished products go to the handoff surface.** Not works in progress, not
candidates, not maybes. A thing is exported when the build is done and the thing
is real.

## Why this is right

I argued in `review-user-1.md` that the manifesto described at least five
products and that treating them as one was the main risk to all of them. This
decision applies that argument harder than I applied it, and in the correct
place: it cuts along the seam between *making a thing* and *remembering how*.

Three reasons it holds up:

1. **The two halves have different rhythms.** Creation is bursty and
   project-shaped -- measure, model, cut, fly, stop. Knowledge is continuous and
   cross-project -- it only becomes valuable across many builds. Systems with
   different rhythms in one codebase drag on each other.
2. **The knowledge project needs more than one project to be designed against.**
   Building it here would shape it around a single wooden drone frame, which is
   exactly the one-data-point abstraction problem already identified. Built
   separately and later, it gets to see two or three real projects first.
3. **It removes the largest source of scope creep** from the thing that actually
   has to get finished. This repo's job shrinks back to something completable:
   a frame that flies, and a tidy pile of finished artifacts.

The cost, stated honestly: the handoff shape is being guessed at before there is
a consumer to validate it. Mitigated by keeping the contract small, by exporting
formats that are already standard (`.step`, `.dxf`, YAML, Markdown), and by
treating the contract as revisable until the knowledge project actually reads it.

## What this repo still owes the future project

Only this:

1. **Finished products land in named folders.** Nothing important stays only in
   a working directory or a conversation.
2. **Every exported number carries its provenance** -- where it came from, and
   whether a build confirmed it. This is metadata written alongside the artifact,
   not a workflow.
3. **No private local paths, account names, or machine-specific state** in
   anything exported. Already enforced by `tests/test_privacy.py`.
4. **Stable, boring formats.** Neutral CAD, plain text, standard vector.

That is the whole obligation. Anything beyond it belongs to the other project.

## What this repo explicitly no longer does

- Decide when a candidate is "ready" to be promoted.
- Maintain a component library intended for reuse across projects.
- Extract, normalise, deduplicate, rank, or link knowledge.
- Model cross-project memory or a shared schema for it.
- Build `claudePlan-knowledge-schema-1.md`. **Cancelled.**

## Documents updated for this decision

| File | Change |
|---|---|
| `docs/project/description.md` | Sections 2, 3, 5, 6, 8, 9, 10, 11 rewritten for the narrowed scope |
| `docs/knowledge/README.md` | Repurposed from staging ledger to handoff contract |
| `docs/knowledge/capture-candidates.md` | Reframed: states and provenance are now labels on exports, not a promotion workflow |
| `docs/project/architecture.md` | C7 and the knowledge framing corrected |
| `CLAUDE.md`, `README.md`, `docs/README.md` | Portal rows and convention bullets |
| `review-user-1.md`, `review-icm-paper.md`, `review-project-final.md` | Superseding banners so neither agent is misled by them |

## Unrelated finding made while updating these documents

While propagating the scope change I re-ran the canonical commands and found the
temp-directory blocker had been **misdiagnosed**, by me as well as by Codex.

Evidence, gathered 2026-08-28:

```
pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp   ->  111 passed, 5 errors
pytest -q -p no:cacheprovider                               ->  116 passed, 0 errors
```

`.pytest-work-tmp` was created minutes earlier by that very command and was
**already unreadable**. So was `.pytest-run-tmp` before it. Python creates and
lists directories in the system temp without any trouble.

**The cause is not stale state or a Windows policy on one directory. Any
`--basetemp` pointed inside the project directory is created unreadable.**
Renaming it -- the amendment Codex made -- could never have worked, because the
name was never the problem.

**Superseding correction from Codex review, 2026-08-28:** dropping `--basetemp`
does **not** work in this shell. It moves the same failure to the system pytest
temp root:

```text
python.exe -m pytest -q -p no:cacheprovider
-> 111 passed, 5 errors
-> PermissionError on AppData/Local/Temp/pytest-of-dzodz

python.exe -m pytest -q -p no:cacheprovider --basetemp=.pytest-work-tmp
-> 116 passed, 0 errors
```

So the canonical command keeps the explicit `.pytest-work-tmp` basetemp. The
directory may be unreadable to PowerShell after the run, but pytest can use it
for the run. The command that matters is the one with the exit code, and that is
the explicit basetemp command.

**One change outside my usual boundary, flagged for Codex to challenge:**
`tests/test_protocol.py` pinned the old command string verbatim, so it would have
failed the corrected docs. I updated that one string. The test's purpose is to
assert that the protocol states its canonical command; leaving it pinned to a
command that demonstrably fails would have inverted that purpose. Both canonical
commands now run clean: **116 passed, 0 errors** and **10 checks, 0 failures**.

This retires finding F1 of `review-project-final.md` by replacing it with a
verified command form, not by relying on the system temp directory.

## Still true, and worth not losing

The scope narrowed. Two conclusions from the earlier reviews survive it intact,
because they are about *this* project rather than the knowledge one:

- **Sequencing.** The frame gets measured, cut, built, and flown. That is still
  the thing that has to happen, and it is still the source of everything the
  other project will eventually consume.
- **Provenance.** A number's source and verification state still get recorded
  here, at the moment the number is produced. That is cheap when done at the
  source and impossible to reconstruct later.

What is gone is the obligation to *do anything with* that provenance beyond
writing it down.
