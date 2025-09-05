from unittest.mock import Mock

import pytest

from app.components.tables import DEFAULT_TABLE_CLASSES, SORTABLE_TABLE_MODULE, DataTable, TransposedDataTable


class TestDataTable:
    def test_init_with_list_data(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}, {"name": "Jane"}]

        table = DataTable(structure, data)

        assert table.structure == structure
        assert table.data == data
        assert table.first_cell_is_header is False
        assert table.sortable_table is True

    def test_init_with_single_dict_data(self):
        structure = [{"text": "Name", "id": "name"}]
        data = {"name": "John"}

        table = DataTable(structure, data)

        assert table.structure == structure
        assert table.data == [{"name": "John"}]

    def test_validate_structure_invalid_type(self):
        with pytest.raises(ValueError, match="Table structure must be a list, got str"):
            DataTable("invalid", [])

    def test_validate_structure_empty(self):
        with pytest.raises(ValueError, match="Table structure cannot be empty"):
            DataTable([], [])

    def test_validate_structure_invalid_item(self):
        with pytest.raises(ValueError, match="Table structure item 0 must be a dict, got str"):
            DataTable(["invalid"], [])

    def test_validate_data_invalid_type(self):
        with pytest.raises(ValueError, match="Data must be a list, got str"):
            DataTable._validate_data("invalid")

    def test_validate_data_invalid_row(self):
        with pytest.raises(ValueError, match="Data row 0 must be a dict.*Row content: invalid"):
            DataTable._validate_data(["invalid"])

    def test_get_cell_basic(self):
        header = {"text": "Name", "id": "name"}
        row_data = {"name": "John"}

        cell = DataTable._get_cell(header, row_data)

        assert cell == {"text": "John"}

    def test_get_cell_missing_id(self):
        header = {"text": "Name", "id": "name"}
        row_data = {"other": "value"}

        cell = DataTable._get_cell(header, row_data)

        assert cell == {"text": ""}

    def test_get_cell_falsy_values(self):
        header = {"text": "Count", "id": "count"}

        test_cases = [({"count": 0}, "0"), ({"count": False}, "False"), ({"count": ""}, ""), ({"count": None}, "None")]

        for row_data, expected in test_cases:
            cell = DataTable._get_cell(header, row_data)
            assert cell["text"] == expected

    def test_get_cell_with_format_text(self):
        header = {"text": "Name", "id": "name", "format_text": lambda x: x.upper()}
        row_data = {"name": "john"}

        cell = DataTable._get_cell(header, row_data)

        assert cell == {"text": "JOHN"}

    def test_get_cell_with_html_function(self):
        html_func = Mock(return_value="<strong>John</strong>")
        header = {"text": "Name", "id": "name", "html_renderer": html_func}
        row_data = {"name": "John"}

        cell = DataTable._get_cell(header, row_data)

        assert cell["text"] == "John"
        assert cell["html"] == "<strong>John</strong>"
        html_func.assert_called_once_with(row_data)

    def test_get_cell_with_format_and_classes(self):
        header = {"text": "Amount", "id": "amount", "format": "numeric", "classes": "text-right bold"}
        row_data = {"amount": "100"}

        cell = DataTable._get_cell(header, row_data)

        assert cell == {"text": "100", "format": "numeric", "classes": "text-right bold"}

    def test_get_cell_with_attributes(self):
        header = {"text": "Name", "id": "name", "attributes": {"data-sort": "name"}}
        row_data = {"name": "John"}

        cell = DataTable._get_cell(header, row_data)

        assert cell == {"text": "John", "attributes": {"data-sort": "name"}}

    def test_get_rows(self):
        structure = [{"text": "Name", "id": "name"}, {"text": "Age", "id": "age", "format": "numeric"}]
        data = [{"name": "John", "age": "30"}, {"name": "Jane", "age": "25"}]

        table = DataTable(structure, data)
        rows = table.get_rows()

        expected = [
            [{"text": "John"}, {"text": "30", "format": "numeric"}],
            [{"text": "Jane"}, {"text": "25", "format": "numeric"}],
        ]
        assert rows == expected

    def test_get_headings(self):
        structure = [
            {"text": "Name", "id": "name", "classes": "name-col"},
            {"text": "Age", "id": "age"},
            {"text": "Email", "id": "email", "format": "text"},  # format should be ignored
        ]

        table = DataTable(structure, [])
        headings = table.get_headings()

        expected = [
            {"id": "name", "text": "Name", "classes": "name-col"},
            {"id": "age", "text": "Age", "classes": ""},
            {"id": "email", "text": "Email", "classes": ""},
        ]
        assert headings == expected

    def test_to_govuk_params_basic(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}]

        table = DataTable(structure, data)
        params = table.to_govuk_params()

        expected_head = [{"id": "name", "text": "Name", "classes": ""}]
        expected_rows = [[{"text": "John"}]]

        assert params["head"] == expected_head
        assert params["rows"] == expected_rows
        assert params["firstCellIsHeader"] is False
        assert params["classes"] == DEFAULT_TABLE_CLASSES
        assert params["attributes"] == {"data-module": SORTABLE_TABLE_MODULE}

    def test_to_govuk_params_not_sortable(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}]

        table = DataTable(structure, data)
        table.sortable_table = False
        params = table.to_govuk_params()

        assert "attributes" not in params

    def test_to_govuk_params_with_overrides(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}]

        table = DataTable(structure, data)
        params = table.to_govuk_params(classes="custom-class", caption="Custom Caption")

        assert params["classes"] == "custom-class"
        assert params["caption"] == "Custom Caption"


