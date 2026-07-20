"""Product response model.

Products are read-only catalog data, so this models a *response* (parsed from
GET /productsList), not a payload we send. Only the fields tests assert on are
declared; pydantic ignores the rest (e.g. the deeply-nested category.usertype),
so upstream drift won't break parsing.
"""

import re

from pydantic import BaseModel, computed_field


class Product(BaseModel):
    id: int
    name: str
    price: str  # the API returns "Rs. 500" - a string with currency, not a number
    brand: str | None = None

    @computed_field
    @property
    def price_value(self) -> int:
        """Numeric price parsed out of the "Rs. 500" string (0 if no digits).
        r"\D" - the pattern. \D is the regex class meaning "any character that is not a digit 0–9"
        "" - the replacement
        self.price - the input
        """
        digits = re.sub(r"\D", "", self.price)
        return int(digits) if digits else 0
