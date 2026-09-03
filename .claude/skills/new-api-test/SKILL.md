---
name: new-api-test
description: Scaffold API test(s) for an endpoint in this framework, following the facade → resource-client → BaseClient layering. Adds the one-line client method if missing, writes positive + negative tests with the responseCode/retry conventions, and verifies green. Use when adding coverage for a new or existing automationexercise.com endpoint.
---

# new-api-test

Add API coverage the way this framework is built: cross-cutting concerns live in
`BaseClient`, each endpoint is a **one-line method** on a resource client, and the
test stays a thin, targeted assertion. `templates/test_case.py` is the starting
boilerplate — copy from it, don't hand-roll a new shape.

## Input

The user describes the endpoint. Pin down (ask only what's missing):
- **verb + path** (e.g. `POST /searchProduct`)
- **resource group** — `products`, `accounts`, or a new group
- **scenarios** — the happy path plus the negatives worth covering
- **expected** — the real `responseCode` and, where asserted, the `message` string

## Workflow

### 1. Ensure the resource-client method exists (one-liner)
Look in `clients/products_api.py` / `clients/accounts_api.py`. If the endpoint has
no method, add one — a single call into `self.client`, matching the existing style:

```python
def search_product(self, product_name: str) -> ApiResponse:
    """POST /searchProduct - finds a product by name."""
    return self.client.post("/searchProduct", data={"search_product": product_name})
```

**`retry_until_ok`** decision (this is the deliberate retry policy — don't break it):
- **Positive** create/update/delete that expects success → pass `retry_until_ok=True`
  (see `AccountsApi.create_account`).
- Everything else (reads, and anything a **negative** test drives) → leave the
  default `False`, so an expected 4xx returns on the first try, unmasked.

Never assert through a `retry_until_ok=True` method in a negative test — post
directly via `api_facade.<resource>.client.post("/path", data=...)` instead.

**New resource group?** Create `clients/<name>_api.py` (class mirroring the
others, `client: BaseClient` in `__init__`), then register it in the `Api` facade
(`clients/api.py`): `self.<name> = <Name>Api(client)`. One line — everything
cross-cutting is already inherited from `BaseClient`.

### 2. Write the test(s)
Copy the relevant blocks from `templates/test_case.py` into
`tests/api/test_<resource>.py` (append if the file exists). Hold these lines:
- `pytestmark = allure.feature("<Resource>")` at module top.
- `@allure.title("...")` on every test; `@pytest.mark.smoke` on the core happy paths.
- **Assert on `.status_code`** (the body `responseCode`) — *not* `.http_status`.
  The only place `http_status` is asserted is the wrong-verb case, where you check
  `http_status == 200` **and** `status_code == 405` together.
- Assert `message`/payload with **plain, targeted asserts** — don't validate the
  whole response. (Pydantic models are reserved for the `Product`/`User` showcase.)
- Build data with `make_user(**overrides)`; drop a field (`del payload[field]`) for
  missing-field negatives.
- Use existing fixtures — `api_facade`, `user_entity` (created+cleaned up),
  `logged_in_user`. Anything you create yourself, delete in a `finally` or fixture.
- Absorb "just-created, not queryable yet" lag with `wait_until(...)`, never `sleep`.

### 3. Verify
```
.venv/bin/pytest tests/api/test_<resource>.py -vv          # the new tests
.venv/bin/pytest tests/api/test_<resource>.py -m smoke -q  # core subset
```
Confirm green. The ruff PostToolUse hook auto-formats edited files, so no manual
lint step — but if you added a whole file, a quick `.venv/bin/ruff check .` is fine.

### 4. Report
- Which client method you added (or reused) and the `retry_until_ok` choice + why.
- The tests added (names, positive/negative, smoke or not).
- Verification: what you ran and that it passed.
- If a negative's real `message` differed from what was expected, surface it —
  don't quietly rewrite the assertion to match.

## Guardrails
- One endpoint = one thin client method. No logic, timeout, or retry in the test
  or the resource client — that all lives in `BaseClient`.
- No hardcoded URLs; paths only (base URL comes from `settings`).
- Don't add `retry_until_ok=True` to make a negative test pass.
- New markers must be registered in `pytest.ini` (`--strict-markers` will error otherwise).
- Clean up every resource a test creates.
