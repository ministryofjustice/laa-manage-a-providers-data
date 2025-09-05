import logging
import math
from typing import Literal, NoReturn

from flask import abort, current_app, redirect, render_template, request, session, url_for
from flask.views import MethodView

from app.components.tables import DataTable, TableStructure, TransposedDataTable, add_field
from app.main.utils import add_new_provider
from app.models import Firm, Office
from app.utils.formatting import (
    format_advocate_level,
    format_constitutional_status,
    format_date,
    format_firm_type,
    format_head_office,
    format_office_address_one_line,
    format_yes_no,
)
from app.views import BaseFormView

logger = logging.getLogger(__name__)


class ProviderList(BaseFormView):
    """View for provider list"""

    template = "providers.html"
    firms_shown_per_page = 20

    @staticmethod
    def firm_name_html(row_data: dict[str, str]) -> str:
        _firm_id = row_data.get("firm_id", "")
        _firm_name = row_data.get("firm_name", "")
        return f"<a class='govuk-link', href={url_for('main.view_provider', firm=_firm_id)}>{_firm_name}"

    def get(self, context):
        form = self.get_form_class()(request.args)

        pda = current_app.extensions["pda"]
        firms: list[Firm] = pda.get_all_provider_firms()

        # Filter providers based on search term
        if form.validate() and form.data.get("search"):
            search_lower = form.data.get("search").lower()
            firms = [
                firm
                for firm in firms
                if (search_lower in firm.firm_name.lower() or search_lower in str(firm.firm_id).lower())
            ]

        columns: list[TableStructure] = [
            {"text": "Provider name", "id": "firm_name", "html_renderer": self.firm_name_html},
            {"text": "Account number", "id": "firm_number"},
            {"text": "Provider type", "id": "firm_type"},
        ]

        form.page = request.args.get("page", 1, type=int)
        form.firms_shown_per_page = self.firms_shown_per_page
        form.num_results = len(firms)

        max_page = math.ceil(len(firms) / self.firms_shown_per_page)
        if form.page < 1 or form.page > max_page:
            abort(404)

        if form.num_results == 0:
            form.search.errors.append("No providers found. Check the spelling and search for something else.")

        start_id = self.firms_shown_per_page * (form.page - 1)
        end_id = self.firms_shown_per_page * (form.page - 1) + self.firms_shown_per_page

        table = DataTable(structure=columns, data=[firm.to_internal_dict() for firm in firms[start_id:end_id]])

        return render_template(self.get_template(), table=table, **self.get_context_data(form, context))

    def post(self, context) -> NoReturn:
        """POST method not allowed for this resource."""
        abort(405)


