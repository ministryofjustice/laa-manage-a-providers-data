from flask import current_app, flash, render_template, session
from flask.views import MethodView

from app.components.tables import TransposedDataTable
from app.pda.api import ProviderDataApiError
from app.utils.formatting import (
    format_constitutional_status,
    format_date,
    format_provider_type,
    format_title_case,
    format_yes_no,
)


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
