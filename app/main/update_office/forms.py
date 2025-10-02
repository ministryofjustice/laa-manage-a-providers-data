from wtforms.fields.choices import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Optional

from app.constants import OFFICE_ACTIVE_STATUS_CHOICES, PAYMENT_METHOD_CHOICES
from app.validators import (
    ValidateVATRegistrationNumber,
)
from app.widgets import GovRadioInput, GovTextInput

from ...forms import BaseForm


class UpdateOfficeBaseForm(BaseForm):
    template = "update_office/form.html"

    def __init__(self, firm=None, office=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm
        self.office = office

    @property
    def caption(self):
        if not self.firm:
            return "Unknown office"
        return self.firm.firm_name


class UpdateVATRegistrationNumberForm(UpdateOfficeBaseForm):
    title = "VAT registration number (optional)"
    url = "/provider/<firm:firm>/office/<office:office>/add-vat-number"

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


class PaymentMethodForm(UpdateOfficeBaseForm):
    title = "Payment method"
    url = "provider/<firm:firm>/office/<office:office>/payment-method"
    template = "update_office/payment-method.html"
    submit_button_text = "Save"

    payment_method = RadioField(
        "Payment method",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        validators=[InputRequired(message="Select a payment method")],
        choices=PAYMENT_METHOD_CHOICES,
        default="Electronic",
    )


class ChangeOfficeActiveStatusForm(UpdateOfficeBaseForm):
    title = "Change active status"
    url = "provider/<firm:firm>/office/<office:office>/confirm-office-status"
    submit_button_text = "Submit"

    active_status = RadioField(
        "",
        widget=GovRadioInput(
            heading_class="govuk-fieldset__legend--m",
        ),
        choices=OFFICE_ACTIVE_STATUS_CHOICES,
    )
