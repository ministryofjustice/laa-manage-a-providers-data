from flask import session
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import Email, InputRequired, Length, Optional

from app.constants import YES_NO_CHOICES
from app.forms import BaseForm
from app.models import Firm
from app.validators import ValidatePostcode
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
        validators=[
            InputRequired(message="Enter the office name"),
            Length(max=320, message="Office name must be less than 320 characters"),
        ],
    )

    is_head_office = RadioField(
        "Is this the head office?",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m", classes="govuk-radios--inline"),
        validators=[InputRequired(message="Select yes if this is the head office")],
        choices=YES_NO_CHOICES,
    )


class OfficeContactDetailsForm(BaseForm):
    title = "Office contact details"
    url = "provider/<firm:firm>/add-office-contact-details"
    template = "add_office/office-contact-details.html"
    submit_button_text = "Submit"

    firm: Firm | None = None  # Firm this office is being added to

    def __init__(self, firm: Firm, *args, **kwargs):
        self.firm = firm
        super(OfficeContactDetailsForm, self).__init__(*args, **kwargs)

    @property
    def caption(self):
        # Get office name from session if available
        new_office = session.get("new_office", {})
        office_name = new_office.get("office_name", "Office name")
        return office_name

    address_line_1 = StringField(
        "Address line 1",
        widget=GovTextInput(classes="govuk-!-width-three-quarters"),
        validators=[
            InputRequired(message="Enter address line 1, typically the building and street"),
            Length(max=240, message="Address line 1 must be 240 characters or fewer"),
        ],
    )

    address_line_2 = StringField(
        "Address line 2 (optional)",
        widget=GovTextInput(classes="govuk-!-width-three-quarters"),
        validators=[Optional(), Length(max=240, message="Address line 2 must be 240 characters or fewer")],
    )

    address_line_3 = StringField(
        "Address line 3 (optional)",
        widget=GovTextInput(classes="govuk-!-width-three-quarters"),
        validators=[Optional(), Length(max=240, message="Address line 3 must be 240 characters or fewer")],
    )

    address_line_4 = StringField(
        "Address line 4 (optional)",
        widget=GovTextInput(classes="govuk-!-width-three-quarters"),
        validators=[Optional(), Length(max=560, message="Address line 4 must be 560 characters or fewer")],
    )

    city = StringField(
        "Town or city",
        widget=GovTextInput(classes="govuk-!-width-two-thirds"),
        validators=[
            InputRequired(message="Enter the town or city"),
            Length(max=25, message="Town or city must be 25 characters or fewer"),
        ],
    )

    county = StringField(
        "County (optional)",
        widget=GovTextInput(classes="govuk-!-width-two-thirds"),
        validators=[Optional(), Length(max=150, message="County must be 150 characters or fewer")],
    )

    postcode = StringField(
        "Postcode",
        widget=GovTextInput(classes="auto-capitalise govuk-input--width-10"),
        validators=[
            InputRequired(message="Enter the postcode"),
            Length(max=20, message="Postcode must be 20 characters or fewer"),
            ValidatePostcode(),
        ],
    )

    # Contact fields
    telephone_number = StringField(
        "Telephone number (optional)",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m", classes="govuk-input--width-20"),
        validators=[
            Optional(),
            Length(max=20, message="Telephone number must be 20 characters or fewer"),
        ],
    )

    email_address = StringField(
        "Office email address (optional)",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m", classes="govuk-!-width-full"),
        validators=[
            Optional(),
            Email(message="Enter a valid email address"),
            Length(max=100, message="Email address must be 100 characters or fewer"),
        ],
    )

    # DX fields
    dx_number = StringField(
        "DX number (optional)",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m", classes="govuk-input--width-20"),
        validators=[
            Optional(),
            Length(max=20, message="DX number must be 20 characters or fewer"),
        ],
    )

    dx_centre = StringField(
        "DX centre (optional)",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m", classes="govuk-input--width-20"),
        validators=[
            Optional(),
            Length(max=50, message="DX centre must be 50 characters or fewer"),
        ],
    )
