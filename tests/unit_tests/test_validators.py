from datetime import date
from unittest.mock import Mock

import pytest
from wtforms import Form, ValidationError

from app.fields import GovDateField
from app.validators import ValidateCompaniesHouseNumber, ValidateGovDateField, ValidatePastDate


class TestValidateCompaniesHouseNumber:
    def test_valid_companies_house_numbers(self):
        """Test validation of valid Companies House numbers."""
        validator = ValidateCompaniesHouseNumber()
        form = Mock()

        valid_numbers = [
            "AB123456",  # 2 letters + 6 digits
            "12345678",  # 8 digits
            "BC234567",  # 2 letters + 6 digits
            "87654321",  # 8 digits
        ]

        for number in valid_numbers:
            field = Mock()
            field.data = number
            # Should not raise ValidationError
            validator(form, field)

    def test_invalid_companies_house_numbers(self):
        """Test validation rejects invalid Companies House numbers."""
        validator = ValidateCompaniesHouseNumber()
        form = Mock()

        invalid_numbers = [
            "1234567",  # Only 7 digits
            "123456789",  # 9 digits
            "12-34567",  # Contains hyphen
            "AB 12345",  # Contains space
        ]

        for number in invalid_numbers:
            field = Mock()
            field.data = number
            with pytest.raises(ValidationError) as exc_info:
                print(field.data)
                validator(form, field)
            assert "Enter a valid Companies House number" in str(exc_info.value)

    def test_empty_field_data(self):
        """Test that empty field data doesn't raise validation error."""
        validator = ValidateCompaniesHouseNumber()
        form = Mock()
        field = Mock()
        field.data = None

        # Should not raise ValidationError for None/empty data
        validator(form, field)

    def test_custom_error_message(self):
        """Test custom error message."""
        custom_message = "Custom error message"
        validator = ValidateCompaniesHouseNumber(message=custom_message)
        form = Mock()
        field = Mock()
        field.data = "invalid"

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == custom_message


class TestValidatePastDate:
    def test_valid_past_dates(self):
        """Test validation allows past dates."""
        validator = ValidatePastDate()
        form = Mock()

        # Test with past dates
        past_dates = [
            date(2020, 1, 1),
            date(2023, 12, 31),
            date.today().replace(year=date.today().year - 1),  # Last year
        ]

        for test_date in past_dates:
            field = Mock()
            field.data = test_date
            # Should not raise ValidationError
            validator(form, field)

    def test_valid_today_date(self):
        """Test validation allows today's date."""
        validator = ValidatePastDate()
        form = Mock()
        field = Mock()
        field.data = date.today()

        # Should not raise ValidationError for today
        validator(form, field)

    def test_invalid_future_dates(self):
        """Test validation rejects future dates."""
        validator = ValidatePastDate()
        form = Mock()

        # Test with future dates
        future_dates = [
            date(2030, 1, 1),
            date(2025, 12, 31),
            date.today().replace(year=date.today().year + 1),  # Next year
        ]

        for test_date in future_dates:
            field = Mock()
            field.data = test_date
            with pytest.raises(ValidationError) as exc_info:
                validator(form, field)
            assert "Date must be today or in the past" in str(exc_info.value)

    def test_empty_field_data(self):
        """Test that empty field data doesn't raise validation error."""
        validator = ValidatePastDate()
        form = Mock()
        field = Mock()
        field.data = None

        # Should not raise ValidationError for None/empty data
        validator(form, field)

    def test_custom_error_message(self):
        """Test custom error message."""
        custom_message = "Custom past date error"
        validator = ValidatePastDate(message=custom_message)
        form = Mock()
        field = Mock()
        field.data = date(2030, 1, 1)  # Future date

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == custom_message


class TestValidateGovDateField:
    def test_non_gov_date_field_skipped(self):
        """Test that non-GovDateField fields are skipped."""
        validator = ValidateGovDateField()
        form = Mock()
        field = Mock()
        field.data = None

        # Should not raise any validation errors for non-GovDateField
        validator(form, field)

    def test_no_raw_data_skipped(self):
        """Test that fields without raw data are skipped."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field

        validator(form, field)

    def test_missing_day_validation(self):
        """Test validation error for missing day."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["", "1", "2025"]
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must include a day"

    def test_missing_month_validation(self):
        """Test validation error for missing month."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["1", "", "2025"]
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must include a month"

    def test_missing_year_validation(self):
        """Test validation error for missing year."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["1", "1", ""]
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must include a year"

    def test_missing_day_and_month_validation(self):
        """Test validation error for missing day and month."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["", "", "2025"]
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must include a day and month"

    def test_missing_day_and_year_validation(self):
        """Test validation error for missing day and year."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["", "1", ""]
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must include a day and year"

    def test_missing_month_and_year_validation(self):
        """Test validation error for missing month and year."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["1", "", ""]
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must include a month and year"

    def test_missing_all_fields_required_validation(self):
        """Test validation error for missing all fields on required field."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["", "", ""]
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must include a day, month and year"

    def test_missing_all_fields_optional_allowed(self):
        """Test that empty optional fields are allowed."""
        from wtforms.validators import Optional

        class TestForm(Form):
            test_field = GovDateField(validators=[Optional()])

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["", "", ""]
        field.data = None

        # Should not raise any validation errors
        validator(form, field)

    def test_invalid_year_length_validation(self):
        """Test validation error for year not having 4 digits."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["1", "1", "25"]  # 2-digit year
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Year must include 4 numbers"

    def test_invalid_year_non_numeric_validation(self):
        """Test validation error for non-numeric year."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["1", "1", "abcd"]  # Non-numeric year
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Year must include 4 numbers"

    def test_invalid_real_date_validation(self):
        """Test validation error for invalid real date."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["32", "13", "2025"]  # Invalid day and month
        field.data = None  # Field couldn't parse the date
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must be a real date"

    def test_valid_date_no_validation_error(self):
        """Test that valid dates don't raise validation errors."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["1", "1", "2025"]
        field.data = date(2025, 1, 1)  # Successfully parsed date
        field.validators = []

        # Should not raise any validation errors
        validator(form, field)

    def test_whitespace_only_fields_treated_as_empty(self):
        """Test that fields with only whitespace are treated as empty."""

        class TestForm(Form):
            test_field = GovDateField()

        validator = ValidateGovDateField()
        form = TestForm()
        field = form.test_field
        field._original_raw_data = ["  ", "\t", "\n"]  # Whitespace only
        field.data = None
        field.validators = []

        with pytest.raises(ValidationError) as exc_info:
            validator(form, field)
        assert str(exc_info.value) == "Date must include a day, month and year"
