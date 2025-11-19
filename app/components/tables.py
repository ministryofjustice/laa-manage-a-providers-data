from collections.abc import Callable
from typing import Any, Literal, TypedDict

from app.utils.formatting import format_uncapitalized

DEFAULT_TABLE_CLASSES = "govuk-table--small-text-until-tablet"
SORTABLE_TABLE_MODULE = "moj-sortable-table"

CellFormat = Literal["numeric"]  # Currently numeric is the only valid cell format option
RowActionTypes = Literal["enter", "add", "change"]  # Actions are 'enter' if value is missing, 'add' or 'change'


class TableStructureItem(TypedDict, total=False):
    """
    Defines how a range of cells are labelled and rendered, with the range being a column (in a regular
    table) or a row (in a transposed table) of values with the same label.
    """

    text: str  # Display text of the header
    format: CellFormat | None  # Format of the table cell, "numeric" wil right align the cell
    classes: str | None  # CSS classes to add to the table column, as comma separated class names.

    id: str | None  # ID of the data to be displayed in the table i.e. firmId
    format_text: Callable[[str], str] | None  # Function used to the format the data i.e. lambda x: x.title()

    # The two below attributes are exclusive and override the id and format text logic, if present.
    # They allow you to render a cell based on the full row data rather than just a single attribute.
    # You can pass in strings directly to override text/ HTML generation logic.
    text_renderer: (
        Callable[[dict[str, str]], str] | str | None
    )  # Function that takes row data, returns text for display.
    html_renderer: Callable[[dict[str, str]], str] | str | None  # Function that takes row data, returns HTML string


class SummaryTableStructureItem(TableStructureItem):
    """
    Adds row action support as optional URLs for each supported action.
    """

    row_action_urls: dict[RowActionTypes, str] | None  # Optional URLs used if the cell needs corresponding row actions
    row_action_texts: (
        dict[RowActionTypes, str] | None
    )  # Optional labels to override the generated '{Action} {field name}'


class Card(TypedDict, total=False):
    """Card used for rendering a header area to a GOV.UK summary list. Only supported by TransposedDataTables"""

    title: str
    action_text: str | None
    action_url: str | None
    action_visually_hidden_text: str | None
    classes: str | None


class Cell(TypedDict, total=False):
    """Represents a single table cell in the rendered output."""

    text: str
    html: str | None  # HTML takes precedence over text if present
    format: str | None
    classes: str | None
    attributes: dict[str, str] | None


Row = list[Cell]
RowData = dict[str, str]  # Key value pairs of data e.g. {"sortCode": "01-02-03"}.
Data = list[RowData]


class DataTable:
    first_cell_is_header = False
    sortable_table = True  # Adds the moj-sortable-table data module

    def __init__(self, structure: list[TableStructureItem], data: Data | RowData) -> None:
        """
        Helper class for generating the head and rows required for displaying GOV.UK Tables.
        Tables usually represent many objects with shared attributes, whereas transposed tables
        usually represent a single object with many attributes.

        Args:
            structure: List of `TableStructure` used by the table to label and render the columns (regular table) or
            rows (transposed table) of values.
            data: The values for the cells, each dict given representing a 'row' (regular table) or 'column'
             (transposed table), and having a key which matches the `id` property in the associated TableStructure item.
        """
        self._validate_structure(structure)

        if isinstance(data, dict):
            data = [data]

        self._validate_data(data)

        self.structure = structure
        self.data = data

    @staticmethod
    def _validate_structure(structure: list[TableStructureItem]) -> None:
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
    def _get_cell(header: TableStructureItem, row_data: RowData) -> Cell:
        header_id = header.get("id", "")
        if header_id in row_data:
            text = str(row_data[header_id])
        else:
            text = ""

        if format_func := header.get("format_text"):
            text = format_func(text)

        if text_renderer := header.get("text_renderer"):
            # If we need to call a function to generate the text do so, otherwise just render the provided text
            if isinstance(text_renderer, Callable):
                text = text_renderer(row_data)
            else:
                text = text_renderer

        cell = {"text": text}

        if html_renderer := header.get("html_renderer"):
            # If we need to call a function to generate the HTML do so, otherwise just render the provided HTML
            if isinstance(html_renderer, Callable):
                cell["html"] = html_renderer(row_data)
            else:
                cell["html"] = html_renderer

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


