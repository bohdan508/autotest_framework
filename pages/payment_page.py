"""Payment page object — automationexercise.com/payment."""

from playwright.sync_api import Page

from models.user import User
from pages.base_page import BasePage


class PaymentPage(BasePage):
    path = "/payment"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.name_on_card = page.locator('[data-qa="name-on-card"]')
        self.card_number = page.locator('[data-qa="card-number"]')
        self.cvc = page.locator('[data-qa="cvc"]')
        self.expiration_month = page.locator('[data-qa="expiry-month"]')
        self.expiration_year = page.locator('[data-qa="expiry-year"]')
        self.confirm_button = page.locator('[data-qa="pay-button"]')

        self.payment_success = page.get_by_text("Order Placed!")
        self.download_invoice = page.get_by_text("Download Invoice")

    def fill_payment_data(self, user: User):
        exp_month = user.card_exp_date.split("/")[0]
        exp_year = user.card_exp_date.split("/")[1]
        self.name_on_card.fill(user.name)
        self.card_number.fill(user.card_number)
        self.cvc.fill(user.card_cvc)
        self.expiration_month.fill(exp_month)
        self.expiration_year.fill(exp_year)

        self.confirm_button.click()
