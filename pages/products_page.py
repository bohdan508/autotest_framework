"""Products page object — automationexercise.com/products."""

from playwright.sync_api import Locator, Page

from pages.base_page import BasePage


class ProductsPage(BasePage):
    path = "/products"

    def __init__(self, page: Page) -> None:
        super().__init__(page)
        self.cards = page.locator(".product-image-wrapper")
        self.view_cart_link = page.get_by_text("View Cart")
        self.continue_shopping_button = page.get_by_text("Continue Shopping")

    def add_to_cart_button(self, product_id: int) -> Locator:
        return self.page.locator(f'a.add-to-cart[data-product-id="{product_id}"]').first

    def add_to_cart_by_id(self, product_id: int) -> None:
        self.add_to_cart_button(product_id).click()

    def add_to_cart_by_name(self, name: str) -> None:
        card = self.cards.filter(has_text=name)
        card.get_by_role("link", name="Add to cart").first.click()

    def view_cart(self) -> None:
        self.view_cart_link.click()
