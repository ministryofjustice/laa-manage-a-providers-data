from app.main.utils import get_entity_active_text, provider_name_html
from app.utils.formatting import (
    format_advocate_level,
    format_constitutional_status,
    format_date,
    format_yes_no,
)

# Valid data sources to use in the view provider main table configuration, default is firm
MAIN_TABLE_VALID_DATA_SOURCES = ["firm", "parent_firm", "head_office"]

# Status table configuration for different entity types
STATUS_TABLE_FIELD_CONFIG = {
    "Legal Services Provider": [
        {
            "label": "Active",
            "text_renderer": get_entity_active_text,
            "change_link": "main.change_provider_active_status",
        },
        {
            "label": "Payments on hold",
            "id": "hold_all_payments_flag",
            "formatter": format_yes_no,
            "default": "No",
        },
        {"label": "Intervened", "default": "No"},
        {"label": "Referred to debt recovery", "default": "No"},
    ],
    "Chambers": [
        {
            "label": "Active",
            "text_renderer": get_entity_active_text,
            "change_link": "main.change_provider_active_status",
        },
    ],
    "Barrister": [
        {
            "label": "Active",
            "text_renderer": get_entity_active_text,
            "change_link": "main.change_provider_active_status",
        },
        {
            "label": "Payments on hold",
            "id": "hold_all_payments_flag",
            "formatter": format_yes_no,
            "default": "No",
        },
        {"label": "Intervened", "default": "No"},
        {"label": "Referred to debt recovery", "default": "No"},
    ],
    "Advocate": [
        {
            "label": "Active",
            "text_renderer": get_entity_active_text,
            "change_link": "main.change_provider_active_status",
        },
        {
            "label": "Payments on hold",
            "id": "hold_all_payments_flag",
            "formatter": format_yes_no,
            "default": "No",
        },
        {"label": "Intervened", "default": "No"},
        {"label": "Referred to debt recovery", "default": "No"},
    ],
    "Office": [
        {
            "label": "Active",
            "text_renderer": get_entity_active_text,
            "change_link": "main.office_active_status_form",
        },
        {
            "label": "Payments on hold",
            "id": "hold_all_payments_flag",
            "formatter": format_yes_no,
            "default": "No",
        },
        {"label": "Intervened", "default": "No"},
        {
            "label": "Referred to debt recovery",
            "default": "No",
            "visible": lambda office: office.get("inactive_date") is None,
        },  # Show if inactive
        {
            "label": "False balance",
            "default": "No",
            "visible": lambda office: office.get("inactive_date"),
        },  # Show if active
    ],
}

# View provider ,ain table configuration for each firm type
MAIN_TABLE_FIELD_CONFIG = {
    "Legal Services Provider": [
        {"label": "Provider name", "id": "firm_name"},
        {"label": "Provider number", "id": "firm_number"},
        {"label": "Account number", "id": "firm_office_code", "data_source": "head_office"},
        {"label": "Parent provider name", "id": "firm_name", "data_source": "parent_firm", "hide_if_null": True},
        {
            "label": "Parent provider number",
            "id": "firm_number",
            "data_source": "parent_firm",
            "hide_if_null": True,
        },
        {
            "label": "Constitutional status",
            "id": "constitutional_status",
            "formatter": format_constitutional_status,
        },
        {
            "label": "Indemnity received date",
            "id": "indemnity_received_date",
            "formatter": format_date,
            "default": "Not provided",
        },
        {"label": "Companies House number", "id": "company_house_number", "default": "Not provided"},
        {"label": "Contract manager", "id": "contract_manager"},
    ],
    "Chambers": [
        {"label": "Provider name", "id": "firm_name"},
        {"label": "Provider number", "id": "firm_number"},
        {"label": "Account number", "id": "firm_office_code", "data_source": "head_office"},
        {"label": "Parent provider name", "id": "firm_name", "data_source": "parent_firm", "hide_if_null": True},
        {
            "label": "Parent provider number",
            "id": "firm_number",
            "data_source": "parent_firm",
            "hide_if_null": True,
        },
    ],
    "Barrister": [
        {"label": "Barrister name", "id": "firm_name"},
        {"label": "Barrister number", "id": "firm_number"},
        {"label": "Account number", "id": "firm_office_code", "data_source": "head_office"},
        {
            "label": "Chambers",
            "id": "firm_name",
            "html_renderer": provider_name_html,
            "data_source": "parent_firm",
            "change_link": "main.assign_chambers",
        },
        {"label": "Barrister level", "id": "advocate_level", "formatter": format_advocate_level},
        {"label": "Bar Council roll number", "id": "bar_council_roll"},
    ],
    "Advocate": [
        {"label": "Advocate name", "id": "firm_name"},
        {"label": "Advocate number", "id": "firm_number"},
        {"label": "Account number", "id": "firm_office_code", "data_source": "head_office"},
        {
            "label": "Chambers",
            "id": "firm_name",
            "html_renderer": provider_name_html,
            "data_source": "parent_firm",
            "change_link": "main.assign_chambers",
        },
        {"label": "Advocate level", "id": "advocate_level", "formatter": format_advocate_level},
        {"label": "Solicitors Regulation Authority roll number", "id": "bar_council_roll"},
    ],
}
