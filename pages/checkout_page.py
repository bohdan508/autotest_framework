"""Checkout page object — automationexercise.com/checkout.

The order-review step, reached from the cart's "Proceed To Checkout" (requires a
logged-in user).
"""

from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.product_row import ProductRow


class CheckoutPage(BasePage):
    # Reached via CartPage.proceed_to_checkout(), not opened directly.
    path = "/checkout"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.delivery_address = page.locator("#address_delivery")
        self.comment = page.locator('textarea[name="message"]')
        # text, not get_by_role('link'): it's an <a> without href
        self.place_order_button = page.get_by_text("Place Order")
        self.total_amount = page.locator(".cart_total_price").last

    def row(self, product_id: int) -> ProductRow:
        """Order-review row for a product (shared component — no delete on checkout)."""
        return ProductRow(self.page.locator(f"#product-{product_id}"))

    def add_comment(self, text: str) -> None:
        self.comment.fill(text)

    def place_order(self) -> None:
        """Submit the order — navigates on to the payment page."""
        self.place_order_button.click()
