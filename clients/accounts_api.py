"""Client for the account/auth endpoints (create, update, delete, verify and get)."""

from clients.base_client import ApiResponse, BaseClient
from models.user import User


class AccountsApi:
    def __init__(self, client: BaseClient) -> None:
        self.client = client

    def get_user_by_email(self, email: str) -> ApiResponse:
        """GET /getUserDetailByEmail - returns user details by email."""
        return self.client.get('/getUserDetailByEmail', params={'email': email})

    def verify_login(self, email: str, password: str) -> ApiResponse:
        """POST /verifyLogin - returns 'User exists!' if the data is right and user was crested before."""
        return self.client.post('/verifyLogin', data={'email': email, 'password': password})

    def create_account(self, user: User) -> ApiResponse:
        """POST /createAccount - returns 'User created!' on success."""
        return self.client.post('/createAccount', data=user.model_dump(exclude_none=True))

    def update_account(self, user: User) -> ApiResponse:
        """PUT /updateAccount - returns 'User updated!' on success.
        Email + password identify the account, email is the lookup key,
        not editable (only delete-recreate in that case)
        """
        return self.client.put('/updateAccount', data=user.model_dump(exclude_none=True))

    def delete_account(self, email: str, password: str) -> ApiResponse:
        """DELETE /deleteAccount - returns 'Account deleted!' on success."""
        return self.client.delete('/deleteAccount', data={'email': email, 'password': password})
