---
name: fix-test
description: Diagnose and fix a failing pytest test in this framework (API or UI). Runs the test in isolation, classifies the failure (real app defect vs test bug vs framework bug vs flaky/lag), fixes at the correct layer, and verifies green. Use when a test is red, a CI job failed, or the user says "fix this test".
---

# fix-test

Diagnose a failing test and fix it **at the right layer** — never by weakening an
assertion to force green. A red test is a signal; the job is to find out what it's
signalling before touching anything.

## Input

The user names a target (test node id, test name, file, or "the CI failure").
If none is given, run the suite and pick the failures. Accept forms like:
- `/fix-test tests/api/test_products.py::test_search_product`
- `/fix-test test_login_ui`
- `/fix-test` (then discover what's red)

## Workflow

### 1. Reproduce in isolation
Run the single target first — full output, stop on first failure:

```
.venv/bin/pytest "tests/api/test_products.py::test_search_product" -x -vv
```

For UI tests, add `--headed` only if you need to watch it; the default failure
diagnostics (trace/screenshot/video, `retain-on-failure`) are usually enough.
Read the traceback **and** `logs/run.log` (the HTTP client logs every
request/response line there).

If it passes in isolation but failed in the suite → suspect **flakiness or test
interdependence** (shared state, order), not the test's own logic. Note that and
jump to the flaky branch below.

### 2. Classify the failure — decide before editing

| Signal | Class | Fix at |
|---|---|---|
| App/site genuinely returns something different now (endpoint changed, message reworded) | **Real defect / upstream drift** | Don't silently weaken — see below |
| Wrong assertion, wrong expected value, wrong node id, typo | **Test bug** | The test |
| Locator broke, page object method wrong, client method wrong, fixture wrong | **Framework bug** | The page object / client / fixture — *not* the test |
| Passes alone, fails in suite; or intermittent; or "just-created resource not found yet" | **Flaky / server lag** | Waits / retry policy (below) |

**The #1 gotcha here:** automationexercise.com returns **HTTP 200 even on errors**;
the real status is `responseCode` in the body. So:
- assert on `response.status_code` (the **body** code), not `response.http_status`.
- A test asserting `http_status == 405` is almost always a **test bug** — it should
  be `status_code == 405` (see `test_post_to_get_endpoints` for the rare valid
  `http_status` check).

### 3. Apply the minimal, correct fix

- **Test bug** → correct the assertion/expected value/node id. Keep the assert
  targeted (this framework prefers plain, specific asserts over full-response
  validation).
- **Framework bug** → fix the layer that owns the behaviour. Locators live in the
  page object's `__init__`; assertions stay in the **test**, never in the page
  object. Endpoint methods stay one-liners in the resource client; cross-cutting
  concerns (timeout/logging/retry) live in `BaseClient`.
- **Flaky / lag** → use `wait_until(...)` to absorb server-side lag (never
  `sleep`). For a **positive** op that expects success (create/update/delete),
  the correct lever is `retry_until_ok=True` on that call.
  ⚠️ **Respect the retry policy** (see CLAUDE.md): transport errors and 5xx are
  always retried; body-level error codes are retried **only** with
  `retry_until_ok=True`. **Negative tests keep the default (`False`)** so their
  expected 4xx returns immediately — do **not** add blanket retry to make a
  negative test pass.
- **Real defect / upstream drift** → do **not** just relax the assertion to go
  green. Confirm it (re-run, check `logs/run.log`, hit the endpoint directly if
  needed), then report it to the user with evidence and a recommendation. Only
  adjust the expectation if the user confirms the new behaviour is correct.

### 4. Verify
Re-run the single test, then widen to catch regressions:

```
.venv/bin/pytest "tests/api/test_products.py::test_search_product" -vv   # the fix
.venv/bin/pytest tests/api/test_products.py -q                            # the module
.venv/bin/pytest -m smoke -q                                             # core paths
```

The ruff PostToolUse hook auto-formats any file you edit, so no manual lint step.

### 5. Report
State plainly:
- **Root cause** and which **class** it was.
- **Which layer** you changed and why that layer (not the test) was correct.
- **Verification**: what you re-ran and that it's green.
- If it was a **real defect** you did *not* mask: what's broken upstream and your
  recommendation.

## Guardrails

- Never weaken/delete an assertion just to force green. A test that passes by
  testing nothing is worse than a red one.
- Assertions stay in tests; locators/actions stay in page objects.
- No hardcoded URLs — everything flows from `settings`.
- Don't add blanket retry to negative tests (breaks the deliberate retry policy).
- Prefer `wait_until` over `sleep`.
