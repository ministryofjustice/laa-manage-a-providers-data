from typing import List

from flask import current_app
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Optional

from app.constants import OFFICE_ACTIVE_STATUS_CHOICES, PAYMENT_METHOD_CHOICES, YES_NO_CHOICES
from app.forms import BaseForm, NoChangesMixin
from app.main.add_a_new_office.forms import OfficeContactDetailsForm
from app.main.add_a_new_provider import AssignContractManagerForm
from app.main.forms import BaseBankAccountForm, BaseBankAccountSearchForm
from app.models import BankAccount, Firm, Office
from app.validators import (
    ValidateVATRegistrationNumber, ValidateGovDateField, ValidatePastDate, ValidateIf,
)
from app.widgets import GovRadioInput, GovTextInput, GovDateInput
from ...fields import GovDateField, GovUKRadioField


class UpdateOfficeBaseForm(BaseForm):
    template = "update_office/form.html"

    def __init__(self, firm: Firm, office: Office, *args, **kwargs):
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
    url = [
        "/provider/<firm:firm>/office/<office:office>/change-vat-registration",
        "/provider/<firm:firm>/change-vat-registration",
    ]

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


class BankAccountSearchForm(BaseBankAccountSearchForm, UpdateOfficeBaseForm):
    title = "Search for bank account"
    url = [
        "/provider/<firm:firm>/office/<office:office>/search-bank-account",
        "/provider/<firm:firm>/search-bank-account",
    ]
    template = "update_office/search-bank-account.html"
    submit_button_text = "Continue"

    def get_bank_accounts(self, *args, **kwargs) -> List[BankAccount]:
        """
        Get list of bank accounts belonging to the given firm id

        Args:
        firm_id: The firm ID

        Returns:
            List[BankAccount]: List of bank accounts that belong to firm_id

        Raises:
            NoBankAccountsError: When the given firm does not have any bank accounts
        """
        pda = current_app.extensions["pda"]
        if self.firm.is_advocate or self.firm.is_barrister:
            return pda.get_all_bank_accounts()

        return pda.get_provider_firm_bank_details(self.firm.firm_id)


class ChangeOfficeContactDetailsForm(OfficeContactDetailsForm):
    url = "provider/<firm:firm>/office/<office:office>/change-office-contact-details"
    template = "update_office/form.html"

    def __init__(self, firm: Firm, office: Office, *args, **kwargs):
        self.office = office
        super(ChangeOfficeContactDetailsForm, self).__init__(firm, *args, **kwargs)

    @property
    def caption(self):
        return self.firm.firm_name


class BankAccountForm(BaseBankAccountForm):
    title = "Add a bank account"
    url = [
        "provider/<firm:firm>/office/<office:office>/add-bank-account",
        "provider/<firm:firm>/add-bank-account",
    ]
    submit_button_text = "Submit"
    template = "update_office/form.html"

    @property
    def caption(self):
        return self.firm.firm_name

    def __init__(self, firm: Firm, office: Office, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm
        self.office = office


class ChangeOfficeContractManagerForm(AssignContractManagerForm):
    url = "provider/<firm:firm>/office/<office:office>/change-contract-manager"
    office: Office | None = None

    def __init__(self, firm: Firm, office: Office | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm
        self.office = office


class ChangeOfficeFalseBalanceForm(NoChangesMixin, UpdateOfficeBaseForm):
    url = "provider/<firm:firm>/office/<office:office>/change-false-balance"
    title = "Does this office have a false balance?"
    submit_button_text = "Submit"
    no_changes_error_message = "You have not changed the false balance status. Cancel if you do not want to change it."

    @property
    def caption(self):
        return self.firm.firm_name

    status = RadioField(
        label="",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        choices=YES_NO_CHOICES,
        validators=[InputRequired("Please select a valid choice.")],
        default="No",
    )


class ChangeOfficeIntervenedForm(NoChangesMixin, UpdateOfficeBaseForm):
    template = "update_office/intervened-form.html"
    url = "provider/<firm:firm>/office/<office:office>/intervention-status"
    title = "Has this office been intervened?"
    submit_button_text = "Submit"
    yes_no_changes_error_message = "Select no if this provider has not been intervened. Cancel if you do not want to change the answer."
    no_no_changes_error_message = "Select yes if this provider has been intervened. Cancel if you do not want to change the answer."

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.status.data == "Yes":
            self.no_changes_error_message = self.yes_no_changes_error_message
        else:
            self.no_changes_error_message = self.no_no_changes_error_message

    @property
    def caption(self):
        return self.firm.firm_name

    status = RadioField(
        label="",
        widget=GovRadioInput(heading_class="govuk-fieldset__legend--m"),
        choices=YES_NO_CHOICES,
        validators=[InputRequired("Please select a valid choice.")],
        default="No",
    )

    intervened_date = GovDateField(
        "Date intervened",
        widget=GovDateInput(heading_class="govuk-fieldset__legend--m", hint="For example 27 3 2025"),
        format="%d %m %Y",
        validators=[
            ValidateIf("status", "Yes"),
            ValidateGovDateField(),
            ValidatePastDate()
        ],
    )
