# API surface — automationexercise.com

Source of truth for API coverage. Captured from https://automationexercise.com/api_list.
The 14 documented endpoints/scenarios. Paths are shown as the resource clients use
them (without the `/api` prefix, which `settings.api_prefix` supplies).

To refresh: re-read /api_list, update this table, review the diff, commit. This file
is intentionally static so coverage results are deterministic and offline-repeatable.

| ID | Method | Path | Params | Expected (responseCode / message) | Kind |
|----|--------|------|--------|-----------------------------------|------|
| API-1  | GET    | /productsList        | — | 200 · all products | positive |
| API-2  | POST   | /productsList        | — | 405 · method not supported | negative (wrong verb) |
| API-3  | GET    | /brandsList          | — | 200 · all brands | positive |
| API-4  | PUT    | /brandsList          | — | 405 · method not supported | negative (wrong verb) |
| API-5  | POST   | /searchProduct       | search_product | 200 · matched products | positive |
| API-6  | POST   | /searchProduct       | — (missing) | 400 · search_product parameter is missing | negative (missing param) |
| API-7  | POST   | /verifyLogin         | email, password | 200 · User exists! | positive |
| API-8  | POST   | /verifyLogin         | password only (missing email) | 400 · email or password parameter is missing | negative (missing param) |
| API-9  | DELETE | /verifyLogin         | — | 405 · method not supported | negative (wrong verb) |
| API-10 | POST   | /verifyLogin         | email, password (invalid) | 404 · User not found! | negative (bad data) |
| API-11 | POST   | /createAccount       | full user payload | 201 · User created! | positive |
| API-12 | DELETE | /deleteAccount       | email, password | 200 · Account deleted! | positive |
| API-13 | PUT    | /updateAccount       | full user payload | 200 · User updated! | positive |
| API-14 | GET    | /getUserDetailByEmail | email | 200 · user detail JSON | positive |

## Mapping hints (for the coverage pass)

- `ProductsApi` methods cover API-1/3/5; API-2/4/6 are wrong-verb / missing-param
  variants driven directly via `.client`.
- `AccountsApi` methods cover API-7/10/11/12/13/14; API-8/9 are missing-param /
  wrong-verb variants.
- A scenario counts as **covered** only if a test asserts its **real** status
  (`status_code`, the body responseCode) AND, for the documented ones, the message.
  A positive endpoint hit without its negative variants is **partial** coverage.
