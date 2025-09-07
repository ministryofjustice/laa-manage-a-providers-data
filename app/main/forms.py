from flask import current_app, url_for
from wtforms.fields.simple import StringField
from wtforms.validators import Length

from app.components.tables import DataTable, TableStructure
from app.forms import BaseForm
from app.models import Firm
from app.validators import ValidateSearchResults
from app.widgets import GovTextInput


def firm_name_html(row_data: dict[str, str]) -> str:
    _firm_id = row_data.get("firm_id", "")
    _firm_name = row_data.get("firm_name", "")
    return f"<a class='govuk-link', href={url_for('main.view_provider_with_id', firm=_firm_id)}>{_firm_name}"


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
        validators=[Length(max=100, message="Search term must be 100 characters or less"), ValidateSearchResults()],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Get firms data
        pda = current_app.extensions["pda"]
        firms: list[Firm] = pda.get_all_provider_firms()

        self.search_term = self.data.get("search", None)

        # Filter providers based on search term
        if self.search_term != "":
            search_lower = str(self.search_term).lower()
            firms = [
                firm
                for firm in firms
                if (search_lower in firm.firm_name.lower() or search_lower in str(firm.firm_id).lower())
            ]

        self.page = self.data.get("page", 1)
        self.num_results = len(firms)

        # Limit results and populate choices
        start_id = self.providers_shown_per_page * (self.page - 1)
        end_id = self.providers_shown_per_page * (self.page - 1) + self.providers_shown_per_page

        columns: list[TableStructure] = [
            {"text": "Provider name", "id": "firm_name", "html": firm_name_html},
            {"text": "Provider type", "id": "firm_type"},
            {"text": "Provider number", "id": "firm_number"},
            {"text": "Status", "html": get_firm_statuses},  # Add status tags here when available.
        ]

        if len(firms) > 0:
            self.table = DataTable(structure=columns, data=[firm.to_internal_dict() for firm in firms[start_id:end_id]])
