"""Root pytest fixtures."""

import re
from collections.abc import Iterator

import pytest

from clients.api import Api
from clients.base_client import BaseClient
from components.user import UserEntity
from config.settings import settings
from pages.pages import Pages
from utils.factories import make_user
from utils.wait import wait_until


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """Anchor the log file to the project root, whatever the working directory.

    'log_file' in pytest.ini is resolved relative to the launch directory, so
    running from an IDE scatters logs. Pinning it to rootpath keeps one
    run.log at the project root for API and UI test.
    """
    config.option.log_file = str(config.rootpath / "logs" / "run.log")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    # Chromium: open the window maximized
    return {
        **browser_type_launch_args,
        "args": ["--window-position=0,0", "--window-size=1440,900"],
    }


@pytest.fixture
def browser_context_args(browser_context_args, request):
    # let the window drive the size instead of a fixed 1280x720 viewport
    if request.config.getoption("--headed"):
        return {**browser_context_args, "no_viewport": True}
    return browser_context_args


@pytest.fixture
def api_client() -> Iterator[BaseClient]:
    client = BaseClient()
    yield client
    client.session.close()  # teardown: release pooled connections


@pytest.fixture
def api_facade(api_client: BaseClient) -> Api:
    return Api(api_client)


@pytest.fixture(scope="session")
def base_url() -> str:
    """Overwritten version of pytest-base-url, used invisibly
    by Playwright (pytest-playwright picks it up and feeds it
    into the browser context it creates)"""
    return settings.base_url


@pytest.fixture
def pages(page) -> Pages:
    """UI twin of api_facade: the page-object facade over pytest-playwright's
    page fixture. Function-scoped, so each test gets a fresh browser page. Also makes
    it ads-free so overlays can't cover the UI"""
    page.route(
        re.compile(r"googlesyndication|doubleclick|googleads|adservice|google-analytics"),
        lambda route: route.abort(),
    )
    return Pages(page)


@pytest.fixture
def user_entity(api_facade, pages):
    """A created UserEntity - data + .api actions"""
    user = UserEntity(api_facade, make_user(), pages)
    user.api.create()
    wait_until(user.api.exists, message="user should exist after create")
    yield user
    user.api.delete()


@pytest.fixture
def logged_in_user(user_entity):
    """A UserEntity created via API and logged in through the UI."""
    user_entity.ui.login()
    return user_entity


@pytest.fixture
def product_in_cart(api_facade, pages):
    product = api_facade.products.list_products().json["products"][0]
    pages.products.open()
    pages.products.add_to_cart_by_id(product["id"])
    pages.products.view_cart()
    return product
