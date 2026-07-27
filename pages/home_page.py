"""Home page object — automationexercise.com"""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class HomePage(BasePage):
    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.logout_link = page.get_by_role("link", name="Logout")
        self.delete_account_link = page.get_by_role("link", name="Delete Account")

    def logged_in_as(self, name: str) -> Locator:
        """Locator for the navbar 'Logged in as <name>' indicator."""
        return self.page.get_by_text(f"Logged in as {name}")

    def logout(self) -> None:
        self.logout_link.click()

    def delete_account(self) -> None:
        self.delete_account_link.click()