class SummaryList(DataTable):
    """
    Renders the headings down the side, rather than along the top, and is intended to be
    started in an empty state and populated using the `add_row` method.

    Transposed data tables can also have a 'Card' along the top to summarise information.
    """

    first_cell_is_header = True  # The first cell in each row will be a bold table header

    def __init__(
        self,
        structure: list[SummaryTableStructureItem] | None = None,
        data: Data | RowData | None = None,
        headings: list[str] | None = None,
        card: Card | None = None,
        additional_classes: str = None,
    ) -> None:
        """
        Helper class for generating the head and rows required for displaying transposed GOV.UK Tables.
        """
        super().__init__(structure if structure else [], data if data else [])
        self.card = card
        self.additional_classes = additional_classes

        if headings is not None:
            expected_heading_count = len(self.data) + 1
            if len(headings) != expected_heading_count:
                raise ValueError(
                    f"Headings length ({len(headings)}) must match data length + 1 ({expected_heading_count})"
                )

        self.headings = headings or []

    @staticmethod
    def _validate_structure(structure: list[SummaryTableStructureItem]) -> None:
        """Override DataTable method to allow empty table structure."""
        if not isinstance(structure, list):
            raise ValueError(f"Table structure must be a list, got {type(structure).__name__}")

        for i, column in enumerate(structure):
            if not isinstance(column, dict):
                raise ValueError(f"Table structure item {i} must be a dict, got {type(column).__name__}")

    def add_row(
        self,
        label,
        value=None,
        formatter=None,
        html=None,
        row_action_urls: dict[RowActionTypes, str] | None = None,
        default_value: str = "No data",
        row_action_texts: dict[RowActionTypes, str] | None = None,
    ):
        """
        Helper to add a single field to this table, optionally specifying which row actions should
        be added by including appropriately keyed URLs.

        Uses the label converted to snake_case as the `id` linking the TableStructure item and the data value.

        If `row_action_urls` are specified, the corresponding action link will be included if appropriate.
        The `enter` row action generates an HTML link where the value would normally go, but only when there is no
        value and the `enter` URL is given, otherwise the `default_value` will be presented.
        See `TransposedDataTable.get_rows` for more information.

        Args:
            label: String presentation label, also used as ID after conversion to snake_case
            value: Optional String value to appear in a cell
            formatter: Optional Callable, used to convert `value` into the presented string in the cell
            html: Optional Callable, used during table generation to provide the HTML for the cell
            row_action_urls: Optional dict, using `RowActionTypes` as key and a URL as value.
            default_value: Optional string used when there is no value and no `enter` URL in `row_action_urls`
            row_action_labels: Optional dict, using `RowActionTypes` as key and string link or button text as value
        """
        if row_action_urls is None:
            row_action_urls = {}
        if row_action_texts is None:
            row_action_texts = {}

        # Convert label to snake_case for the ID
        field_id = label.lower().replace(" ", "_")

        empty_value_has_row_action = not value and not html and row_action_urls.get("enter", None) is not None

        structure_item = {"text": label, "id": field_id, "classes": "govuk-!-width-one-half"}
        if empty_value_has_row_action:
            # If we do not have a value but do have a link to enter a new value, show the HTML change link
            # where the value would normally go.
            action_text = row_action_texts.get("enter", f"Enter {format_uncapitalized(label)}")
            structure_item.update(
                {"html_renderer": f"<a class='govuk-link', href='{row_action_urls.get('enter')}'>{action_text}</a>"}
            )
            # Note we are not adding any other row actions even if provided.
        else:
            # Format the displayed value if we have a formatter and a value to format...
            value = formatter(value) if formatter and value else value
            # ...but use the unformatted default_value if there was no value.
            value = value if value else default_value

            if html:
                structure_item.update({"html_renderer": html})
            if row_action_urls:
                structure_item.update({"row_action_urls": row_action_urls})
            if row_action_texts:
                structure_item.update({"row_action_texts": row_action_texts})

        self.structure.append(structure_item)
        if len(self.data) == 0:
            self.data.append({})
        self.data[-1][field_id] = value

        self._validate_data(self.data)
        self._validate_structure(self.structure)

    def get_rows(self) -> list[Row]:
        """Generate transposed table rows.

        Each row corresponds to a field from the structure, with the first cell being the field name and subsequent
        cells containing the field values for each data record.

        If `add` or `change` entries are in `row_action_urls` extra cells are added for the corresponding row actions.
        The `enter` entry should be used in place of the cell value if there is no value: This is managed automatically
         if adding data via `TransposedDataTable.add_row`

        Returns:
            List of Lists (one per row), each inner list containing Cells
        """
        rows = []
        for structure_item in self.structure:
            # First cell is the field name/header
            row_cells = [{"text": structure_item.get("text", ""), "classes": structure_item.get("classes", "")}]

            # Add data cells for each record
            for row_data in self.data:
                cell = self._get_cell(header=structure_item, row_data=row_data)
                row_cells.append(cell)

                # Row Actions
                # 'Enter' actions are rendered where the value would be, so here we are only looking
                # for 'Add' or 'Change' row actions
                row_action_add_url = structure_item.get("row_action_urls", {}).get("add", None)
                row_action_add_text = structure_item.get("row_action_texts", {}).get("add", "Add")
                row_action_change_url = structure_item.get("row_action_urls", {}).get("change", None)
                row_action_change_text = structure_item.get("row_action_texts", {}).get("change", "Change")
                label = format_uncapitalized(structure_item.get("text", ""))

                for action, url in [
                    (row_action_add_text, row_action_add_url),
                    (row_action_change_text, row_action_change_url),
                ]:
                    if url is None:
                        continue
                    action_cell = {"text": action, "href": url, "visuallyHiddenText": label}
                    row_cells.append(action_cell)

            rows.append(row_cells)

        return rows

    @property
    def is_populated(self):
        return len(self.structure) > 0

    def get_headings(self) -> list[dict[str, str]]:
        return [{"text": heading, "classes": ""} for heading in self.headings]

    def to_summary_govuk_params(self, **kwargs) -> dict[str, Any]:
        """Convert transposed table to govukSummaryList dictionary for template rendering.
        Usage: {{ govukSummaryList(table.to_summary_govuk_params()) }}

        """
        table_rows = self.get_rows()
        summary_rows = []

        for row in table_rows:
            if len(row) >= 2:  # Should have at least key and one value, and sometimes row action cells
                summary_rows.append({"key": row[0], "value": row[1]})
            # If we have more than the key and value, the rest are row actions (add | change)
            if len(row) > 2:
                summary_rows[-1]["actions"] = {"items": row[2:]}

        params = {
            "rows": summary_rows,
            "classes": DEFAULT_TABLE_CLASSES + (f" {self.additional_classes}" if self.additional_classes else ""),
        }

        if self.card:
            card = {"title": {"text": self.card.get("title")}}
            if self.card.get("action_text"):
                card.update(
                    {
                        "classes": self.card.get("classes"),
                        "actions": {
                            "items": [
                                {
                                    "text": self.card["action_text"],
                                    "href": self.card["action_url"],
                                    "visuallyHiddenText": self.card.get("action_visually_hidden_text"),
                                }
                            ]
                        },
                    }
                )
            params["card"] = card

        params.update(kwargs)
        return params


