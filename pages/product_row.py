"""Shared product-row component.

ProductRow is used in checkout page as default one, CartRow in cart page
with additional delete button
"""

from playwright.sync_api import Locator


class ProductRow:
    """A product line item. Sub-locators are scoped to 'root', so they can never
    match a different row. Shared by the cart and checkout tables."""

    def __init__(self, root: Locator) -> None:
        self.root = root
        self.name = root.locator(".cart_description h4 a")  # -> #product-N .cart_description h4 a
        self.price = root.locator(".cart_price p")
        self.quantity = root.locator(".cart_quantity button")
        self.total = root.locator(".cart_total_price")


class CartRow(ProductRow):
    """Cart row = product row + the delete action."""

    def __init__(self, root: Locator) -> None:
        super().__init__(root)
        self.delete_button = root.locator(".cart_quantity_delete")

    def delete(self) -> None:
        self.delete_button.click()
