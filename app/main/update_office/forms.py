from wtforms.fields.simple import StringField
from wtforms.validators import Optional, InputRequired
from wtforms.fields.choices import RadioField

from app.models import Firm, Office
from app.validators import (
    ValidateVATRegistrationNumber,
)
from app.widgets import GovTextInput, GovRadioInput
from app.constants import PAYMENT_METHOD_CHOICES

from ...forms import BaseForm


class UpdateVATRegistrationNumberForm(BaseForm):
    title = "VAT registration number (optional)"
    template = "update_office/form.html"
    url = "/provider/<firm:firm>/office/<office:office>/add-vat-number"
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


class PaymentMethodForm(BaseForm):
    title = "Payment method"
    url = "provider/<firm:firm>/office/<office:office>/payment-method"
    template = "update_office/payment-method.html"
    submit_button_text = "Save"

    def __init__(self, firm=None, office=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm
        self.office = office

    @property
    def caption(self):
        if not self.firm:
            return "Unknown office"
        return self.firm.firm_name

    payment_method = RadioField(
        "Payment method",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message="Select a payment method")],
        choices=PAYMENT_METHOD_CHOICES,
        default="Electronic",
    )