class RadioDataTable(DataTable):
    """Extended DataTable that adds radio button functionality."""

    first_cell_is_header = False
    sortable_table = False  # Disable sorting when using radio buttons

    def __init__(
        self, structure: list[TableStructureItem], data: Data | RowData, radio_field_name: str, radio_value_key: str
    ) -> None:
        """
        Initialize RadioDataTable.

        Args:
            structure: Table structure definition
            data: Table data
            radio_field_name: Name attribute for radio buttons
            radio_value_key: Key in row data to use as radio button value
        """
        super().__init__(structure, data)
        self.radio_field_name = radio_field_name
        self.radio_value_key = radio_value_key

    def get_rows(self, selected_value: str = None) -> list[Row]:
        """Generate table rows with radio buttons in first column."""
        rows = []

        for row_data in self.data:
            # Get the base row from parent class
            base_row = super()._get_row(row_data)

            # Create radio button cell
            radio_value = str(row_data.get(self.radio_value_key, ""))
            radio_id = f"{self.radio_field_name}_{radio_value}"

            # Build radio button HTML
            checked_attr = 'checked="checked"' if selected_value and str(selected_value) == radio_value else ""

            radio_html = f'''
            <div class="govuk-radios__item govuk-radios--small">
                <input class="govuk-radios__input" type="radio" name="{self.radio_field_name}" 
                       value="{radio_value}" id="{radio_id}" {checked_attr}>
                <label class="govuk-radios__label govuk-!-padding-0" for="{radio_id}">
                    <span class="govuk-visually-hidden">Select this row</span>
                </label>
            </div>
            '''

            radio_cell = {"html": radio_html.strip(), "text": "", "classes": "govuk-table__cell--radio"}

            # Prepend radio button cell to the row
            rows.append([radio_cell] + base_row)

        return rows

    def get_headings(self) -> list[dict[str, str]]:
        """Get headings with empty first column for radio buttons."""
        base_headings = super().get_headings()
        radio_heading = {"text": "", "classes": "govuk-table__header--radio", "id": ""}
        return [radio_heading] + base_headings

    def to_govuk_params(self, selected_value: str = None, **kwargs) -> dict[str, Any]:
        """Convert table to dictionary for template rendering with radio buttons."""
        params = {
            "head": self.get_headings(),
            "rows": self.get_rows(selected_value),
            "firstCellIsHeader": self.first_cell_is_header,
            "classes": f"{DEFAULT_TABLE_CLASSES} govuk-table--radio",
        }
        params.update(kwargs)
        return params
