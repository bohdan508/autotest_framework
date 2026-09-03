---
name: coverage-gap
description: Map test coverage against the site's known API + UI surface and report the gaps as a shareable Artifact dashboard plus a terminal summary. Diffs curated reference inventories (references/) against static analysis of the repo — deterministic, offline, no live browsing. Use to find untested endpoints/flows, prioritize what to test next, or produce a coverage report for the README/CV.
---

# coverage-gap

Find what the suite does **not** cover, by diffing two sets:
1. **What exists** — the curated surface inventories in `references/api_surface.md`
   and `references/ui_surface.md` (committed source-of-truth; deterministic).
2. **What's covered** — static analysis of the repo (clients, page objects, tests).

The result is an **Artifact dashboard** (shareable URL, portfolio-friendly) plus a
terminal summary. This skill does **not** browse the live site — coverage must be
repeatable and offline. (Refreshing the reference files from the live site is a
separate, deliberate, human-reviewed step — not part of a coverage run.)

## Workflow

### 1. Load the surface
Read both reference files in `references/`. These define every surface item
(API-1…API-14, UI-1…UI-15) and carry mapping hints.

### 2. Analyze what's covered (static — no network)
- **API:** read `clients/products_api.py`, `clients/accounts_api.py`,
  `clients/api.py`; then read/grep `tests/api/`. For each API-N, decide:
  - **covered** — a test asserts its real `status_code` (body responseCode) and,
    where documented, the `message`;
  - **partial** — endpoint hit but a documented variant (missing-param / wrong-verb
    / bad-data) is untested;
  - **gap** — no test.
  Record the covering test name(s) per item.
- **UI:** read `pages/pages.py` + the page objects; then read/grep `tests/ui/`.
  For each UI-N, decide **covered** (a test drives it and asserts via `expect`
  and/or API), **gap with scaffolding** (page object exists, no test), or
  **full gap** (neither). Record covering test name(s).

Be accurate over generous: if unsure whether an assertion truly exercises a
scenario, open the test and confirm. Don't credit coverage you can't point to.

### 3. Build the coverage model
Compute, per section: covered / partial / gap counts and a coverage %
(covered ÷ total; count `partial` as half or list it separately — state which).
Then a **prioritized gap list**, ordered:
1. core happy paths missing (highest);
2. documented negatives missing (missing-param, wrong-verb, bad-data);
3. flows with no page object (more work, lower urgency);
4. nice-to-haves.

### 4. Render the dashboard (the fancy part)
**First load the `artifact-design` skill** (required before writing any Artifact),
to calibrate design effort. Then write a self-contained HTML file to the scratchpad
dir and publish it with the Artifact tool. The page must include:
- a headline: overall coverage %, plus per-section (API / UI) %;
- a **coverage matrix** per section — each surface item as a row with status
  (✅ covered / ⚠️ partial / ❌ gap), and the covering test name(s);
- a **prioritized "what to test next"** list from step 3;
- theme-aware (light/dark), responsive (tables scroll inside their own container),
  a favicon (e.g. 📊), a stable `<title>`, and a one-sentence `description`.
Keep it a truthful report — no invented numbers; every % must trace to step 2.

### 5. Terminal summary + handoff
Print a compact summary: the three percentages and the top 3–5 gaps. Give the
Artifact URL. Offer to close specific gaps with `/new-api-test` or `/new-ui-test`
(name the exact endpoints/flows).

## Guardrails
- No live browsing in a coverage run — read the reference files, not the network.
- Every coverage claim must point to a real test; when in doubt, open the test.
- If the repo has endpoints/flows **not** in the references, flag them as
  "surface inventory may be stale" — don't silently ignore them.
- Write the HTML to the scratchpad dir, not the repo, unless the user asks to
  commit it. `.claude/` is ruff-excluded, but generated reports don't belong there.
