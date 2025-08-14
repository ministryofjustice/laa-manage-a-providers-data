from flask import Response, current_app, flash, redirect, render_template, request, session, url_for
from flask.views import MethodView

from app.components.tables import TransposedDataTable
from app.main.add_a_new_provider import AssignChambersForm
from app.pda.api import ProviderDataApiError
from app.utils.formatting import (
    format_constitutional_status,
    format_date,
    format_provider_type,
    format_title_case,
    format_yes_no,
)
from app.views import BaseFormView


class AddProviderFormView(BaseFormView):
    """Form view for the add provider"""

    template = "templates/form.html"

    next_step_mapping = {
        "barrister": "main.assign_chambers",
        "advocate": "main.assign_chambers",
        "chambers": "main.add_provider/chambers_details",
        "lsp": "main.additional_details_legal_services_provider",
    }

    def form_valid(self, form):
        session["provider_name"] = form.data.get("provider_name")
        session["provider_type"] = form.data.get("provider_type")

        # Call parent method for redirect
        return super().form_valid(form)

    def get_success_url(self, form):
        provider_type = form.data.get("provider_type")
        next_page = self.next_step_mapping.get(provider_type)
        return url_for(next_page)


class LspDetailsFormView(BaseFormView):
    """Form view for the Legal services provider details"""

    success_endpoint = "main.view_provider"

    def form_valid(self, form):
        session["constitutional_status"] = form.data.get("constitutional_status")
        session["companies_house_number"] = form.data.get("companies_house_number")

        indemnity_date = form.data.get("indemnity_received_date")
        if indemnity_date:
            session["indemnity_received_date"] = indemnity_date.isoformat()

        flash("New provider successfully created", "success")
        return super().form_valid(form)


class ChambersDetailsFormView(BaseFormView):
    """Form view for the Chambers details"""

    pass


class AssignChambersFormView(BaseFormView):
    """Form view for the assign to a chambers form"""

    template = "add_provider/assign-chambers.html"
    success_url = "main.providers"

    def form_valid(self, form):
        session["parent_provider_id"] = form.data.get("provider")
        return redirect(url_for(self.success_url))

    def get(self, context):
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form: AssignChambersForm = self.get_form_class()(search_term=search_term, page=page)

        if search_term:
            form.search.validate(form)

        return render_template(self.get_template(), **self.get_context_data(form, context))

    def post(self, context) -> Response | str:
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(search_term=search_term, page=page)
        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class ViewProvider(MethodView):
    template = "view-provider.html"

    MAIN_SECTION_FIELDS = [
        {"session_key": "provider_name", "label": "Provider name", "formatter": None},
        {"session_key": "provider_number", "label": "Provider number", "formatter": None},
    ]

    ADDITIONAL_DETAILS_FIELDS = [
        {"session_key": "provider_type", "label": "Provider type", "formatter": format_provider_type},
        {
            "session_key": "constitutional_status",
            "label": "Constitutional status",
            "formatter": format_constitutional_status,
        },
        {"session_key": "indemnity_received_date", "label": "Indemnity received date", "formatter": format_date},
        {"session_key": "companies_house_number", "label": "Companies House number", "formatter": None},
        {
            "session_key": "not_for_profit_organisation",
            "label": "Not for profit organisation",
            "formatter": format_yes_no,
        },
        {"session_key": "solicitor_advocate", "label": "Solicitor advocate", "formatter": format_yes_no},
        {"session_key": "advocate_level", "label": "Advocate level", "formatter": format_title_case},
        {"session_key": "bar_or_council_roll", "label": "Bar or council roll", "formatter": None},
        {"session_key": "firm_intervened", "label": "Firm intervened", "formatter": format_yes_no},
    ]

    @staticmethod
    def _process_fields(field_configs):
        """Process field configurations and return rows and data for table creation"""
        rows = []
        data = {}

        for field_config in field_configs:
            session_value = session.get(field_config["session_key"])
            if session_value:
                rows.append({"text": field_config["label"], "id": field_config["session_key"]})
                formatted_value = (
                    field_config["formatter"](session_value) if field_config["formatter"] else session_value
                )
                data[field_config["session_key"]] = formatted_value

        return rows, data

    def get(self):
        main_rows, main_data = self._process_fields(self.MAIN_SECTION_FIELDS)

        # Handle parent provider info (special case requiring API call)
        parent_provider_id = session.get("parent_provider_id")
        if parent_provider_id:
            pda = current_app.extensions["pda"]
            try:
                parent_provider = pda.get_provider_firm(firm_id=int(parent_provider_id))["firm"]

                main_rows.append({"text": "Parent provider name", "id": "parent_provider_name"})
                main_data["parent_provider_name"] = parent_provider["firmName"]

                main_rows.append({"text": "Parent provider number", "id": "parent_provider_number"})
                main_data["parent_provider_number"] = parent_provider["firmNumber"]
            except ProviderDataApiError:
                flash("Parent provider not found", "error")
                pass

        additional_rows, additional_data = self._process_fields(self.ADDITIONAL_DETAILS_FIELDS)

        main_table = TransposedDataTable(structure=main_rows, data=main_data) if main_rows else None
        additional_table = (
            TransposedDataTable(structure=additional_rows, data=additional_data) if additional_rows else None
        )

        return render_template(
            self.template,
            main_table=main_table,
            additional_table=additional_table,
            provider_name=main_data.get("provider_name"),
            provider_type=additional_data.get("provider_type"),
        )
