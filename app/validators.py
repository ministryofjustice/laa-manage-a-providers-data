import re
from datetime import date

from wtforms import ValidationError


class ValidateCompaniesHouseNumber:
    """Validate Companies House number format."""

    def __init__(self, message=None):
        self.message = message or "Enter a valid Companies House number (8 characters)"

    def __call__(self, form, field):
        if field.data:
            # Companies House numbers are 8 characters long and may start with 2 letters
            if not re.match(r"^[A-Z0-9]{8}$", field.data.upper()):
                raise ValidationError(self.message)


class ValidatePastDate:
    """Validate that a date is today or in the past."""

    def __init__(self, message=None):
        self.message = message or "Date must be today or in the past"

    def __call__(self, form, field):
        if field.data and field.data > date.today():
            raise ValidationError(self.message)
