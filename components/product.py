"""Product entity: data and action components."""

from clients.api import Api


class ProductEntity:
    def __init__(self, api: Api) -> None:
        self.facade = api
        # self.ui = ProductUiActions(self)
