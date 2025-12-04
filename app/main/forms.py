import logging
from datetime import datetime, timedelta
from typing import Any, List

from flask import current_app, url_for
from wtforms.fields.simple import StringField
from wtforms.validators import DataRequired, InputRequired, Length

from app.components.tables import DataTable, RadioDataTable, TableStructureItem
from app.forms import BaseForm
from app.main.utils import get_firm_account_number, get_firm_tags
from app.models import BankAccount, Firm
from app.utils.formatting import format_sentence_case, normalize_for_search
from app.validators import ValidateAccountNumber, ValidateSortCode
from app.widgets import GovTextInput

logger = logging.getLogger(__name__)


def firm_name_html(row_data: dict[str, str]) -> str:
    _firm_id = row_data.get("firm_id", "")
    _firm_name = row_data.get("firm_name", "")
    return f"<a class='govuk-link', href={url_for('main.view_provider', firm=_firm_id)}>{_firm_name}"


def get_firm_statuses(row_data):
    status_tags = get_firm_tags(firm=row_data)
    if status_tags:
        return f"<div>{''.join([s.render() for s in status_tags])}</div>"
    return "<p class='govuk-visually-hidden'>No statuses</p>"


def firm_account_number_html(row_data: dict[str, str]) -> str:
    firm_id = row_data.get("firm_id")
    firm_account_number = "UNKNOWN"
    if firm_id:
        try:
            firm_account_number = get_firm_account_number(int(firm_id))
        except ValueError:
            logger.error(f"Invalid firm number: {firm_id} from {row_data}")
    return firm_account_number


class ProviderListForm(BaseForm):
    title = "Provider records"
    url = "providers"
    template = "providers.html"
    providers_shown_per_page = 20

    class Meta:
        csrf = False  # CSRF is disabled as this form only accepts GET requests with search data in a query string.

    search = StringField(
        "Find a provider",
        widget=GovTextInput(
            form_group_classes="govuk-!-width-two-thirds",
            heading_class="govuk-fieldset__legend--s",
            hint="You can search by name, provider number or account number",
        ),
        validators=[Length(max=100, message="Search term must be 100 characters or less")],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get firms data
        pda = current_app.extensions["pda"]
        firms: list[Firm] = pda.get_all_provider_firms()

        self.search_term = self.data.get("search", None)

        # On initial page load we show no results
        if self.search_term is None:
            firms = []
        # If an empty search is submitted we show all providers
        elif self.search_term == "":
            pass
        else:
            # Here we need to clean up the search terms to remove % and make sure it doesnt break responses
            search_lower = normalize_for_search(self.search_term).lower()
            firms = [
                firm
                for firm in firms
                if (
                    search_lower in normalize_for_search(firm.firm_name).lower()
                    or search_lower in normalize_for_search(str(firm.firm_id)).lower()
                )
            ]

        self.page = self.data.get("page", 1)
        self.num_results = len(firms)

        # Limit results and populate choices
        start_id = self.providers_shown_per_page * (self.page - 1)
        end_id = self.providers_shown_per_page * (self.page - 1) + self.providers_shown_per_page

        columns: list[TableStructureItem] = [
            {"text": "Provider name", "id": "firm_name", "html_renderer": firm_name_html},
            {"text": "Provider type", "id": "firm_type", "format_text": format_sentence_case},
            {"text": "Account number", "html_renderer": firm_account_number_html},
            {"text": "Status", "html_renderer": get_firm_statuses},  # Add status tags here when available.
        ]

        if len(firms) > 0:
            self.table = DataTable(structure=columns, data=[firm.to_internal_dict() for firm in firms[start_id:end_id]])


class BaseBankAccountForm(BaseForm):
    bank_account_name = StringField(
        "Account name",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            classes="govuk-!-width-one-quarter",
        ),
        validators=[
            InputRequired(message="Enter the account name"),
            Length(max=100, message="Account name must be 100 characters or less"),
        ],
    )

    sort_code = StringField(
        "Sort code",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            classes="govuk-input--width-10",
            hint="Must be 6 digits long",
        ),
        validators=[
            InputRequired(message="Enter a sort code"),
            ValidateSortCode(),
        ],
    )

    account_number = StringField(
        "Account number",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            classes="govuk-!-width-one-quarter",
            hint="Must be between 6 and 8 digits long",
        ),
        validators=[
            InputRequired(message="Enter an account number"),
            ValidateAccountNumber(),
        ],
    )


