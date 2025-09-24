from wtforms.fields.choices import RadioField
from wtforms.validators import InputRequired

from app.constants import PAYMENT_METHOD_CHOICES
from app.forms import BaseForm
from app.widgets import GovRadioInput


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
        # Reusable template expects caption to be a string
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
