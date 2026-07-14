"""Root pytest fixtures."""

from collections.abc import Iterator

import pytest

from clients.api import Api
from clients.base_client import BaseClient


@pytest.fixture
def api_client() -> Iterator[BaseClient]:
    client = BaseClient()
    yield client
    client.session.close()  # teardown: release pooled connections


@pytest.fixture
def api(api_client: BaseClient) -> Api:
    return Api(api_client)