class SearchableTableForm(BaseForm):
    ITEMS_PER_PAGE = 10
    SEARCH_FIELD_LABEL = "Search term"
    SEARCH_FIELD_HINT = None
    SEARCH_FIELD_VALIDATORS = []

    search = StringField(
        SEARCH_FIELD_LABEL,
        widget=GovTextInput(
            form_group_classes="govuk-!-width-two-thirds",
            heading_class="govuk-fieldset__legend--s",
            hint=SEARCH_FIELD_LABEL,
        ),
        validators=[],
    )

    def __init__(self, *args, search_term="", page=1, selected_value=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.search.label.text = self.SEARCH_FIELD_LABEL
        self.search.widget.hint_text = self.SEARCH_FIELD_HINT
        self.search.validators = self.SEARCH_FIELD_VALIDATORS

        self.page = page

        # Set search field data
        self.search_term = search_term
        if search_term:
            self.search.data = search_term

        # Filter bank accounts based on search term
        if search_term is None:
            return

        data = self.get_searchable_data()
        data = self.filter_searchable_data(data, search_term)
        self.num_results = len(data)
        # Limit results and populate choices
        data = self.paginate_data(data, page)

        # Create RadioDataTable for contract managers
        table_structure: list[TableStructureItem] = self.describe_data_structure()
        self.bank_accounts_table = RadioDataTable(
            structure=table_structure,
            data=data,
            radio_field_name="bank_account",
            radio_value_key="bank_account_id",
        )

        # Store selected value for table rendering
        self.selected_value = selected_value

    def describe_data_structure(self) -> list[dict[str, str]]:
        """Example return results
         [
            {"text": "Label", "id": "data_field_name"},
            {"text": "Account number", "id": "account_number"},
            {"text": "Account name", "id": "bank_account_name"},
        ]
        """
        return []

    def get_searchable_data(self, *args, **kwargs) -> List[dict[str, Any]]:
        """get a list of data that can be searched"""
        return []

    def filter_searchable_data(self, data: List[dict[str, Any]], search_term: str) -> List[dict[str, Any]]:
        """Filter data based on search term."""
        return data

    def paginate_data(self, data: List[dict[str, Any]], page: int) -> List[dict[str, Any]]:
        start_id = self.ITEMS_PER_PAGE * (page - 1)
        end_id = self.ITEMS_PER_PAGE * (page - 1) + self.ITEMS_PER_PAGE
        return data[start_id:end_id]


class NoBankAccountsError(Exception):
    pass


class BaseBankAccountSearchForm(SearchableTableForm):
    title = "Search for bank account"
    SEARCH_FIELD_LABEL = "Search for a bank account"
    SEARCH_FIELD_HINT = "You can search by sort code or account number"
    SEARCH_FIELD_MAX_CHARS = 8
    bank_account = StringField(
        validators=[DataRequired(message="Select a bank account or search again")],
    )

    def describe_data_structure(self) -> list[dict[str, Any]]:
        return [
            {"text": "Sort code", "id": "sort_code"},
            {"text": "Account number", "id": "account_number"},
            {"text": "Account name", "id": "bank_account_name"},
        ]

    def get_bank_accounts(self, *args, **kwargs) -> List[BankAccount]:
        """
        Get list of all bank accounts

        Returns:
            List[dict[str, any]: List of bank accounts

        Raises:
            NoBankAccountsError: No bank accounts found
        """
        pda = current_app.extensions["pda"]
        return pda.get_all_bank_accounts()

    @classmethod
    def sort_bank_accounts(
        cls,
        bank_accounts: List[BankAccount],
    ) -> list[BankAccount]:
        """Sort bank accounts based on the start date"""

        # Sink bank accounts with no start date to the bottom
        no_start_date_default = (datetime.today() - timedelta(weeks=5200)).date()
        return sorted(
            bank_accounts,
            key=lambda account: account.start_date if account.start_date else no_start_date_default,
            reverse=True,
        )

    def get_searchable_data(self, *args, **kwargs) -> List[dict[str, Any]]:
        bank_accounts = self.get_bank_accounts(*args, **kwargs)

        if not bank_accounts:
            raise NoBankAccountsError("No bank accounts found")
        bank_accounts = self.sort_bank_accounts(bank_accounts)
        return [bank_account.to_internal_dict() for bank_account in bank_accounts]

    def filter_searchable_data(self, bank_accounts: List[dict[str, Any]], search_term: str) -> List[dict[str, Any]]:
        """
        Get bank accounts matching the search term

        Args:
        search_term: A bank account sort code or account number to search for

        Returns:
            List[dict[str, any]: List of bank accounts that match the search term
        """
        if not search_term:
            # Return all bank accounts when no search term is provided.
            return bank_accounts

        matched_bank_accounts = []
        for bank_account in bank_accounts:
            search_fields = [bank_account["account_number"], bank_account["sort_code"]]
            if search_term in search_fields:
                matched_bank_accounts.append(bank_account)
        return matched_bank_accounts
