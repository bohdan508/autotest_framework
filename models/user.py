"""User payload model.

createAccount and updateAccount take the same 17 form fields, so the
payload is modelled once and reused by both.
"""

from pydantic import BaseModel


class User(BaseModel):
    # --- required: createAccount rejects the request without these ---------- #
    name: str
    email: str
    password: str

    # --- optional: sent only when set -------------------------------------- #
    title: str | None = None  # "Mr" / "Mrs"
    birth_date: str | None = None  # day, e.g. "15"
    birth_month: str | None = None  # f.e "May"
    birth_year: str | None = None  # f.e "1990"
    firstname: str | None = None
    lastname: str | None = None
    company: str | None = None
    address1: str | None = None
    address2: str | None = None
    country: str | None = None  # the site only accepts a fixed set (India,
    # United States, Canada, Australia, Israel, New Zealand, Singapore).
    zipcode: str | None = None
    state: str | None = None
    city: str | None = None
    mobile_number: str | None = None
