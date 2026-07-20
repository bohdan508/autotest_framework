"""User entity: data and action components."""

from clients.api import Api
from clients.base_client import ApiResponse
from models.user import User


class UserEntity:
    def __init__(self, api: Api, data: User) -> None:
        self.facade = api
        self.data = data
        self.api = UserApiActions(self)
        # self.ui = UserUiActions(self)


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


# class UserUiActions:
#     def __init__(self, base: UserEntity) -> None:
#         self.base = base
#
#     def create(self):
