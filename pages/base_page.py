"""Base page object.

The UI counterpart to BaseClient: concrete pages (LoginPage etc) subclass this
instead of touching Playwright's 'page' directly.
"""

from typing import Self

from playwright.sync_api import Page


class BasePage:
    path = '/'

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self) -> Self:
        """Navigate to this page's 'path' (relative to base_url). Returns self
        so a test can LoginPage(page).open().login(...)."""
        self.page.goto(self.path)
        return self
