from wtforms.fields.choices import RadioField

from app.components.tables import RadioDataTable, TableStructure


class GovUKTableRadioField(RadioField):
    """A RadioField that generates GovUK table params for template rendering."""

    def __init__(
        self,
        label: str = None,
        validators: list = None,
        structure: list[TableStructure] = None,
        radio_value_key: str = "id",
        **kwargs,
    ):
        """
        Initialize the field.

        Args:
            label: str - Field label (will be rendered as page heading in template)
            validators: list - Field validators
            structure: Table structure definition following your TableStructure format
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
        """Generate GovUK table params

        Usage in template: {{ govukTable(field.get_table_params()) }}

        Args:
            **kwargs: Additional parameters to pass to the table

        Returns:
            dict: GovUK table parameters
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
