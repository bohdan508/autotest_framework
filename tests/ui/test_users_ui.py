import allure
import pytest
from playwright.sync_api import expect

from components.user import UserEntity
from utils.factories import make_user
from utils.wait import wait_until


@pytest.mark.smoke
@allure.title("UI Logging with right user data")
def test_login_with_real_user(user_entity, pages):
    pages.login.open().login(user_entity.data.email, user_entity.data.password)
    expect(pages.home.logged_in_as(user_entity.data.name)).to_be_visible()


@pytest.mark.smoke
@allure.title("UI Log-out")
def test_logout(user_entity, page, pages):
    pages.login.open().login(user_entity.data.email, user_entity.data.password)
    pages.home.logout()
    expect(page).to_have_url("/login")
    expect(pages.home.logged_in_as(user_entity.data.name)).to_be_hidden()


@pytest.mark.smoke
@allure.title("UI delete account")
def test_delete_account(api_facade, pages, page):
    user = UserEntity(api_facade, make_user())
    try:
        response = user.api.create()
        assert response.status_code == 201
        wait_until(user.api.exists, message="user should exist after create")

        pages.login.open().login(user.data.email, user.data.password)
        pages.home.delete_account()
        expect(page).to_have_url("/delete_account")
        expect(page.get_by_text("Account Deleted!")).to_be_visible()
        assert not user.api.exists(), "account should be gone after UI delete"
    finally:
        if user.api.exists():
            user.api.delete()


@allure.title("UI Logging in with wrong user data")
def test_login_wrong_credentials(pages):
    pages.login.open().login("bad@example.com", "wrong")
    expect(pages.login.login_error).to_be_visible()


@allure.title("UI Sign up with real data")
def test_signup_via_ui(api_facade, pages):
    user = UserEntity(api_facade, make_user(), pages)
    try:
        user.ui.create()
        expect(pages.signup.signup_success).to_be_visible()
        assert user.api.exists(), "account created via UI should exist per API"
    finally:
        if user.api.exists():
            user.api.delete()
