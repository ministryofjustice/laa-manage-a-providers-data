from typing import NoReturn

from flask import abort, current_app, redirect, render_template, request, session, url_for
from flask.views import MethodView

from app.components.tables import TransposedDataTable
from app.main.utils import add_new_provider
from app.models import Firm, Office
from app.utils.formatting import format_advocate_level, format_constitutional_status, format_date, format_yes_no
from app.views import BaseFormView


class ProviderList(BaseFormView):
    """View for provider list"""

    template = "providers.html"

    def get(self, context):
        form = self.get_form_class()(request.args)
        form.validate()
        return render_template(self.get_template(), **self.get_context_data(form, context))

    def post(self, context) -> NoReturn:
        """POST method not allowed for this resource."""
        abort(405)


class ViewProvider(MethodView):
    template = "view-provider.html"

    @staticmethod
    def parent_provider_name_html(parent_provider: Firm):
        return f"<a class='govuk-link', href={url_for('main.view_provider_with_id', firm=parent_provider.firm_id)}>{parent_provider.firm_name}</a>"

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

    def get(self, firm: Firm | None = None):
        pda = current_app.extensions["pda"]

        if not firm:
            if firm_data := session.get("new_provider"):
                del session["new_provider"]
                firm = add_new_provider(Firm(**firm_data))
                return redirect(url_for("main.view_provider_with_id", firm=firm))
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
            firm=firm,
        )