class TestTransposedDataTable:
    def test_init_basic(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}]

        table = TransposedDataTable(structure, data)

        assert table.structure == structure
        assert table.data == data
        assert table.first_cell_is_header is True
        assert table.headings == []

    def test_init_with_headings(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}, {"name": "Jane"}]
        headings = ["Field", "Person 1", "Person 2"]

        table = TransposedDataTable(structure, data, headings)

        assert table.headings == headings

    def test_init_headings_wrong_length(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}, {"name": "Jane"}]
        headings = ["Field", "Person 1"]  # Should be 3 items

        with pytest.raises(ValueError, match="Headings length \\(2\\) must match data length \\+ 1 \\(3\\)"):
            TransposedDataTable(structure, data, headings)

    def test_init_with_single_dict_data(self):
        structure = [{"text": "Name", "id": "name"}]
        data = {"name": "John"}
        headings = ["Field", "Value"]

        table = TransposedDataTable(structure, data, headings)

        assert table.data == [{"name": "John"}]
        assert table.headings == headings

    def test_get_rows_transposed(self):
        structure = [{"text": "Name", "id": "name"}, {"text": "Age", "id": "age", "format": "numeric"}]
        data = [{"name": "John", "age": "30"}, {"name": "Jane", "age": "25"}]

        table = TransposedDataTable(structure, data)
        rows = table.get_rows()

        expected = [
            [{"text": "Name", "classes": ""}, {"text": "John"}, {"text": "Jane"}],
            [{"text": "Age", "classes": ""}, {"text": "30", "format": "numeric"}, {"text": "25", "format": "numeric"}],
        ]
        assert rows == expected

    def test_get_rows_with_classes_in_structure(self):
        structure = [{"text": "Name", "id": "name", "classes": "name-header"}]
        data = [{"name": "John"}]

        table = TransposedDataTable(structure, data)
        rows = table.get_rows()

        assert rows[0][0] == {"text": "Name", "classes": "name-header"}

    def test_get_headings_transposed(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}]
        headings = ["Field", "Value"]

        table = TransposedDataTable(structure, data, headings)
        result_headings = table.get_headings()

        expected = [{"text": "Field", "classes": ""}, {"text": "Value", "classes": ""}]
        assert result_headings == expected

    def test_get_headings_empty(self):
        structure = [{"text": "Name", "id": "name"}]
        data = [{"name": "John"}]

        table = TransposedDataTable(structure, data)
        headings = table.get_headings()

        assert headings == []


class TestIntegration:
    def test_complex_table_scenario(self):
        structure = [
            {"text": "Name", "id": "name", "classes": "name-col"},
            {"text": "Age", "id": "age", "format": "numeric"},
            {"text": "Email", "id": "email", "format_text": lambda x: x.lower()},
            {
                "text": "Profile",
                "id": "profile",
                "html": lambda row: f"<a href='/user/{row['name']}'>{row['name']}</a>",
            },
        ]

        data = [
            {"name": "John", "age": "30", "email": "JOHN@EXAMPLE.COM", "profile": "john"},
            {"name": "Jane", "age": "25", "email": "JANE@EXAMPLE.COM", "profile": "jane"},
        ]

        table = DataTable(structure, data)
        params = table.to_govuk_params()

        assert len(params["head"]) == 4
        assert len(params["rows"]) == 2
        assert len(params["rows"][0]) == 4

        assert params["rows"][0][2]["text"] == "john@example.com"  # Email lowercased
        assert params["rows"][0][3]["html_renderer"] == "<a href='/user/John'>John</a>"  # HTML generated
        assert params["rows"][0][1]["format"] == "numeric"  # Numeric format applied

    def test_transposed_with_missing_data(self):
        structure = [{"text": "Name", "id": "name"}, {"text": "Age", "id": "age"}, {"text": "City", "id": "city"}]

        data = [
            {"name": "John", "age": "30"},  # Missing city
            {"name": "Jane", "city": "NYC"},  # Missing age
        ]

        table = TransposedDataTable(structure, data)
        rows = table.get_rows()

        # Check that missing values become empty strings
        assert rows[1][2]["text"] == ""  # John's missing age
        assert rows[2][1]["text"] == ""  # Jane's missing city
