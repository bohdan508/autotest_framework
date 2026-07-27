"""Pages - one object that exposes every page object.

The UI twin of clients.Api: built over a single Playwright 'page', so a test
reaches every screen via 'pages.login', 'pages.signup' etc
"""

from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.products_page import ProductsPage
from pages.signup_page import SignupPage


class Pages:
    def __init__(self, page: Page) -> None:
        self.login = LoginPage(page)
        self.signup = SignupPage(page)
        self.home = HomePage(page)
        self.products = ProductsPage(page)
        self.cart = CartPage(page)
        self.checkout = CheckoutPage(page)
