"""API - one object that exposes every resource client."""

from clients.accounts_api import AccountsApi
from clients.base_client import BaseClient
from clients.products_api import ProductsApi


class Api:
    def __init__(self, client: BaseClient) -> None:
        self.products = ProductsApi(client)
        self.accounts = AccountsApi(client)
