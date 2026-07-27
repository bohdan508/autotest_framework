"""Test-data factories to create object with one call"""

from uuid import uuid4

from faker import Faker

from models.user import User

fake = Faker()

# The site accepts only this fixed set of countries; Faker's country() would
# return unsupported values
_COUNTRIES = (
    "India",
    "United States",
    "Canada",
    "Australia",
    "Israel",
    "New Zealand",
    "Singapore",
)


def make_user(**overrides) -> User:
    """Builds a valid class User.
    Example:

        make_user()                         # all fields random and valid
        make_user(name="Ada", title="Mrs")  # some fields are user input
        make_user(password=None)            # drop a field to test negative scenario
    """
    dob = fake.date_of_birth(minimum_age=18, maximum_age=80)
    defaults = {
        "name": fake.name(),
        "email": f"aqa_{uuid4().hex[:12]}@example.com",
        "password": fake.password(length=12),
        "title": fake.random_element(("Mr", "Mrs")),
        "birth_date": str(dob.day),
        "birth_month": dob.strftime("%B"),
        "birth_year": str(dob.year),
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "company": fake.company(),
        "address1": fake.street_address(),
        "address2": fake.secondary_address(),
        "country": fake.random_element(_COUNTRIES),
        "zipcode": fake.postcode(),
        "state": fake.state(),
        "city": fake.city(),
        "mobile_number": fake.msisdn(),
    }
    defaults.update(overrides)
    return User(**defaults)
