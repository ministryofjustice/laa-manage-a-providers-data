import math
from typing import NoReturn

from flask import abort, current_app, flash, render_template, request, session, url_for
from flask.views import MethodView

from app.components.tables import DataTable, TableStructure, TransposedDataTable
from app.models import Firm, Office
from app.utils.formatting import format_advocate_level, format_constitutional_status, format_date, format_yes_no
from app.views import BaseFormView


class ProviderList(BaseFormView):
    """View for provider list"""

    template = "providers.html"
    firms_shown_per_page = 20

    @staticmethod
    def firm_name_html(row_data: dict[str, str]) -> str:
        _firm_id = row_data.get("firm_id", "")
        _firm_name = row_data.get("firm_name", "")
        return f"<a class='govuk-link', href={url_for('main.view_provider_with_id', firm_id=_firm_id)}>{_firm_name}"

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
            {"text": "Provider name", "id": "firm_name", "html": self.firm_name_html},
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

    @staticmethod
    def parent_provider_name_html(parent_provider: Firm):
        return f"<a class='govuk-link', href={url_for('main.view_provider_with_id', firm_id=parent_provider.firm_id)}>{parent_provider.firm_name}</a>"

    @staticmethod
    def _add_field(rows, data, value, label, formatter=None, html=None):
        """Helper to add a field if it has a value. Uses snake_case label as ID."""
        if value:
            # Convert label to snake_case for the ID
            field_id = label.lower().replace(" ", "_")
            row = {"text": label, "id": field_id, "classes": "govuk-!-width-one-half"}
            if html:
                row.update({"html": html})
            rows.append(row)
            data[field_id] = formatter(value) if formatter else value

    def get(self, firm_id: int | None = None):
        pda = current_app.extensions["pda"]

        if firm_id:
            firm = pda.get_provider_firm(firm_id)
        else:
            # If there is no firm in the URL load from the session
            flash("<b>New provider successfully created</b>", "success")
            if firm := session.get("new_provider", None):
                firm = Firm(**firm)

        if not firm:
            abort(404)

        head_office, parent_provider = None, None

        if firm.firm_id:
            # Get head office for account number
            head_office: Office = pda.get_head_office(firm.firm_id)

        if firm.parent_firm_id:
            # Get parent provider
            parent_provider: Firm = pda.get_provider_firm(firm.parent_firm_id)

        # Main section
        main_rows, main_data = [], {}
        self._add_field(main_rows, main_data, firm.firm_name, "Provider name")
        self._add_field(main_rows, main_data, firm.firm_number, "Provider number")

        if head_office:
            self._add_field(main_rows, main_data, head_office.firm_office_code, "Account number")

        if parent_provider:
            self._add_field(
                main_rows,
                main_data,
                parent_provider.firm_name,
                "Parent provider name",
                html=self.parent_provider_name_html(parent_provider),
            )
            self._add_field(main_rows, main_data, parent_provider.firm_number, "Parent provider number")

        # Additional section
        additional_rows, additional_data = [], {}
        self._add_field(
            additional_rows,
            additional_data,
            firm.constitutional_status,
            "Constitutional status",
            format_constitutional_status,
        )
        self._add_field(
            additional_rows, additional_data, firm.indemnity_received_date, "Indemnity received date", format_date
        )
        self._add_field(
            additional_rows, additional_data, firm.non_profit_organisation, "Not for profit organisation", format_yes_no
        )
        self._add_field(additional_rows, additional_data, firm.solicitor_advocate, "Solicitor advocate", format_yes_no)
        self._add_field(additional_rows, additional_data, firm.advocate_level, "Advocate level", format_advocate_level)
        self._add_field(additional_rows, additional_data, firm.company_house_number, "Companies House number")
        self._add_field(additional_rows, additional_data, firm.bar_council_roll, "Bar Council roll number")

        # Create tables
        main_table = TransposedDataTable(structure=main_rows, data=main_data) if main_rows else None
        additional_table = (
            TransposedDataTable(structure=additional_rows, data=additional_data) if additional_rows else None
        )

        return render_template(
            self.template,
            main_table=main_table,
            additional_table=additional_table,
            provider_name=firm.firm_name,
            provider_type=firm.firm_type,
        )
