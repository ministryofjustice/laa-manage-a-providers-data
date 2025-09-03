from wtforms import SelectMultipleField, StringField
from wtforms.validators import DataRequired, InputRequired, Length

from app.forms import BaseForm
from app.widgets import GovTextInput


class AddContractManagerForm(BaseForm):
    title = "Add Contract Manager"
    url = "contract-managers"
    submit_button_text = "Add Manager"

    name = StringField(
        "Contract manager name",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m"),
        validators=[
            InputRequired(message="Enter the manager name"),
            Length(max=100, message="Name must be 100 characters or less"),
        ],
    )


class BulkRemoveContractManagerForm(BaseForm):
    title = "Remove Selected Managers"
    url = "contract-managers"
    submit_button_text = "Remove Selected"

    selected_managers = SelectMultipleField(
        "Selected Managers", validators=[DataRequired(message="Please select at least one manager to remove")]
    )
