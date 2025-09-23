from wtforms.fields import DateField
from wtforms.fields.choices import RadioField

from app.components.tables import RadioDataTable, TableStructureItem


class GovDateField(DateField):
    """DateField that can parse month strings like 'January' or 'Jan' into numeric format."""

    MONTH_MAP = {
        # Full month names
        "january": "1",
        "february": "2",
        "march": "3",
        "april": "4",
        "may": "5",
        "june": "6",
        "july": "7",
        "august": "8",
        "september": "9",
        "october": "10",
        "november": "11",
        "december": "12",
        # Short month names
        "jan": "1",
        "feb": "2",
        "mar": "3",
        "apr": "4",
        "jun": "6",
        "jul": "7",
        "aug": "8",
        "sep": "9",
        "oct": "10",
        "nov": "11",
        "dec": "12",
        # Alternative short forms
        "sept": "9",
    }

    def _process_date_list(self, date_list):
        """Convert month strings to numbers in a date list [day, month, year]."""
        if not isinstance(date_list, list) or len(date_list) != 3:
            return date_list

        day, month, year = date_list

        # Try to convert month string to number
        if isinstance(month, str) and month.lower() in self.MONTH_MAP:
            month = self.MONTH_MAP[month.lower()]

        return [day, month, year]

    def process_formdata(self, valuelist):
        if valuelist:
            # Store the original raw data for validation later
            self._original_raw_data = valuelist

            # Convert month strings to numbers before processing
            processed_valuelist = self._process_date_list(valuelist)

            try:
                if len(processed_valuelist) == 3:
                    day, month, year = processed_valuelist
                    if day and month and year:
                        from datetime import datetime

                        self.data = datetime.strptime(f"{day} {month} {year}", "%d %m %Y").date()
                    else:
                        self.data = None
                else:
                    self.data = None
            except (ValueError, TypeError):
                self.data = None
        else:
            self._original_raw_data = valuelist
            self.data = None


class GovUKTableRadioField(RadioField):
    """RadioField that generates a GOV.UK table with radio buttons as the first table column."""

    def __init__(
        self,
        label: str = None,
        validators: list = None,
        structure: list[TableStructureItem] = None,
        radio_value_key: str = "id",
        **kwargs,
    ):
        """
        Initialize the field.

        Args:
            label: str - Field label (will be rendered as page heading in template)
            validators: list - Field validators
            structure: list - Table structure
            radio_value_key: Key to use for radio button values
            **kwargs: Additional field arguments
        """
        super().__init__(label, validators, **kwargs)

        if structure is None:
            raise ValueError("structure parameter is required")

        self.structure = structure
        self.radio_value_key = radio_value_key
        self.type = "GovUKTableRadioField"

    def get_table_params(self, **kwargs):
        """Generate GOV.UK table params for template rendering

        Usage in template: {{ govukTable(field.get_table_params()) }}

        Args:
            **kwargs: Additional parameters to pass to the table

        Returns:
            dict: GOV.UK table parameters
        """
        # Convert field choices to DataTable format
        data = []
        for choice_value, choice_data in self.choices:
            if isinstance(choice_data, dict):
                # If choice_data is already a dict, use it directly
                row_data = choice_data.copy()
                row_data[self.radio_value_key] = choice_value
            elif isinstance(choice_data, (list, tuple)):
                # Convert list/tuple to dict using structure IDs
                row_data = {self.radio_value_key: choice_value}
                for i, value in enumerate(choice_data):
                    if i < len(self.structure):
                        structure_id = self.structure[i].get("id", f"col_{i}")
                        row_data[structure_id] = str(value)
            else:
                row_data = {self.radio_value_key: choice_value, "label": str(choice_data)}
            data.append(row_data)

        table = RadioDataTable(
            structure=self.structure, data=data, radio_field_name=self.name, radio_value_key=self.radio_value_key
        )

        return table.to_govuk_params(selected_value=self.data, **kwargs)
