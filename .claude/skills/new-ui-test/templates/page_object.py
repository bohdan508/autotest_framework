"""Page object skeleton — automationexercise.com/PATH.

Copy to pages/<name>_page.py, rename the class, then register it ONE line in
the Pages facade (pages/pages.py):

    self.<name> = <Name>Page(page)

Rules (keep them):
- subclass BasePage; set `path` (relative to base_url); open() navigates + returns self
- locators live in __init__ — prefer `data-qa` attrs, then role/text, then CSS
- methods are user ACTIONS only (fill, click, navigate). NO assertions here —
  assertions belong in the test via Playwright `expect`.
- for repeated table rows, reuse ProductRow/CartRow (pages/product_row.py) scoped
  to a single <tr>, rather than page-level locators that can match the wrong row.
"""

from playwright.sync_api import Page

from pages.base_page import BasePage


class NamePage(BasePage):
    path = "/PATH"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.some_field = page.locator('[data-qa="SOME-QA"]')
        self.some_button = page.get_by_role("button", name="SOME LABEL")
        self.some_message = page.get_by_text("SOME TEXT")  # exposed for the test to assert on

    def do_action(self, value: str) -> None:
        """One user action per method."""
        self.some_field.fill(value)
        self.some_button.click()
