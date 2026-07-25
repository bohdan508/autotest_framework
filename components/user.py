"""User entity: data and action components."""

from clients.api import Api
from clients.base_client import ApiResponse
from models.user import User
from pages.pages import Pages


class UserEntity:
    def __init__(self, api: Api, data: User, pages: Pages | None = None) -> None:
        self.facade = api
        self.pages = pages  # UI facade; None for API-only tests (no browser)
        self.data = data
        self.api = UserApiActions(self)
        self.ui = UserUiActions(self)


class UserApiActions:
    """API actions for a UserEntity. Reads the entity's data via self.base."""

    def __init__(self, base: UserEntity) -> None:
        self.base = base

    def create(self) -> ApiResponse:
        return self.base.facade.accounts.create_account(self.base.data)

    def update(self) -> ApiResponse:
        return self.base.facade.accounts.update_account(self.base.data)

    def delete(self) -> ApiResponse:
        user = self.base.data
        return self.base.facade.accounts.delete_account(user.email, user.password)

    def exists(self) -> bool:
        user = self.base.data
        return self.base.facade.accounts.exists(user.email, user.password)

    @property
    def details(self) -> ApiResponse:
        return self.base.facade.accounts.get_user_by_email(self.base.data.email)


class UserUiActions:
    """UI actions for a UserEntity"""

    def __init__(self, base: UserEntity) -> None:
        self.base = base

    @property
    def _pages(self) -> Pages:
        if self.base.pages is None:
            raise RuntimeError("UserEntity was built without a pages facade; "
                               "pass pages=... to use .ui actions")
        return self.base.pages

    def create(self) -> None:
        """Register the user entirely through the UI: the login page's signup form
        posts name+email, then the account form is filled and submitted."""
        user = self.base.data
        self._pages.login.open().start_signup(user.name, user.email)
        self._pages.signup.fill_account(user)

    def login(self) -> None:
        user = self.base.data
        self._pages.login.open().login(user.email, user.password)
