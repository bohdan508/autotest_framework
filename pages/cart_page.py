"""Cart page object — automationexercise.com/view_cart."""

from playwright.sync_api import Page

from pages.base_page import BasePage
from pages.product_row import CartRow


class CartPage(BasePage):
    path = "/view_cart"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.empty_cart_message = page.get_by_text('Cart is empty!')

    def row(self, product_id: int) -> CartRow:
        """The cart row for a product, identified by its id (tr id='product-N')."""
        return CartRow(self.page.locator(f"#product-{product_id}"))

    def row_by_name(self, name: str) -> CartRow:
        return CartRow(self.page.locator("tr").filter(has_text=name))

    def proceed_to_checkout(self) -> None:
        """Go to the checkout page (requires a logged-in user)."""
        self.page.get_by_text("Proceed To Checkout").click()
