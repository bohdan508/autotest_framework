"""Tests for the <RESOURCE> endpoints.

Template — copy the blocks you need, delete the rest, then rename to
tests/api/test_<resource>.py. Placeholders are UPPERCASE.

Conventions baked in below (keep them):
- assert on `.status_code` (the BODY responseCode), never `.http_status`
- `@allure.title` on every test; `@pytest.mark.smoke` on the core happy paths
- positive create/update/delete goes through a resource-client method that sets
  `retry_until_ok=True`; NEGATIVE tests post directly via `.client.post(...)` so
  their expected 4xx returns immediately, unmasked
- build data with `make_user(**overrides)`; absorb server lag with `wait_until`
- always clean up anything you create (try/finally or a fixture)
"""

import allure
import pytest

from utils.factories import make_user
from utils.wait import wait_until

pytestmark = allure.feature("RESOURCE")  # groups every test in this file in Allure


# --- positive: simple GET -------------------------------------------------- #
@pytest.mark.smoke
@allure.title("SHORT HUMAN-READABLE TITLE")
def test_ENDPOINT_success(api_facade):
    response = api_facade.RESOURCE.METHOD_NAME(ARGS)

    assert response.status_code == 200
    assert response.json["KEY"], "EXPLAIN WHAT SHOULD BE TRUE"


# --- positive: create then verify, with cleanup ---------------------------- #
@pytest.mark.smoke
@allure.title("Create a RESOURCE")
def test_create_ENTITY(api_facade):
    payload = make_user()  # or the relevant factory / model
    try:
        response = api_facade.RESOURCE.create_METHOD(payload)
        assert response.status_code == 201
        wait_until(
            lambda: api_facade.RESOURCE.exists(ARGS),
            message="ENTITY should exist after create",
        )
    finally:
        api_facade.RESOURCE.delete_METHOD(ARGS)  # teardown even if asserts fail


# --- negative: missing required field -------------------------------------- #
# Post directly through .client (no retry_until_ok) so the 4xx comes back at once.
@allure.title("Create RESOURCE without a required field")
@pytest.mark.parametrize(
    "field",
    [
        pytest.param("name", id="no name"),
        pytest.param("email", id="no email"),
    ],
)
def test_create_ENTITY_negative(api_facade, field):
    payload = make_user().model_dump(exclude_none=True)
    del payload[field]
    request = api_facade.RESOURCE.client.post("/ENDPOINT", data=payload)

    assert request.status_code == 400
    assert request.json["message"] == f"Bad request, {field} parameter is missing in POST request."


# --- negative: wrong verb (the 200-but-405 gotcha) ------------------------- #
@allure.title("POST to a GET-only endpoint")
@pytest.mark.parametrize("path", ["/ENDPOINT_A", "/ENDPOINT_B"])
def test_wrong_verb(api_facade, path):
    request = api_facade.RESOURCE.client.post(path)

    assert request.http_status == 200  # transport really is 200 here...
    assert request.status_code == 405  # ...the real status is in the body
