from collections.abc import Callable
from typing import Any, TypedDict

DEFAULT_TABLE_CLASSES = "govuk-table--small-text-until-tablet"
SORTABLE_TABLE_MODULE = "moj-sortable-table"


class TableStructure(TypedDict, total=False):
    text: str  # Display text of the header
    id: str | None  # ID of the data to be displayed in the table i.e. firmId
    format_text: Callable[[str], str] | None  # Function used to the format the data i.e. lambda x: x.title()
    format: str | None  # Format of the table cell, "numeric" is the only valid option
    classes: str | None  # CSS classes to add to the table column, as comma separated class names.
    html: Callable[[dict[str, str]], str] | None  # Function that takes row data, returns HTML string


class Cell(TypedDict, total=False):
    """Represents a single table cell in the rendered output."""

    text: str  # The display text for the cell
    html: str | None  # HTML content (takes precedence over text)
    format: str | None  # Cell format, currently only supports "numeric"
    classes: str | None  # CSS classes to add to the table column, as comma separated class names.
    attributes: dict[str, str] | None  # Additional HTML attributes


Row = list[Cell]
RowData = dict[str, str]
Data = list[RowData]


class DataTable:
    first_cell_is_header = False
    sortable_table = True  # Adds the moj-sortable-table data module

    def __init__(self, structure: list[TableStructure], data: Data | RowData) -> None:
        """Helper class for generating the head and rows required for displaying GOV.UK Tables."""
        self._validate_structure(structure)

        if isinstance(data, dict):
            data = [data]

        self._validate_data(data)

        self.structure = structure
        self.data = data

    @staticmethod
    def _validate_structure(structure: list[TableStructure]) -> None:
        if not isinstance(structure, list):
            raise ValueError(f"Table structure must be a list, got {type(structure).__name__}")

        if not structure:
            raise ValueError("Table structure cannot be empty")

        for i, column in enumerate(structure):
            if not isinstance(column, dict):
                raise ValueError(f"Table structure item {i} must be a dict, got {type(column).__name__}")

    @staticmethod
    def _validate_data(data: Data) -> None:
        if not isinstance(data, list):
            raise ValueError(f"Data must be a list, got {type(data).__name__}")

        for i, row in enumerate(data):
            if not isinstance(row, dict):
                raise ValueError(f"Data row {i} must be a dict, got {type(row).__name__}. Row content: {row}")

    @staticmethod
    def _get_cell(header: TableStructure, row_data: RowData) -> Cell:
        header_id = header.get("id", "")
        if header_id in row_data:
            text = str(row_data[header_id])
        else:
            text = ""

        if format_func := header.get("format_text"):
            text = format_func(text)

        cell = {"text": text}

        if html_func := header.get("html"):
            cell["html"] = html_func(row_data)

        for key in ("format", "classes", "attributes"):
            if value := header.get(key):
                cell[key] = value

        return cell

    def _get_row(self, row_data: RowData) -> Row:
        return [self._get_cell(header=header, row_data=row_data) for header in self.structure]

    def get_rows(self) -> list[Row]:
        return [self._get_row(row_data) for row_data in self.data]

    def get_headings(self) -> list[dict[str, str]]:
        return [{key: column.get(key, "") for key in ("id", "text", "classes")} for column in self.structure]

    def to_govuk_params(self, **kwargs) -> dict[str, Any]:
        """Convert table to dictionary for template rendering.
        Usage: {{ govukTable(table.to_govuk_params()) }}
        With overrides: {{ govukTable(table.to_govuk_params(classes="custom-class")) }}
        """
        params = {
            "head": self.get_headings(),
            "rows": self.get_rows(),
            "firstCellIsHeader": self.first_cell_is_header,
            "classes": DEFAULT_TABLE_CLASSES,
        }
        if self.sortable_table:
            params.update({"attributes": {"data-module": SORTABLE_TABLE_MODULE}})
        params.update(kwargs)  # Allow overriding any defaults
        return params


class TransposedDataTable(DataTable):
    first_cell_is_header = True  # The first cell in each row will be a bold table header

    def __init__(
        self, structure: list[TableStructure], data: Data | RowData, headings: list[str] | None = None
    ) -> None:
        """Helper class for generating the head and rows required for displaying transposed GOV.UK Tables."""
        super().__init__(structure, data)

        if headings is not None:
            expected_heading_count = len(data) + 1
            if len(headings) != expected_heading_count:
                raise ValueError(
                    f"Headings length ({len(headings)}) must match data length + 1 ({expected_heading_count})"
                )

        self.headings = headings or []

    def get_rows(self) -> list[Row]:
        """Generate transposed table rows.

        Each row corresponds to a field from the structure, with the first cell being
        the field name and subsequent cells containing the field values for each data record.
        """
        rows = []
        for structure_item in self.structure:
            # First cell is the field name/header
            row_cells = [{"text": structure_item.get("text", ""), "classes": structure_item.get("classes", "")}]

            # Add data cells for each record
            for row_data in self.data:
                cell = self._get_cell(header=structure_item, row_data=row_data)
                row_cells.append(cell)

            rows.append(row_cells)

        return rows

    def get_headings(self) -> list[dict[str, str]]:
        return [{"text": heading, "classes": ""} for heading in self.headings]
