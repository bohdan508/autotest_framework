import re

import allure
import pytest
from playwright.sync_api import expect


@pytest.mark.smoke
@allure.title("UI add product to cart")
def test_add_to_cart(api_facade, pages):
    product = api_facade.products.list_products().json["products"][0]
    pages.products.open()
    pages.products.add_to_cart_by_id(product["id"])
    pages.products.view_cart()

    row = pages.cart.row(product["id"])
    expect(row.name).to_have_text(product["name"])
    expect(row.total).to_have_text(product["price"])


@allure.title("UI Delete product from cart")
def test_delete_from_cart(product_in_cart, pages):
    row = pages.cart.row(product_in_cart.id)
    row.delete()
    expect(row.root).to_have_count(0)
    expect(pages.cart.empty_cart_message).to_be_visible()


@allure.title("UI checkout flow")
def test_checkout_payment(logged_in_user, product_in_cart, page, pages):
    pages.cart.proceed_to_checkout()

    row = pages.checkout.row(product_in_cart.id)
    expect(row.name).to_have_text(product_in_cart.name)

    pages.checkout.add_comment("Test comment")
    pages.checkout.place_order()

    expect(page).to_have_url(re.compile(r"/payment"))

    pages.payment.fill_payment_data(logged_in_user.data)

    expect(page).to_have_url(f"/payment_done/{product_in_cart.price_value}")
    expect(pages.payment.payment_success).to_be_visible()

    with page.expect_download() as download_info:
        pages.payment.download_invoice.click()

    download = download_info.value
    file_path = download.path()

    with open(file_path) as file:
        content = file.read()

    assert content == (f"Hi {logged_in_user.data.name}, Your total purchase amount "
                       f"is {product_in_cart.price_value}. Thank you")
