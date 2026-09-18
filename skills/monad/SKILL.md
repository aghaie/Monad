---
name: monad
description: Use when asked to improve, upgrade, review-and-fix, or "take forward" an existing project of any kind or maturity (idea-only, prototype, tested, shipped) — including "/monad <path>", "بهبودش بده", "make this project better", "what should I do next with this repo", or when a previous improvement pass has no measured result.
---

# MONAD — improve any project toward the truth, one measured step at a time

**Core principle:** a project improves only when a real measurement says so. Everything else is opinion. MONAD runs one cycle: OBSERVE → LEVEL → PROPOSE → EXECUTE → MEASURE → REPORT. Never skip a stage, never merge two.

**Violating the letter of this cycle is violating its spirit.**

## Stage 0 — Language and scope
Reply in the user's language. Scope = the project path given (default: cwd). Do not touch anything outside it.

## Stage 1 — OBSERVE (facts only, each with its command)
Run, do not guess. Record every fact with the command that produced it:
```
git log --oneline | head; git status --short        # history, dirty state
find . -type f -not -path './.git/*' | head -200    # shape, languages, size
cat README* 2>/dev/null | head -60                  # stated purpose, stated usage
<run the documented usage exactly as the README says>   # does it work AS DOCUMENTED?
<run tests / build / lint if they exist>            # BASELINE numbers: pass/fail counts, errors
```
Reproduce every bug you intend to fix **before** touching code. A bug you only read is a HYPOTHESIS; a bug you ran is a FACT.

## Stage 2 — LEVEL (where the project actually is)
| Level | Evidence required |
|---|---|
| L0 idea | no runnable code |
| L1 runs | documented usage works on a clean run |
| L2 tested | a test command exists and passes |
| L3 usable by others | install/run instructions verified from scratch; no data loss on normal input |
| L4 in real use | evidence of real users/data (issues, logs, exports, commits by others) |
| L5 measured | a real-use metric exists and is tracked over time |
The level is the highest row whose evidence you actually saw. "Probably L2" = L1.

## Stage 3 — PROPOSE (write it down before doing it)
Write `docs/monad/PROPOSAL-<YYYY-MM-DD>.md` (create the folder) containing:
1. Level now + the evidence lines from Stage 1.
2. **ONE** step that moves the project up one level (or fixes the worst L-blocker), and why it is the smallest correct change. Candidate steps are ranked by: need of the real users > truth (fixes a reproduced defect) > utility > feasibility > cost/risk.
3. The metric that will show the step worked, and its baseline value from Stage 1.
4. What you will NOT do this cycle (everything else you noticed).
If the user said "propose only", stop here.

## Stage 4 — EXECUTE (smallest correct diff)
- Follow the project's existing conventions, language, style, tooling. Add no dependency that stdlib covers.
- Existing data files / formats keep working after your change (old input must still read). A change that breaks stored data is not an improvement.
- Tests exist → write the failing test first. No tests and code is non-trivial → leave ONE runnable check (a `test_*` file or `__main__` self-check).
- Nothing destructive without asking: no deleting user data, no force-push, no rewriting history, no wholesale rewrites.

## Stage 5 — MEASURE (same commands as Stage 1)
Re-run the baseline commands. Compare before/after on the declared metric. Verdict:
- **DEPLOY** — metric improved, nothing regressed → commit with the message format below.
- **ROLLBACK** — anything regressed or the metric did not move → `git checkout -- .` (or revert), record why.
- **INCONCLUSIVE** — could not measure → say so; do not claim improvement.

Commit message format (only if the project is a git repo and the verdict is DEPLOY):
```
<area>: <what changed>

WHY: <reproduced problem / level blocker>
WHAT: <files, in one line>
EXPECTED: <metric before → target>
ACTUAL: <metric after, verbatim from the command>
```

## Stage 6 — REPORT
Write `docs/monad/REPORT-<YYYY-MM-DD>.md` with exactly these seven headings, one to three lines each, then echo it in chat:
1. What I understood (facts with commands) · فهمیدم
2. What I built/changed · ساختم
3. What is usable now · قابل استفاده
4. What got better — metric before → after, verdict · بهتر شد
5. What failed / is blocked · شکست / مسدود
6. What I learned · یاد گرفتم
7. Next step (the next single level-up) · قدم بعد
Every sentence in sections 1 and 4 is one of: **FACT** (has a command/output), **HYPOTHESIS** (not run), **UNKNOWN**. Confidence follows evidence, not eloquence. One observation is one witness — do not count it twice.

## Red flags — stop, go back to the stage you skipped
- Editing code before running the documented usage
- "Obvious bug, no need to reproduce"
- Fixing six things in one pass ("while I'm here")
- "Better" stated without a before-number
- Changing a file format without reading old files
- Report in chat only, no file
- Asking the user to choose between options you could rank with the Stage 3 criteria

| Rationalization | Reality |
|---|---|
| "The project is tiny, the cycle is overkill" | A tiny project takes five minutes per stage. Skipping stages is how tiny projects rot. |
| "I fixed everything I saw, that's more value" | Unmeasured bundles cannot be rolled back one at a time. One step, one verdict. |
| "Tests pass, so it's better" | Your new tests test your new code. The metric is the one declared in the proposal. |
| "The user wants results, not proposals" | The proposal is 10 lines and is what lets the user redirect before the diff exists. |
