from wtforms.fields.choices import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired

from app.constants import YES_NO_CHOICES
from app.forms import BaseForm
from app.models import Firm
from app.widgets import GovRadioInput, GovTextInput


class AddOfficeForm(BaseForm):
    title = "Add a new office"
    url = "provider/<firm:firm>/add-office"

    firm: Firm | None = None  # Firm this office is being added to

    def __init__(self, firm: Firm, *args, **kwargs):
        self.firm = firm
        super(AddOfficeForm, self).__init__(*args, **kwargs)

    @property
    def caption(self):
        if not self.firm:
            return "Unknown"

        return self.firm.firm_name

    office_name = StringField(
        "Office name",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message="Enter the office name")],
    )

    is_head_office = RadioField(
        "Is this the head office?",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m", classes="govuk-radios--inline"),
        validators=[InputRequired(message="Select yes if this is the head office")],
        choices=YES_NO_CHOICES,
    )
