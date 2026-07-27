"""Login / signup page object — automationexercise.com/login.

Mirrors the accounts API on the UI side: this page drives the same
create/login/delete-user flows a real user would.
"""

from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    path = "/login"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # --- login form ---
        self.login_email = page.locator('[data-qa="login-email"]')
        self.login_password = page.locator('[data-qa="login-password"]')
        self.login_button = page.locator('[data-qa="login-button"]')
        self.login_error = page.get_by_text("Your email or password is incorrect!")
        # --- signup form ---
        self.signup_name = page.locator('[data-qa="signup-name"]')
        self.signup_email = page.locator('[data-qa="signup-email"]')
        self.signup_button = page.locator('[data-qa="signup-button"]')
        self.signup_error_duplicate = page.get_by_text("Email Address already exist!")

    def login(self, email: str, password: str) -> None:
        """Fill the login form and submit."""
        self.login_email.fill(email)
        self.login_password.fill(password)
        self.login_button.click()

    def start_signup(self, name: str, email: str) -> None:
        """Fill the signup form and submit."""
        self.signup_name.fill(name)
        self.signup_email.fill(email)
        self.signup_button.click()
