---
name: new-ui-test
description: Scaffold Playwright UI test(s) for a flow in this framework, following the Pages facade → page object → BasePage layering and the shared row component. Adds/extends page objects (locators + action methods, no asserts) when needed, writes tests using expect() and existing fixtures, and verifies. Use when adding UI coverage for a screen or user flow on automationexercise.com.
---

# new-ui-test

Add UI coverage the way this framework is built: the page object owns
**locators + user actions**, the test owns **assertions** (`expect`), state is set
up the fast way via the API, and everything reaches the screen through the `Pages`
facade. `templates/page_object.py` and `templates/ui_test_case.py` are the starting
boilerplate — copy from them, don't hand-roll a new shape.

## Input

The user describes the flow/screen. Pin down (ask only what's missing):
- **flow** — what user journey (e.g. "search then add to cart", "signup error")
- **screens involved** — which existing page objects (`login`, `products`, `cart`,
  `checkout`, `payment`, `home`, `signup`) and whether a **new** one is needed
- **scenarios** — happy path plus the negatives worth covering
- **assertions** — what visible/URL/API state proves success

## Workflow

### 1. Page-object layer — add or extend (only if needed)
If the flow uses existing pages and their methods, skip to step 2. Otherwise:

- **New action on an existing page** → add a method to that page object. Locators
  go in `__init__` (prefer `data-qa` attrs like `[data-qa="login-email"]`, then
  `get_by_role`/`get_by_text`, then CSS). The method does the action only — **no
  assertions**. Expose any element the test needs to assert on as a locator attr
  (see `LoginPage.login_error`).
- **New page** → copy `templates/page_object.py` to `pages/<name>_page.py`, set
  `path`, then register it one line in the `Pages` facade (`pages/pages.py`):
  `self.<name> = <Name>Page(page)`.
- **Repeated table rows** → reuse `ProductRow`/`CartRow` (`pages/product_row.py`)
  scoped to one `<tr>` via the page's `row(product_id)` method — never page-level
  locators that could match the wrong row.
- **Entity `.ui` actions** → if the flow belongs on an entity (like
  `user.ui.create()`), follow the `UserUiActions` pattern in `components/user.py`
  (read the same entity data, guard on a missing `pages` facade). Note
  `ProductEntity.ui` is still stubbed — building it out is a valid task here.

### 2. Write the test(s)
Copy the relevant blocks from `templates/ui_test_case.py` into
`tests/ui/test_<flow>_ui.py`. Hold these lines:
- **Assertions are `expect(...)` in the test**, not in page objects. Use
  `expect(locator).to_be_visible()/to_have_text(...)` and
  `expect(page).to_have_url("/relative")`.
- **Relative URLs only** — base_url is fed to Playwright from `settings`. Never
  hardcode `https://automationexercise.com`.
- Set state up via the API for speed: create a user with `api_facade` /
  `UserEntity`, or use fixtures `user_entity` (created + cleaned up),
  `logged_in_user` (created + logged in via UI), `product_in_cart`.
- `@allure.title("...")` on every test; `@pytest.mark.smoke` on core happy paths.
- **Clean up** any account/resource you create in a `finally` (guard with
  `if user.api.exists()`), or use a self-cleaning fixture.
- The `pages` fixture already aborts ad/analytics requests, so don't re-handle
  overlays. Use `wait_until` for backend lag; rely on Playwright auto-waiting for
  the UI (avoid `sleep`).

### 3. Verify
```
.venv/bin/pytest tests/ui/test_<flow>_ui.py --headed -vv   # watch it once (optional)
.venv/bin/pytest tests/ui/test_<flow>_ui.py -q             # headless, as CI runs it
.venv/bin/pytest tests/ui -m smoke -q                      # core subset
```
On failure, the trace/screenshot/video are retained (`retain-on-failure`); open a
trace with `playwright show-trace <zip>`. The ruff hook auto-formats edited files.

### 4. Report
- Page objects added/extended (and the one-line facade registration if new).
- Tests added (names, positive/negative, smoke or not).
- Verification: what you ran (headed/headless) and that it passed.
- If a real UI defect surfaced, report it — don't loosen the assertion to go green.

## Guardrails
- Locators + actions in page objects; assertions in tests. Never mix.
- Locators live in `__init__`; prefer `data-qa` / role / text over brittle CSS.
- No hardcoded URLs — relative paths only, base_url from `settings`.
- Reuse `ProductRow`/`CartRow` for table rows; don't reinvent row locators.
- New markers must be registered in `pytest.ini` (`--strict-markers`).
- Clean up every resource a test creates.
- An entity's `.ui` actions need `pages` passed to `UserEntity(...)`; API-only
  construction leaves `.ui` unusable by design.
