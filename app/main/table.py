from collections.abc import Callable
from typing import TypedDict


class Column(TypedDict, total=False):
    text: str  # Display text of the header
    id: str | None  # ID of the data to be displayed in the table i.e. firmId
    format_text: Callable[[str], str] | None  # Function used to the format the data i.e. lambda x: x.title()
    format: str | None  # Format of the table cell, "numeric" is the only valid option
    classes: list[str] | None  # Classes to add to the table column.
    html: Callable[[dict[str, str]], str] | None  # Takes row data, returns HTML string


class DataTable:
    """Helper class for generating the head and rows required for displaying GOV.UK Tables."""

    def __init__(self, columns: list[Column], data: list[dict[str, str]]) -> None:
        self.columns = columns
        self.data = data

    def get_rows(self):
        rows = []
        for row_data in self.data:
            row = []
            for column in self.columns:
                text = row_data[column["id"]] if "id" in column and column["id"] in row_data else ""
                if text is None:
                    text = ""

                if column.get("format_text"):
                    text = column["format_text"](text)

                cell = {"text": text}

                if column.get("format"):
                    cell["format"] = column["format"]

                if column.get("classes"):
                    cell["classes"] = column["classes"]

                if column.get("html"):
                    cell["html"] = column["html"](row_data)

                row.append(cell)

            rows.append(row)
        return rows

    def get_headings(self):
        columns = []
        for column in self.columns:
            column = {"id": column.get("id", ""), "text": column.get("text", ""), "classes": column.get("classes", "")}
            columns.append(column)
        return columns
