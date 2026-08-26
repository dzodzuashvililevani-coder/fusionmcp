# Planner Behaviour

This project uses a lightweight Plan-Gate-Verify protocol for work that spans
multiple steps, multiple sessions, or more than one agent.

## Role

The planner:

- reads the user request and repo context;
- writes a self-contained plan in `docs/implementer/`;
- names the files in scope and the files deliberately out of scope;
- defines observable acceptance criteria;
- reviews gate reports and implementation diffs;
- appends sign-off entries to the plan, or writes an error-fix file.

## Forbidden

The planner must not:

- write production code for the same feature it will verify;
- skip a gate because a phase looks small;
- mark a phase complete without independently checking the diff and commands;
- approve changes to files outside the plan unless a revision or error-fix says
  why the scope changed.

## Verification Checklist

For every verify phase, do all six:

1. Re-read the plan and any related error-fix files.
2. Read the diff since the previous verified commit.
3. Run the canonical test commands from the plan.
4. Spot-check at least one acceptance criterion end to end.
5. Check for scope drift: extra files, deleted tests, suppressed warnings.
6. Check for over-engineering beyond the plan.

PASS means all six checks passed. Anything else becomes an error-fix file in
`docs/implementer/`.

## Sign-off Rules

Sign-offs are appended to the original plan file under `## 7. Sign-off log`.
Use absolute dates in `YYYY-MM-DD` form. Do not rely on chat history as state.
