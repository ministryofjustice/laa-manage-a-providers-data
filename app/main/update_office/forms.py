from wtforms.fields.simple import StringField
from wtforms.validators import Optional

from app.models import Firm, Office
from app.validators import (
    ValidateVATRegistrationNumber,
)
from app.widgets import GovTextInput

from ...forms import BaseForm


class UpdateVATRegistrationNumberForm(BaseForm):
    title = "VAT registration number (optional)"
    template = None
    url = None
    firm: Firm
    office: Office

    def __init__(self, firm: Firm, office: Office, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm
        self.office = office

    @property
    def caption(self):
        return self.firm.firm_name

    vat_registration_number = StringField(
        "",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--xl",
            classes="govuk-!-width-one-half",
            hint="This is 9 numbers, sometimes with ‘GB’ at the start, for example 123456789 or GB123456789.",
        ),
        validators=[
            Optional(),
            ValidateVATRegistrationNumber(message="Enter the VAT registration number in the correct format"),
        ],
    )
