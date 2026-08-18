"""Root pytest fixtures."""

import random
import re
from collections.abc import Iterator

import allure
import pytest

from clients.api import Api
from clients.base_client import BaseClient
from components.user import UserEntity
from config.settings import settings
from models.product import Product
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


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to the Allure report when a UI test fails.

    pytest-playwright already saves a screenshot to disk on failure, but nothing
    wires it into Allure. This hook runs during the test's 'call' phase (the page
    is still open) and, on failure, grabs the live page and attaches it. API tests
    have no 'page' fixture, so they're skipped.
    """
    outcome = yield
    report = outcome.get_result()
    if report.when == "call" and report.failed:
        page = item.funcargs.get("page")
        if page is not None:
            allure.attach(
                page.screenshot(full_page=True),
                name="screenshot-on-failure",
                attachment_type=allure.attachment_type.PNG,
            )


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
    response = api_facade.products.list_products()
    products = [Product(**p) for p in response.json["products"]]
    product = products[random.randint(0, len(products))]

    pages.products.open()
    pages.products.add_to_cart_by_id(product.id)
    pages.products.view_cart()
    return product
