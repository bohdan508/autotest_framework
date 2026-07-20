"""Tests for the products endpoints (read-only catalogue)."""

import allure
import pytest

from models.product import Product

pytestmark = allure.feature('Products')


@pytest.mark.smoke
@allure.title('Return the products catalogue')
def test_list_products(api_facade):
    request = api_facade.products.list_products()

    assert request.status_code == 200
    products = [Product(**p) for p in request.json["products"]]
    assert products, 'expected a non-empty catalogue'
    assert all(p.price_value > 0 for p in products), 'every product needs a price'


@allure.title('Find matching products via search')
def test_search_product(api_facade):
    request = api_facade.products.search_product('tshirt')

    assert request.status_code == 200
    assert request.json["products"], 'expected at least one match for \'tshirt\''


@pytest.mark.smoke
@allure.title('Return the list of brands')
def test_list_brands(api_facade):
    request = api_facade.products.list_brands()

    assert request.status_code == 200
    assert request.json['brands'], 'expected a non-empty brands list'


@allure.title('Try to POST to endpoints that only except GET requests')
@pytest.mark.parametrize('path', ['/productsList', '/brandsList'])
def test_post_to_get_endpoints(api_facade, path):
    request = api_facade.products.client.post(path)

    assert request.http_status == 200
    assert request.status_code == 405


@allure.title('Search for not existing product')
def test_search_not_existing_product(api_facade):
    request = api_facade.products.search_product('qwe-nonexistent-zxc')

    assert request.status_code == 200
    assert request.json['products'] == [], 'expected empty list when searching for not existing one'


@allure.title('Search with no search_product parameter')
def test_search_product_no_search_parameter(api_facade):
    request = api_facade.products.client.post('/searchProduct')

    assert request.status_code == 400
    assert request.json['message'] == 'Bad request, search_product parameter is missing in POST request.', \
        'wrong error message'
