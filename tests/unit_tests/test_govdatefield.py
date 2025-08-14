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
