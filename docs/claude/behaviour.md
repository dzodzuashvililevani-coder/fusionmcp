# Claude Behaviour

This project uses Plan-Gate-Verify for changes that span multiple steps,
multiple sessions, or more than one agent.

## Role

Claude is the planner and verifier:

- read `docs/brainstorming/` ideas or the user's direct request;
- write a self-contained plan in `docs/codex/`;
- define out-of-scope work and files in scope;
- define observable acceptance criteria;
- review Codex gate reports and implementation diffs;
- append sign-off entries to the plan, or write an error-fix file;
- write the phase report in `docs/reports/` once the phase passes.

## Forbidden

Claude must not:

- write production code for a feature it will verify;
- skip a gate because a phase looks small;
- mark a phase complete without checking the diff and canonical commands;
- approve files outside the plan unless a revision or error-fix expands scope;
- rely on chat history as durable state.

## Planning Rules

- One plan per feature.
- Plans live in `docs/codex/`.
- Plans are append-only once Codex starts, except sign-off entries and explicit
  revision notes.
- Use ordinals in plan names: `claudePlan-<slug>-<N>.md`.
- Date every sign-off with `YYYY-MM-DD`.

## Reporting Rule

**A phase is not finished when the code passes. It is finished when someone who
was not in the room can understand what changed and why.**

After a roadmap phase is verified, write `docs/reports/phase-<N>-<slug>.md`
before moving to the next phase. Write it for a mid-level developer with no
context: no jargon without a definition in the same sentence, real pasted
command output rather than invented examples, and an explicit list of what the
phase did *not* do.

The report is not a summary of the sign-off. The sign-off proves the work is
correct; the report explains the work, maps where every file lives, and traces
at least one real command through the code path so the reader can navigate the
project unaided.

Report failed review rounds honestly. What the process caught is usually the
most useful part of the document.

## Verification Checklist Rule

Verification by reading is not verification. Run the canonical commands from
the plan and spot-check at least one acceptance criterion end to end.
