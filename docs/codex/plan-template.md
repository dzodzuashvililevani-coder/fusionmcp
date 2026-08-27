# <Feature title>

**Plan:** claudePlan-<slug>-N.md
**Created:** YYYY-MM-DD
**Source spec:** <path in docs/brainstorming/ or direct user request>
**Status:** in-progress | blocked | complete

## 1. Goal (<= 3 sentences)

What we are building, in one breath. No background beyond what Codex needs.

## 2. Out of scope

What this plan deliberately does not touch.

## 3. Files in scope

Paths only. Mark `(new)` for files to create.

Anything not on this list is OFF-LIMITS unless an error-fix or revision says
otherwise.

## 4. Acceptance criteria

Each criterion must be observable and testable from outside the code.

## 5. Phases

### Phase <K>: implement - <one-line title>

**Definition of done:** observable, testable bullets
**Touches:** subset of files from section 3

### Phase <K+1>: gate - <one-line title>

**Definition of done:** gate report appended, then halt
**Touches:** plan file only
**Commands to run:** exact shell commands
**Status report sections:** commit SHA, files changed, test output, self-assessment, open questions

### Phase <K+2>: verify - <one-line title>

**Definition of done:** Claude appends PASS sign-off or writes error-fix
**Touches:** plan file, or error-fix file if verification fails

## 6. Test commands (canonical)

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m frame_tools.cli report
```

## 7. Sign-off log

### Phase <K> gate report - YYYY-MM-DD

**Commit SHA:** <sha>
**Files changed:** <git diff --stat since previous gate>
**Test command output:** <verbatim tail of each canonical command>
**Self-assessment:** <three lines max>
**Open questions:** none | <list>

### Phase <K+1> sign-off - YYYY-MM-DD

**Verdict:** PASS | FAIL -> errorFix-<M>
**Evidence:** commit SHA, test output, files inspected
**Notes:** one or two lines max
