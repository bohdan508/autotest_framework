"""Signup / account-information page object — automationexercise.com/signup.

Reached from LoginPage.start_signup() (which posts name + email).
Full account form that drives the same create-user flow as the accounts API, so
UserUiActions can build a user entirely through the UI.
"""

from playwright.sync_api import Page

from models.user import User
from pages.base_page import BasePage


class SignupPage(BasePage):
    # Reached via the login-page signup flow
    path = "/signup"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        # --- title: radio buttons
        self.title_mr = page.locator("#id_gender1")
        self.title_mrs = page.locator("#id_gender2")

        # --- account information (name + email are prefilled from signup) ------
        self.password = page.locator('[data-qa="password"]')
        self.birth_day = page.locator('[data-qa="days"]')
        self.birth_month = page.locator('[data-qa="months"]')
        self.birth_year = page.locator('[data-qa="years"]')

        # --- address information ------------------------------------------------
        self.first_name = page.locator('[data-qa="first_name"]')
        self.last_name = page.locator('[data-qa="last_name"]')
        self.company = page.locator('[data-qa="company"]')
        self.address1 = page.locator('[data-qa="address"]')
        self.address2 = page.locator('[data-qa="address2"]')
        self.country = page.locator('[data-qa="country"]')
        self.state = page.locator('[data-qa="state"]')
        self.city = page.locator('[data-qa="city"]')
        self.zipcode = page.locator('[data-qa="zipcode"]')
        self.mobile_number = page.locator('[data-qa="mobile_number"]')

        # --- submit -------------------------------------------------------------
        self.create_account_button = page.locator('[data-qa="create-account"]')
        self.signup_success = page.get_by_text("Account created!")

    def select_title(self, title: str) -> None:
        """Pick the Mr/Mrs radio"""
        (self.title_mr if title == "Mr" else self.title_mrs).check()

    def fill_account(self, user: User) -> None:
        """Fill the whole account form from a User model and submit."""
        if user.title:
            self.select_title(user.title)
        self.password.fill(user.password)

        self.birth_day.select_option(user.birth_date)
        self.birth_month.select_option(label=user.birth_month)
        self.birth_year.select_option(user.birth_year)

        self.first_name.fill(user.firstname)
        self.last_name.fill(user.lastname)
        self.company.fill(user.company)
        self.address1.fill(user.address1)
        self.address2.fill(user.address2)
        self.country.select_option(user.country)
        self.state.fill(user.state)
        self.city.fill(user.city)
        self.zipcode.fill(user.zipcode)
        self.mobile_number.fill(user.mobile_number)

        self.create_account_button.click()
