# AutoTest Framework

A test-automation framework for the public demo site
**[automationexercise.com](https://automationexercise.com)**, covering both its
REST API and its web UI. Written as a portfolio piece: one job per layer, config and CI. Kept
intentionally lean: no over-engineering.

**📊 [Live Allure report](https://bohdan508.github.io/autotest_framework/)** —
published from CI on every run.

---

## What it demonstrates

- **A layered HTTP client** where tests stay one-line-per-endpoint and everything
  cross-cutting (timeout, logging, retry, reporting) lives *underneath* them, so
  it happens for free and never leaks into a test.
- **A retry policy that knows the difference** between a transient failure (retry
  it) and a negative test's *expected* error (don't — or you'd mask the very
  thing under test).
- **Handling a real API issue**: the site returns **HTTP 200 on every error**,
  with the true status hidden in a `responseCode` body field. The client is built
  around that, so tests assert on the real status transparently.
- **Config with zero hardcoded URLs** — one `.env` re-points the entire suite
  (API client *and* browser) at any environment.
- **UI mirrors API deliberately** — a facade over page objects mirrors the facade
  over resource clients, and an entity/component pattern lets the *same* user data
  drive both API and UI flows (create over API, verify through the browser, and
  the reverse).
- **CI/CD** — a fast lint gate plus a full suite that publishes an Allure report
  to GitHub Pages, with a nightly smoke run.

---

## Architecture

Each layer has exactly one job.

### API side

```
test
 └─ Api                 facade — one object exposing every resource group
     └─ ProductsApi /   resource client — one tiny method per endpoint
        AccountsApi
         └─ BaseClient   the HTTP client: request/retry, logging hook, result wrap
             ├─ _TimeoutSession   requests.Session subclass, default timeout everywhere
             └─ ApiResponse       exposes the REAL status (the responseCode gotcha)
```

Tests reach everything through one facade (`api_facade.products`,
`api_facade.accounts`, …) built over a **single shared client** — one session, one
connection pool. Adding an endpoint group is one line; the cross-cutting behaviour
below it applies automatically.

### UI side (Playwright, Page Object Model)

```
test
 └─ Pages               facade — one object exposing every page object
     └─ LoginPage /      page object — locators + one method per user action
        ProductsPage …
         └─ BasePage      shared open()/navigation over Playwright's `page`
             └─ ProductRow  shared row component, scoped to one <tr> (cart + checkout)
```

The UI stack is a deliberate twin of the API stack: facade-over-shared-resource,
one small method per user action, assertions kept in the tests (via Playwright
`expect`).

### The seam between them

An **entity** bundles data with two actions objects reading the *same* data:

```python
user.api.create()     # over HTTP (fast — used to seed state)
user.ui.create()      # through the browser (the thing a UI test exercises)
user.api.exists       # verify over API
```

So a UI test can sign a user up **in the browser** and then assert
`user.api.exists()` — the two halves agree because they share one entity.

---

## Tech stack

| Concern        | Choice                                               |
| -------------- | ---------------------------------------------------- |
| Language       | Python 3.11                                          |
| Test runner    | `pytest`                                             |
| HTTP           | `requests` (with a timeout/logging/retry base client)|
| UI             | `playwright` + `pytest-playwright`                   |
| Config         | `pydantic-settings` (reads `config/.env`)            |
| Models         | `pydantic` (payload + response, as a showcase)       |
| Test data      | `faker` (via factories)                              |
| Reporting      | `allure-pytest` → Allure report                      |
| Lint/format    | `ruff` (config in `pyproject.toml`)                  |
| CI             | GitHub Actions → GitHub Pages                        |

---

## Project structure

```
autotest_framework/
├── .github/workflows/  lint.yml (ruff gate), tests.yml (suite + Allure → Pages)
├── config/          settings.py (pydantic-settings), .env.example
├── clients/         base_client.py, api.py (facade), products_api.py, accounts_api.py
├── pages/           pages.py (facade), base_page.py, *_page.py, product_row.py
├── components/      user.py (entity + api & ui actions), product.py (api-only)
├── models/          user.py (payload), product.py (response)
├── utils/           factories.py (Faker), wait.py
├── tests/api/       test_products.py, test_users.py
├── tests/ui/        test_products_ui.py, test_users_ui.py
├── conftest.py      fixtures: api_facade, pages, user_entity, logged_in_user, …
├── pytest.ini       markers + logging config
├── pyproject.toml   ruff config
├── requirements.txt / requirements-dev.txt
```

---

## Getting started

Requires **Python 3.11**.

```bash
# 1. Clone and enter
git clone https://github.com/bohdan508/autotest_framework.git
cd autotest_framework

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. Browser for the UI tests (Chromium + its system libs)
python -m playwright install chromium

# 5. Config — copy the example and adjust if needed
cp config/.env.example config/.env
```

The defaults in `.env.example` already point at the live site, so no editing is
needed to run against it.

---

## Running the tests

```bash
pytest                          # everything (API + UI)
pytest tests/api                # API suite only
pytest tests/ui                 # UI suite only
pytest -m smoke                 # fast core-path subset (both layers)
pytest --headed --slowmo 500    # watch the UI tests run in a real browser
```

A per-request log line prints live and is also written to `logs/run.log`.

---

## Reporting (Allure)

Tests write result files that Allure turns into an HTML report.

```bash
pytest --alluredir=allure-results       # 1. collect results
allure serve allure-results             # 2. open the report locally
```

`allure serve` needs the Allure CLI (`brew install allure`, or see the
[Allure docs](https://allurereport.org/docs/install/)). Collecting results needs
no extra tooling — that's built into `allure-pytest`.

In CI the report is generated and **published to GitHub Pages** automatically —
see the link at the top.

---

## Continuous integration

Two GitHub Actions workflows (`.github/workflows/`):

- **`lint.yml`** — the cheap gate. Runs `ruff check` + `ruff format --check` on
  every push and PR. Fast, deterministic, no network.
- **`tests.yml`** — runs the suite and publishes the Allure report to GitHub
  Pages. Triggered on code changes (docs edits are skipped via a path filter),
  nightly at 03:00 UTC as a `smoke` run, and on demand via the *Run workflow*
  button.

---

## Status

A work in progress:

- **API layer** — largely complete. Two resource groups (products, accounts/users)
  with positive and negative tests over the full client/config/logging/retry
  foundation.
- **UI layer** — in progress. Page-object layer and user/product flows are built;
  `ProductEntity`'s UI actions are still stubbed.
- **Planned** — Allure history/trends across runs (CI currently publishes the
  latest report only).