class ViewProvider(MethodView):
    template = "view-provider.html"

    def __init__(self, subpage: Literal["contact", "offices"] = "contact"):
        if subpage:
            self.subpage = subpage

    @staticmethod
    def parent_provider_name_html(parent_provider: Firm):
        return f"<a class='govuk-link', href={url_for('main.view_provider', firm=parent_provider.firm_id)}>{parent_provider.firm_name}</a>"

    def get_main_table(self, firm, head_office, parent_provider) -> DataTable:
        main_rows, main_data = [], {}
        add_field(main_rows, main_data, firm.firm_name, "Provider name")
        add_field(main_rows, main_data, firm.firm_number, "Provider number")

        if head_office:
            add_field(main_rows, main_data, head_office.firm_office_code, "Account number")

        if parent_provider:
            add_field(
                main_rows,
                main_data,
                parent_provider.firm_name,
                "Parent provider name",
                html=self.parent_provider_name_html(parent_provider),
            )
            add_field(main_rows, main_data, parent_provider.firm_number, "Parent provider number")

        main_table = TransposedDataTable(structure=main_rows, data=main_data) if main_rows else None

        return main_table

    def get_additional_table(self, firm) -> DataTable:
        additional_rows, additional_data = [], {}
        add_field(
            additional_rows,
            additional_data,
            firm.constitutional_status,
            "Constitutional status",
            format_constitutional_status,
        )
        add_field(
            additional_rows, additional_data, firm.indemnity_received_date, "Indemnity received date", format_date
        )
        add_field(
            additional_rows, additional_data, firm.non_profit_organisation, "Not for profit organisation", format_yes_no
        )
        add_field(additional_rows, additional_data, firm.solicitor_advocate, "Solicitor advocate", format_yes_no)
        add_field(additional_rows, additional_data, firm.advocate_level, "Advocate level", format_advocate_level)
        add_field(additional_rows, additional_data, firm.company_house_number, "Companies House number")
        add_field(additional_rows, additional_data, firm.bar_council_roll, "Bar Council roll number")

        additional_table = (
            TransposedDataTable(structure=additional_rows, data=additional_data) if additional_rows else None
        )

        return additional_table

    def get_office_tables(self, firm, head_office: Office, other_offices: list[Office]) -> dict[str, DataTable]:
        """Gets two data tables one for the main office and one for other offices."""
        office_tables = {}

        def firm_office_html(row_data: dict[str, str]) -> str:
            # Renders the office account number as a link
            _office_code = row_data.get("firm_office_code", "")
            return f"<a class='govuk-link' href='{url_for('main.view_office', firm=firm.firm_id, office=_office_code)}'>{_office_code}</a>"

        office_table_structure: list[TableStructure] = [
            {"text": "Account number", "id": "firm_office_code", "html_renderer": firm_office_html},
            {"text": "Address", "text_renderer": format_office_address_one_line},
            {"text": "Status", "id": "firm_number"},
        ]

        if head_office:
            head_office_data_table = DataTable(office_table_structure, head_office.to_internal_dict())
            office_tables.update({"head": head_office_data_table})

        if other_offices:
            other_offices_dict = list(map(lambda o: o.to_internal_dict(), other_offices))
            other_offices_data_table = DataTable(office_table_structure, other_offices_dict)
            office_tables.update({"other": other_offices_data_table})

        return office_tables

    def get_context(self, firm):
        pda = current_app.extensions["pda"]

        head_office, parent_provider = None, None

        if firm.firm_id:
            # Get head office for account number
            head_office: Office = pda.get_head_office(firm.firm_id)

        if firm.parent_firm_id:
            # Get parent provider
            parent_provider: Firm = pda.get_provider_firm(firm.parent_firm_id)

        main_table = self.get_main_table(firm, head_office, parent_provider)
        additional_table = self.get_additional_table(firm)

        context = {"main_table": main_table, "additional_table": additional_table}

        if True:
            offices = pda.get_provider_offices(firm.firm_id)

            # Remove the head office from the list of offices
            other_offices = list(filter(lambda o: not o.get_is_head_office(), offices))

            office_tables = self.get_office_tables(firm, head_office, other_offices)
            context.update({"office_tables": office_tables})

        return context

    def get(self, firm: Firm | None = None):
        if not firm:
            if firm_data := session.get("new_provider"):
                del session["new_provider"]
                firm = add_new_provider(Firm(**firm_data))
                return redirect(url_for("main.view_provider", firm=firm))
            abort(404)

        context = self.get_context(firm)

        return render_template(self.template, firm=firm, subpage=self.subpage, **context)


class ViewOffice(MethodView):
    template = "view-office.html"

    @staticmethod
    def parent_provider_name_html(parent_provider: Firm):
        return f"<a class='govuk-link', href={url_for('main.view_provider', firm=parent_provider.firm_id)}>{parent_provider.firm_name}</a>"

    def get(self, firm: Firm, office: Office | None = None):
        if not firm or not office:
            abort(404)

        # Overview section
        overview_rows, overview_data = [], {}
        add_field(
            overview_rows,
            overview_data,
            firm.firm_name,
            "Parent provider",
            html=self.parent_provider_name_html(firm),
        )
        add_field(overview_rows, overview_data, office.firm_office_code, "Account number")
        add_field(overview_rows, overview_data, office.head_office, "Head office", format_head_office)
        add_field(overview_rows, overview_data, firm.firm_type, "Supplier type", format_firm_type)

        # Create tables
        overview_table = TransposedDataTable(structure=overview_rows, data=overview_data) if overview_rows else None

        return render_template(self.template, overview_table=overview_table, firm=firm, office=office)
