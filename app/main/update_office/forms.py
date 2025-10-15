from typing import List

from flask import current_app
from wtforms.fields.choices import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, InputRequired, Length, Optional

from app.components.tables import RadioDataTable, TableStructureItem
from app.constants import OFFICE_ACTIVE_STATUS_CHOICES, PAYMENT_METHOD_CHOICES
from app.forms import BaseForm
from app.main.forms import BaseBankAccountForm
from app.models import BankAccount, Firm, Office
from app.validators import (
    ValidateVATRegistrationNumber,
)
from app.widgets import GovRadioInput, GovTextInput


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


class NoBankAccountsError(Exception):
    pass


class BankAccountSearchForm(UpdateOfficeBaseForm):
    title = "Search for bank account"
    url = "/provider/<firm:firm>/office/<office:office>/search-bank-account"
    template = "update_office/search-bank-account.html"
    submit_button_text = "Continue"
    ITEMS_PER_PAGE = 10

    search = StringField(
        "Search for a bank account",
        widget=GovTextInput(
            form_group_classes="govuk-!-width-two-thirds",
            heading_class="govuk-fieldset__legend--s",
            hint="You can search by sort code or account number",
        ),
        validators=[Length(max=8, message="Search term must be 8 characters or less")],
    )
    bank_account = StringField(
        validators=[DataRequired(message="Select a bank account or search again")],
    )

    def __init__(self, firm: Firm, office: Office, search_term=None, page=1, selected_value=None, *args, **kwargs):
        super().__init__(firm, office, *args, **kwargs)
        self.page = page

        # Set search field data
        self.search_term = search_term
        if search_term:
            self.search.data = search_term

        # Filter bank accounts based on search term
        bank_accounts = self.get_matched_bank_accounts(firm.firm_id, search_term)
        self.num_results = len(bank_accounts)

        # Limit results and populate choices
        start_id = self.ITEMS_PER_PAGE * (page - 1)
        end_id = self.ITEMS_PER_PAGE * (page - 1) + self.ITEMS_PER_PAGE

        bank_accounts = bank_accounts[start_id:end_id]

        # Create RadioDataTable for contract managers
        table_structure: list[TableStructureItem] = [
            {"text": "Sort code", "id": "sort_code"},
            {"text": "Account number", "id": "account_number"},
            {"text": "Account name", "id": "bank_account_name"},
        ]
        self.bank_accounts_table = RadioDataTable(
            structure=table_structure,
            data=[bank_account.to_internal_dict() for bank_account in bank_accounts],
            radio_field_name="bank_account",
            radio_value_key="bank_account_id",
        )

        # Store selected value for table rendering
        self.selected_value = selected_value

    def get_bank_accounts(self, firm_id: int) -> List[BankAccount]:
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
        bank_accounts = pda.get_provider_firm_bank_details(firm_id)
        if not bank_accounts:
            raise NoBankAccountsError("No bank accounts found")
        return bank_accounts

    def get_matched_bank_accounts(self, firm_id: int, search_term: str) -> List[BankAccount]:
        """
        Get bank accounts matching the search term that belong to a given firm

        Args:
        firm_id: The firm ID of the firm to limit the search to
        search_term: A bank account sort code or account number to search for

        Returns:
            List[BankAccount]: List of bank accounts that belong to the given that match the search term
        """
        bank_accounts = self.get_bank_accounts(firm_id)
        if not search_term:
            # Return all bank accounts when no search term is provided.
            return bank_accounts

        matched_bank_accounts = []
        search_lower = search_term.lower()
        for bank_account in bank_accounts:
            search_fields = [bank_account.account_number, bank_account.sort_code]
            if search_lower in search_fields:
                matched_bank_accounts.append(bank_account)
        return matched_bank_accounts


class BankAccountForm(BaseBankAccountForm):
    title = "Add a bank account"
    url = "provider/<firm:firm>/office/<office:office>/add-bank-account"
    submit_button_text = "Submit"
    template = "update_office/form.html"

    @property
    def caption(self):
        return self.firm.firm_name

    def __init__(self, firm: Firm, office: Office, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm
        self.office = office
