import re
from datetime import date

from wtforms import ValidationError

from app.fields import GovDateField


class ValidateGovDateField:
    """Validate GovDateField for incomplete dates and invalid real dates."""

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if not isinstance(field, GovDateField):
            return

        # Get the original raw data if available
        valuelist = getattr(field, "_original_raw_data", None)
        if not valuelist:
            return

        # Validate incomplete date
        self._validate_incomplete_date(field, valuelist)

        # Validate real date (if field couldn't parse the date)
        self._validate_real_date(field, valuelist)

    @staticmethod
    def _validate_incomplete_date(field, valuelist):
        """Validate that all date components are present and valid format."""
        from wtforms.validators import Optional

        # Get the raw form data - expecting [day, month, year]
        raw_data = valuelist if isinstance(valuelist, list) else [valuelist]

        # Pad with empty strings if we don't have 3 elements
        while len(raw_data) < 3:
            raw_data.append("")

        day, month, year = raw_data[:3]

        # Check what's missing
        missing_parts = []

        # Check day
        if not day or day.strip() == "":
            missing_parts.append("day")

        # Check month
        if not month or month.strip() == "":
            missing_parts.append("month")

        # Check year
        if not year or year.strip() == "":
            missing_parts.append("year")
        elif len(year.strip()) != 4 or not year.strip().isdigit():
            # Year exists but is not 4 digits
            raise ValidationError("Year must include 4 numbers")

        # If we have missing parts, check if field is optional
        if missing_parts:
            # If all parts are missing and field is optional, allow it
            if len(missing_parts) == 3:
                # Check if field has Optional validator
                has_optional = any(isinstance(validator, Optional) for validator in field.validators)
                if has_optional:
                    return  # Allow empty field for optional fields

            # Create error message and raise validation error
            if len(missing_parts) == 1:
                message = f"Date must include a {missing_parts[0]}"
            elif len(missing_parts) == 2:
                message = f"Date must include a {missing_parts[0]} and {missing_parts[1]}"
            else:  # all 3 missing (for required fields)
                message = "Date must include a day, month and year"

            raise ValidationError(message)

    @staticmethod
    def _validate_real_date(field, valuelist):
        """Validate that the date is a real date."""
        # If field couldn't parse the data but all components were present
        if field.data is None and valuelist:
            raw_data = valuelist if isinstance(valuelist, list) else [valuelist]

            # Pad with empty strings if we don't have 3 elements
            while len(raw_data) < 3:
                raw_data.append("")

            day, month, year = raw_data[:3]

            # Check if all parts are present (and not just whitespace)
            if day and day.strip() and month and month.strip() and year and year.strip():
                raise ValidationError("Date must be a real date")


class ValidateCompaniesHouseNumber:
    """Validate Companies House number format."""

    def __init__(self, message=None):
        self.message = message or "Enter a valid Companies House number (8 characters)"

    def __call__(self, form, field):
        if field.data:
            # Companies House numbers are 8 characters long
            if not re.match(r"^[A-Z0-9]{8}$", field.data.upper()):
                raise ValidationError(self.message)


class ValidatePastDate:
    """Validate that a date is today or in the past."""

    def __init__(self, message=None):
        self.message = message or "Date must be today or in the past"

    def __call__(self, form, field):
        if field.data and field.data > date.today():
            raise ValidationError(self.message)


class ValidateSearchResults:
    """Check if search returned results, checks form.num_results to see how many results were returned."""

    def __init__(self, message=None):
        self.message = message or "No providers found. Check the spelling and search for something else."

    def __call__(self, form, field):
        if field.data and hasattr(form, "num_results") and form.num_results == 0:
            raise ValidationError(self.message)
