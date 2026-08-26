# Verification Checklist

Use this for every `verify` phase in a Codex plan.

## Required Steps

1. Re-read the plan and related error-fix files.
2. Read the diff since the previous verified commit.
3. Run the canonical test commands from the plan.
4. Spot-check at least one acceptance criterion end to end.
5. Check for scope drift: extra files, deleted tests, suppressed warnings.
6. Check for over-engineering beyond the plan.

## Verdicts

PASS only if all six checks pass. Anything else gets an error-fix file in
`docs/codex/` and a FAIL sign-off entry in the original plan.

## Evidence

Every sign-off must include:

- commit SHA;
- test command output or exact command status;
- files inspected;
- short notes on any remaining risk.
