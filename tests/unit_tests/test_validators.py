from datetime import date
from unittest.mock import Mock

import pytest
from wtforms import ValidationError

from app.fields import GovDateField
from app.validators import ValidateCompaniesHouseNumber, ValidatePastDate


class TestGovDateField:
    def test_process_date_list_with_full_month_names(self):
        """Test processing full month names to numeric values."""
        test_cases = [
            (["31", "January", "2025"], ["31", "1", "2025"]),
            (["15", "February", "2024"], ["15", "2", "2024"]),
            (["1", "March", "2023"], ["1", "3", "2023"]),
            (["30", "April", "2025"], ["30", "4", "2025"]),
            (["31", "May", "2024"], ["31", "5", "2024"]),
            (["15", "June", "2023"], ["15", "6", "2023"]),
            (["4", "July", "2025"], ["4", "7", "2025"]),
            (["31", "August", "2024"], ["31", "8", "2024"]),
            (["30", "September", "2023"], ["30", "9", "2023"]),
            (["31", "October", "2025"], ["31", "10", "2025"]),
            (["30", "November", "2024"], ["30", "11", "2024"]),
            (["25", "December", "2023"], ["25", "12", "2023"]),
        ]

        field = GovDateField()
        for input_list, expected in test_cases:
            result = field._process_date_list(input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_short_month_names(self):
        """Test processing short month names to numeric values."""
        test_cases = [
            (["31", "Jan", "2025"], ["31", "1", "2025"]),
            (["28", "Feb", "2024"], ["28", "2", "2024"]),
            (["15", "Mar", "2023"], ["15", "3", "2023"]),
            (["1", "Apr", "2025"], ["1", "4", "2025"]),
            (["31", "May", "2024"], ["31", "5", "2024"]),
            (["30", "Jun", "2023"], ["30", "6", "2023"]),
            (["4", "Jul", "2025"], ["4", "7", "2025"]),
            (["15", "Aug", "2024"], ["15", "8", "2024"]),
            (["30", "Sep", "2023"], ["30", "9", "2023"]),
            (["31", "Oct", "2025"], ["31", "10", "2025"]),
            (["15", "Nov", "2024"], ["15", "11", "2024"]),
            (["25", "Dec", "2023"], ["25", "12", "2023"]),
        ]

        field = GovDateField()
        for input_list, expected in test_cases:
            result = field._process_date_list(input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_alternative_short_forms(self):
        """Test processing alternative short forms like 'Sept'."""
        test_cases = [
            (["15", "Sept", "2024"], ["15", "9", "2024"]),
        ]

        field = GovDateField()
        for input_list, expected in test_cases:
            result = field._process_date_list(input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_case_insensitive(self):
        """Test that month processing is case insensitive."""
        test_cases = [
            (["31", "january", "2025"], ["31", "1", "2025"]),
            (["15", "FEBRUARY", "2024"], ["15", "2", "2024"]),
            (["1", "JaN", "2023"], ["1", "1", "2023"]),
            (["30", "dEcEmBeR", "2025"], ["30", "12", "2025"]),
        ]

        field = GovDateField()
        for input_list, expected in test_cases:
            result = field._process_date_list(input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_numeric_months_unchanged(self):
        """Test that numeric months remain unchanged."""
        test_cases = [
            (["31", "1", "2025"], ["31", "1", "2025"]),
            (["15", "12", "2024"], ["15", "12", "2024"]),
            (["1", "6", "2023"], ["1", "6", "2023"]),
        ]

        field = GovDateField()
        for input_list, expected in test_cases:
            result = field._process_date_list(input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_invalid_month_strings(self):
        """Test that invalid month strings remain unchanged."""
        test_cases = [
            (["31", "invalid", "2025"], ["31", "invalid", "2025"]),
            (["15", "notamonth", "2024"], ["15", "notamonth", "2024"]),
            (["1", "", "2023"], ["1", "", "2023"]),
        ]

        field = GovDateField()
        for input_list, expected in test_cases:
            result = field._process_date_list(input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_invalid_input_types(self):
        """Test that invalid input types are handled gracefully."""
        test_cases = [
            (None, None),
            ("not_a_list", "not_a_list"),
            (["only", "two"], ["only", "two"]),  # Less than 3 elements
            (["too", "many", "elements", "here"], ["too", "many", "elements", "here"]),  # More than 3 elements
        ]

        field = GovDateField()
        for input_data, expected in test_cases:
            result = field._process_date_list(input_data)
            assert result == expected, f"Failed for {input_data}, got {result}, expected {expected}"

    def test_process_date_list_with_mixed_types(self):
        """Test processing when month is not a string."""
        test_cases = [
            (["31", 1, "2025"], ["31", 1, "2025"]),  # Integer month
            (["15", None, "2024"], ["15", None, "2024"]),  # None month
        ]

        field = GovDateField()
        for input_list, expected in test_cases:
            result = field._process_date_list(input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"


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
