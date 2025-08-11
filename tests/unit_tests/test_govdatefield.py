from unittest.mock import Mock

import pytest
from wtforms.validators import StopValidation

from app.fields import GovDateField


class TestGovDateFieldProcessing:
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

        field_class = GovDateField
        for input_list, expected in test_cases:
            result = field_class._process_date_list(field_class, input_list)
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

        field_class = GovDateField
        for input_list, expected in test_cases:
            result = field_class._process_date_list(field_class, input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_alternative_short_forms(self):
        """Test processing alternative short forms like 'Sept'."""
        test_cases = [
            (["15", "Sept", "2024"], ["15", "9", "2024"]),
        ]

        field_class = GovDateField
        for input_list, expected in test_cases:
            result = field_class._process_date_list(field_class, input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_case_insensitive(self):
        """Test that month processing is case insensitive."""
        test_cases = [
            (["31", "january", "2025"], ["31", "1", "2025"]),
            (["15", "FEBRUARY", "2024"], ["15", "2", "2024"]),
            (["1", "JaN", "2023"], ["1", "1", "2023"]),
            (["30", "dEcEmBeR", "2025"], ["30", "12", "2025"]),
        ]

        field_class = GovDateField
        for input_list, expected in test_cases:
            result = field_class._process_date_list(field_class, input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_numeric_months_unchanged(self):
        """Test that numeric months remain unchanged."""
        test_cases = [
            (["31", "1", "2025"], ["31", "1", "2025"]),
            (["15", "12", "2024"], ["15", "12", "2024"]),
            (["1", "6", "2023"], ["1", "6", "2023"]),
        ]

        field_class = GovDateField
        for input_list, expected in test_cases:
            result = field_class._process_date_list(field_class, input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_invalid_month_strings(self):
        """Test that invalid month strings remain unchanged."""
        test_cases = [
            (["31", "invalid", "2025"], ["31", "invalid", "2025"]),
            (["15", "notamonth", "2024"], ["15", "notamonth", "2024"]),
            (["1", "", "2023"], ["1", "", "2023"]),
        ]

        field_class = GovDateField
        for input_list, expected in test_cases:
            result = field_class._process_date_list(field_class, input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"

    def test_process_date_list_with_invalid_input_types(self):
        """Test that invalid input types are handled gracefully."""
        test_cases = [
            (None, None),
            ("not_a_list", "not_a_list"),
            (["only", "two"], ["only", "two"]),  # Less than 3 elements
            (["too", "many", "elements", "here"], ["too", "many", "elements", "here"]),  # More than 3 elements
        ]

        field_class = GovDateField
        for input_data, expected in test_cases:
            result = field_class._process_date_list(field_class, input_data)
            assert result == expected, f"Failed for {input_data}, got {result}, expected {expected}"

    def test_process_date_list_with_mixed_types(self):
        """Test processing when month is not a string."""
        test_cases = [
            (["31", 1, "2025"], ["31", 1, "2025"]),  # Integer month
            (["15", None, "2024"], ["15", None, "2024"]),  # None month
        ]

        field_class = GovDateField
        for input_list, expected in test_cases:
            result = field_class._process_date_list(field_class, input_list)
            assert result == expected, f"Failed for {input_list}, got {result}, expected {expected}"


class TestGovDateFieldValidation:
    """Test the GovDateField's validation functionality."""

    def test_validate_incomplete_date_missing_day(self):
        """Test validation when only day is missing."""
        valuelist = ["", "12", "2025"]

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Date must include a day"

    def test_validate_incomplete_date_missing_month(self):
        """Test validation when only month is missing."""
        valuelist = ["31", "", "2025"]

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Date must include a month"

    def test_validate_incomplete_date_missing_year(self):
        """Test validation when only year is missing."""
        valuelist = ["31", "12", ""]

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Date must include a year"

    def test_validate_incomplete_date_missing_day_and_month(self):
        """Test validation when day and month are missing."""
        valuelist = ["", "", "2025"]

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Date must include a day and month"

    def test_validate_incomplete_date_missing_day_and_year(self):
        """Test validation when day and year are missing."""
        valuelist = ["", "12", ""]

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Date must include a day and year"

    def test_validate_incomplete_date_missing_month_and_year(self):
        """Test validation when month and year are missing."""
        valuelist = ["31", "", ""]

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Date must include a month and year"

    def test_validate_incomplete_date_missing_all_fields(self):
        """Test validation when all fields are missing."""
        valuelist = ["", "", ""]

        # Create a mock field without Optional validator (required field)
        mock_field = Mock()
        mock_field.validators = []

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(mock_field, valuelist)
        assert str(exc_info.value) == "Date must include a day, month and year"

    def test_validate_incomplete_date_whitespace_only_fields(self):
        """Test validation with whitespace-only fields."""
        valuelist = ["  ", "   ", "    "]

        # Create a mock field without Optional validator (required field)
        mock_field = Mock()
        mock_field.validators = []

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(mock_field, valuelist)
        assert str(exc_info.value) == "Date must include a day, month and year"

    def test_validate_incomplete_date_invalid_year_format(self):
        """Test validation with invalid year format."""
        # Test 2-digit year
        valuelist = ["31", "12", "25"]
        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Year must include 4 numbers"

        # Test non-numeric year
        valuelist = ["31", "12", "abcd"]
        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Year must include 4 numbers"

    def test_validate_incomplete_date_single_value_raw_data(self):
        """Test validation with non-list raw_data."""
        valuelist = ["31/12/2025"]  # Single string instead of list - will be padded

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Date must include a month and year"

    def test_validate_incomplete_date_short_raw_data_list(self):
        """Test validation with incomplete raw_data list."""
        valuelist = ["31"]  # Only one element - will be padded

        with pytest.raises(StopValidation) as exc_info:
            GovDateField._validate_incomplete_date(None, valuelist)
        assert str(exc_info.value) == "Date must include a month and year"

    def test_validate_incomplete_date_valid_complete_date(self):
        """Test that complete valid date passes validation."""
        valuelist = ["31", "12", "2025"]

        # Should not raise any exception
        GovDateField._validate_incomplete_date(None, valuelist)

    def test_validate_incomplete_date_optional_field_empty(self):
        """Test that optional field with empty data passes validation."""
        from wtforms.validators import Optional

        valuelist = ["", "", ""]

        # Create a mock field with Optional validator
        mock_field = Mock()
        mock_field.validators = [Optional()]

        # Should not raise any exception for optional empty field
        GovDateField._validate_incomplete_date(mock_field, valuelist)
