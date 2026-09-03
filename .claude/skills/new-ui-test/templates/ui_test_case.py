"""UI tests for the <FLOW> flow.

Template — copy the blocks you need, delete the rest, rename to
tests/ui/test_<flow>_ui.py. Placeholders are UPPERCASE.

Conventions baked in below (keep them):
- assertions use Playwright `expect(...)` IN THE TEST (never in page objects)
- set state up the FAST way (via api_facade / entity API actions), then drive the
  UI, then verify via UI and/or API
- URLs are relative ("/login") — base_url comes from settings via pytest-playwright
- `@allure.title` on every test; `@pytest.mark.smoke` on the core happy paths
- clean up any account/resource a test creates (try/finally)
- the `pages` fixture already blocks ads/analytics, so overlays won't cover the UI
"""

import allure
import pytest
from playwright.sync_api import expect

from components.user import UserEntity
from utils.factories import make_user
from utils.wait import wait_until


# --- happy path with an existing fixture ----------------------------------- #
# user_entity = created via API + cleaned up; logged_in_user = that, logged in via UI.
@pytest.mark.smoke
@allure.title("UI SHORT TITLE")
def test_FLOW_success(user_entity, pages):
    pages.SCREEN.open().DO_ACTION(ARGS)

    expect(pages.SCREEN.SOME_MESSAGE).to_be_visible()


# --- set up via API, act via UI, verify via API + UI, with cleanup --------- #
@pytest.mark.smoke
@allure.title("UI SHORT TITLE")
def test_FLOW_with_setup(api_facade, pages, page):
    user = UserEntity(api_facade, make_user())
    try:
        assert user.api.create().status_code == 201
        wait_until(user.api.exists, message="user should exist after create")

        pages.login.open().login(user.data.email, user.data.password)
        pages.SCREEN.DO_ACTION(ARGS)

        expect(page).to_have_url("/EXPECTED_PATH")
        assert user.api.exists(), "EXPLAIN THE API-SIDE EXPECTATION"
    finally:
        if user.api.exists():
            user.api.delete()


# --- table-row assertion (reuses the shared row component) ------------------ #
@allure.title("UI SHORT TITLE")
def test_FLOW_row(product_in_cart, pages):
    row = pages.cart.row(product_in_cart.id)  # or pages.checkout.row(...)

    expect(row.name).to_have_text(product_in_cart.name)
    expect(row.total).to_have_text(product_in_cart.price)


# --- negative: an error surface is shown ----------------------------------- #
@allure.title("UI SHORT TITLE")
def test_FLOW_negative(pages):
    pages.SCREEN.open().DO_ACTION(BAD_ARGS)

    expect(pages.SCREEN.SOME_ERROR).to_be_visible()


# --- entity-driven: same data through the UI actions ----------------------- #
# Pass `pages` to the entity so its .ui actions have a browser to drive.
@allure.title("UI SHORT TITLE")
def test_FLOW_via_entity(api_facade, pages):
    user = UserEntity(api_facade, make_user(), pages)
    try:
        user.ui.create()
        expect(pages.signup.signup_success).to_be_visible()
        assert user.api.exists(), "account created via UI should exist per API"
    finally:
        if user.api.exists():
            user.api.delete()
