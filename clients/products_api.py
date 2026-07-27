"""Client for the products endpoints (get all, get by name and list brands)."""

from clients.base_client import ApiResponse, BaseClient


class ProductsApi:
    def __init__(self, client: BaseClient) -> None:
        self.client = client

    def list_products(self) -> ApiResponse:
        """GET /productsList - returns every product in the catalogue."""
        return self.client.get("/productsList")

    def search_product(self, product_name: str) -> ApiResponse:
        """POST /searchProduct - finds a product by name."""
        return self.client.post("/searchProduct", data={"search_product": product_name})

    def list_brands(self) -> ApiResponse:
        """GET /brandsList - returns every brand in the catalogue."""
        return self.client.get("/brandsList")
