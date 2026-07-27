"""Tests for the user endpoints"""

import allure
import pytest

from components.user import UserEntity
from utils.factories import make_user
from utils.wait import wait_until

pytestmark = allure.feature("Users")  # applies to every test in this file


@pytest.mark.smoke
@allure.title("Create a user")
def test_create_user(api_facade):
    user = UserEntity(api_facade, make_user())
    try:
        response = user.api.create()
        assert response.status_code == 201
        wait_until(user.api.exists, message="user should exist after create")
    finally:
        user.api.delete()


@pytest.mark.smoke
@allure.title("Verify login with correct credentials")
def test_verify_login_success(user_entity):
    response = user_entity.facade.accounts.verify_login(
        user_entity.data.email, user_entity.data.password
    )

    assert response.status_code == 200
    assert response.json["message"] == "User exists!"


@allure.title("Check get user by email endpoint")
def test_get_user(user_entity):
    response = user_entity.facade.accounts.get_user_by_email(user_entity.data.email)

    assert response.status_code == 200
    assert response.json["user"]["name"] == user_entity.data.name
    assert response.json["user"]["birth_day"] == user_entity.data.birth_date
    assert response.json["user"]["company"] == user_entity.data.company


@allure.title("Get user with non-existent email")
def test_get_user_not_found(api_facade):
    response = api_facade.accounts.get_user_by_email("not_existent@nowhere.com")
    print(response.json)

    assert response.status_code == 404
    assert response.json["message"] == "Account not found with this email, try another email!"


@allure.title("Create user without one of 3 required fields")
@pytest.mark.parametrize(
    "field",
    [
        pytest.param("name", id="no name"),
        pytest.param("email", id="no email"),
        pytest.param("password", id="no password"),
    ],
)
def test_create_user_negative(api_facade, field):
    payload = make_user().model_dump(exclude_none=True)
    del payload[field]
    request = api_facade.accounts.client.post("/createAccount", data=payload)

    assert request.status_code == 400
    assert request.json["message"] == f"Bad request, {field} parameter is missing in POST request."


@allure.title("Try logging in with wrong data")
@pytest.mark.parametrize(
    "email, password, code, message",
    [
        pytest.param("non_existing@gmail.com", "qwe123", 404, "User not found!", id="no user"),
        pytest.param("bad@format", "x", 404, "User not found!", id="bad email"),
    ],
)
def test_verify_login_negative(api_facade, email, password, code, message):
    request = api_facade.accounts.verify_login(email, password)

    assert request.status_code == code
    assert request.json["message"] == message


@pytest.mark.smoke
@allure.title("Update a user")
def test_update_user(user_entity):
    new_name, new_city = "NewName", "Kyiv"
    user_entity.data.name = new_name
    user_entity.data.city = new_city
    request = user_entity.api.update()

    assert request.status_code == 200
    updated_user = user_entity.api.details.json["user"]
    assert updated_user["name"] == new_name, f"expected name {new_name}, got {updated_user['name']}"
    assert updated_user["city"] == new_city, f"expected city {new_city}, got {updated_user['city']}"


@pytest.mark.smoke
@allure.title("Delete a user")
def test_delete_user(api_facade):
    user = UserEntity(api_facade, make_user())

    user.api.create()
    wait_until(user.api.exists, message="user creation failed")
    response = user.api.delete()

    assert response.status_code == 200
    assert response.json["message"] == "Account deleted!", "wrong delete message"
    wait_until(lambda: not user.api.exists(), message="user still exists after delete")


@allure.title("Try creating user with same email")
def test_create_user_duplicate_email(user_entity):
    request = user_entity.facade.accounts.client.post(
        "/createAccount", data=user_entity.data.model_dump(exclude_none=True)
    )
    assert request.status_code == 400
    assert request.json["message"] == "Email already exists!"
