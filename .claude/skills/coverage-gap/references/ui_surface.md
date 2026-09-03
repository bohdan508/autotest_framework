# UI surface — automationexercise.com

Source of truth for UI coverage: the pages and user flows worth testing. Curated
(not crawled) so coverage results stay deterministic. To refresh, walk the site,
update the tables, review the diff, commit.

Scope note: this is a *testable-flow* inventory, not every URL on the site. It
targets the flows a portfolio suite should demonstrate. Marketing/static pages
(About, Test Cases doc, etc.) are intentionally out of scope unless a flow needs
them.

## Pages (page objects)

| Page | Path | Page object |
|------|------|-------------|
| Home            | /          | HomePage |
| Login / Signup  | /login     | LoginPage |
| Signup details  | /signup    | SignupPage |
| Products        | /products  | ProductsPage |
| Cart            | /view_cart | CartPage |
| Checkout        | /checkout  | CheckoutPage |
| Payment         | /payment   | PaymentPage |
| Product detail  | /product_details/{id} | — (none yet) |

## Flows (what a test should exercise)

| ID | Flow | Primary pages | Kind |
|----|------|---------------|------|
| UI-1  | Register a new user via UI          | login → signup | positive |
| UI-2  | Login with valid credentials        | login → home | positive |
| UI-3  | Login with invalid credentials      | login | negative |
| UI-4  | Logout                              | home → login | positive |
| UI-5  | Register with an existing email      | login | negative |
| UI-6  | Delete account                      | home → delete | positive |
| UI-7  | Search a product                    | products | positive |
| UI-8  | Add product to cart                 | products → cart | positive |
| UI-9  | Remove product from cart            | cart | positive |
| UI-10 | Checkout (review order + comment)   | cart → checkout | positive |
| UI-11 | Payment + order confirmation        | payment | positive |
| UI-12 | Download invoice                    | payment | positive |
| UI-13 | View product detail / reviews       | product_details | positive |
| UI-14 | Subscribe to newsletter (footer)    | home/cart footer | positive |
| UI-15 | Contact-us form submission          | /contact_us | positive |

## Mapping hints (for the coverage pass)

- A flow is **covered** if a test in `tests/ui/` drives it end-to-end and asserts
  the outcome with Playwright `expect` (visible element / URL) and/or an API check.
- A flow whose page object exists but has no test is a **gap with scaffolding**
  (cheap to close). A flow with neither page object nor test is a **full gap**.
- UI-13/14/15 currently have no page object — flag as full gaps if untested.
