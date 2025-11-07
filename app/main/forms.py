from flask import current_app, url_for
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Length

from app.components.tables import DataTable, TableStructureItem
from app.forms import BaseForm
from app.models import Firm
from app.utils.formatting import format_sentence_case, normalize_for_search
from app.validators import ValidateAccountNumber, ValidateSortCode
from app.widgets import GovTextInput


def firm_name_html(row_data: dict[str, str]) -> str:
    _firm_id = row_data.get("firm_id", "")
    _firm_name = row_data.get("firm_name", "")
    return f"<a class='govuk-link', href={url_for('main.view_provider', firm=_firm_id)}>{_firm_name}"


def get_firm_statuses(row_data):
    # Add logic to render firm status tags here when available.
    return "<p class='govuk-visually-hidden'>No statuses</p>"


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
            {"text": "Provider number", "id": "firm_number"},
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
