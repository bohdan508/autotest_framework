"""Root pytest fixtures."""

from collections.abc import Iterator

import pytest

from clients.api import Api
from clients.base_client import BaseClient
from components.user import UserEntity
from utils.factories import make_user
from utils.wait import wait_until


@pytest.hookimpl(tryfirst=True)
def pytest_configure(config: pytest.Config) -> None:
    """Anchor the log file to the project root, whatever the working directory.

    `log_file` in pytest.ini is resolved relative to the launch directory, so
    running from an IDE (cwd = the test's folder) scatters logs/ around. Pinning
    it to rootpath keeps one run.log at the project root for API and UI alike.
    """
    config.option.log_file = str(config.rootpath / "logs" / "run.log")


@pytest.fixture
def api_client() -> Iterator[BaseClient]:
    client = BaseClient()
    yield client
    client.session.close()  # teardown: release pooled connections


@pytest.fixture
def api_facade(api_client: BaseClient) -> Api:
    return Api(api_client)


@pytest.fixture
def user_entity(api_facade):
    """A created UserEntity - data + .api actions - cleaned up after the test."""
    user = UserEntity(api_facade, make_user())
    user.api.create()
    wait_until(user.api.exists, message='user should exist after create')
    yield user
    user.api.delete()
