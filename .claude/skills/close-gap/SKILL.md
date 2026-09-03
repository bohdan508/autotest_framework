---
name: close-gap
description: Close ONE test-coverage gap end-to-end and stop before committing. Picks the highest-priority untested endpoint/flow, scaffolds the test via the new-api-test/new-ui-test patterns, runs it, self-reviews with the test-reviewer agent, fixes findings, re-runs to green, then hands over a ready-to-commit test (does NOT commit or push). Use to knock out coverage gaps one reviewed unit at a time; repeat with /loop close-gap.
---

# close-gap

Close **one** coverage gap per run, fully reviewed, and **stop before commit** —
you commit. One reviewed test per run keeps each unit small and readable (quality
over volume, which is what matters for this portfolio).

## Workflow

### 1. Pick the gap
If the user named a target (an API-N / UI-N id, an endpoint, or a flow), use it.
Otherwise find the highest-priority gap **without** running the full dashboard:
read `.claude/skills/coverage-gap/references/api_surface.md` and `ui_surface.md`,
then statically check the repo (clients, page objects, `tests/`) for what's already
covered. Pick the top gap by the coverage-gap priority order:
1. missing core happy path → 2. missing documented negative → 3. flow needing a new
page object → 4. nice-to-have.

Announce the one gap you're closing before writing code.

### 2. Scaffold the test
Follow the relevant skill's conventions exactly:
- **API gap** → `new-api-test`: add the one-line client method if missing (correct
  `retry_until_ok`), write the test from its template, assert on `status_code`.
- **UI gap** → `new-ui-test`: add/extend the page object (locators in `__init__`,
  no asserts) if needed, write the test with `expect(...)`, relative URLs.
If closing the gap needs a sizeable new page object or entity `.ui` build-out, do it
— but if it balloons beyond one clean unit, stop and tell the user rather than
half-building.

### 3. Run it
```
.venv/bin/pytest <path to the new test> -vv
```

### 4. Self-review (keep this IN the loop — don't skip)
Delegate the changed files to the **test-reviewer** agent. Apply every **blocking**
and **should-fix** finding. Note nits but don't over-polish.

### 5. Re-run to green — and prove it's not flaky
Re-run the test after fixes. Because these tests hit a **live site**, run it
2–3 times (or `--count` if available) to confirm it's stable, not luckily green.
If it flakes, fix the root cause (`wait_until`, better locator) — never paper over
it with retry on a negative or a `sleep`.

### 6. Hand over — DO NOT commit or push
Stop here. Present:
- **Gap closed** — which API-N/UI-N and why it was the priority.
- **Files changed** — test + any client method / page object added.
- **Verification** — the pytest runs (how many, all green) and the reviewer verdict.
- **Suggested commit** — a message and the exact `git add`/`commit` command, for the
  user to run. Do not run them.

## Repeat
- Next gap: run `close-gap` again (review + commit the previous one first).
- Unattended: `/loop close-gap` self-paces successive gaps — but note in mode B it
  produces **ready** tests without committing, so uncommitted changes accumulate
  across iterations. Fine for a review-a-batch style; commit between runs if you
  want clean one-test units.

## Guardrails
- **Never commit or push** — mode B stops at a ready test.
- One gap per run.
- test-reviewer stays in the loop; correctness/convention gate before hand-off.
- Never weaken an assertion or add negative-test retry to force green.
- If a gap can't be closed cleanly in one unit, surface it — don't half-do it.
