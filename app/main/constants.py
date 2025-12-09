from app.main.utils import (
    contract_manager_changeable,
    contract_manager_nonstatus_name,
    get_entity_active_text,
    get_entity_referred_to_debt_recovery_text,
    get_firm_false_balance_text,
    get_office_false_balance_text,
    provider_name_html, get_entity_intervened_text,
)
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
        {
            "label": "Referred to debt recovery",
            "text_renderer": get_entity_referred_to_debt_recovery_text,
            "default": "No",
        },
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
        {"label": "Intervened", "default": "No", "text_renderer": get_entity_intervened_text, "change_link": "main.change_office_intervened"},
        {
            "label": "Referred to debt recovery",
            "text_renderer": get_entity_referred_to_debt_recovery_text,
            "default": "No",
        },
        {
            "label": "False balance",
            "text_renderer": get_firm_false_balance_text,
            "default": "No",
            "visible": lambda office: office.get("inactive_date") is not None,
            "change_link": "main.change_firm_false_balance",
        },
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
        {"label": "Intervened", "default": "No", "text_renderer": get_entity_intervened_text, "change_link": "main.change_office_intervened"},
        {
            "label": "Referred to debt recovery",
            "text_renderer": get_entity_referred_to_debt_recovery_text,
            "default": "No",
        },
        {
            "label": "False balance",
            "text_renderer": get_firm_false_balance_text,
            "default": "No",
            "visible": lambda office: office.get("inactive_date") is not None,
            "change_link": "main.change_firm_false_balance",
        },
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
        {"label": "Intervened", "default": "No", "text_renderer": get_entity_intervened_text, "change_link": "main.change_office_intervened"},
        {
            "label": "Referred to debt recovery",
            "default": "No",
            "visible": lambda office: office.get("inactive_date") is None,
        },  # Show if inactive
        {
            "label": "False balance",
            "default": "No",
            "text_renderer": get_office_false_balance_text,
            "visible": lambda office: office.get("inactive_date"),
            "change_link": "main.change_office_false_balance",
        },  # Show if active
    ],
}

# View provider main table configuration for each firm type
MAIN_TABLE_FIELD_CONFIG = {
    "Legal Services Provider": [
        {
            "label": "Provider name",
            "id": "firm_name",
            "row_action_urls": {
                "enter": "main.change_legal_services_provider_name",
                "change": "main.change_legal_services_provider_name",
            },
        },
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
            "row_action_urls": {
                "change": {
                    "link": "main.change_lsp_details",
                    "anchor": "constitutional_status",
                },
                "enter": {
                    "link": "main.change_lsp_details",
                    "anchor": "constitutional_status",
                },
            },
        },
        {
            "label": "Indemnity received date",
            "id": "indemnity_received_date",
            "formatter": format_date,
            "default": "Not provided",
            "row_action_urls": {
                "change": {
                    "link": "main.change_lsp_details",
                    "anchor": "indemnity_received_date",
                },
                "enter": {
                    "link": "main.change_lsp_details",
                    "anchor": "indemnity_received_date",
                },
            },
        },
        {
            "label": "Companies House number",
            "id": "company_house_number",
            "default": "Not provided",
            "row_action_urls": {
                "change": {
                    "link": "main.change_lsp_details",
                    "anchor": "companies_house_number",
                },
                "enter": {
                    "link": "main.change_lsp_details",
                    "anchor": "companies_house_number",
                },
            },
        },
        {
            "label": "Contract manager",
            "id": "contract_manager",
            "data_source": "head_office",
            "value_preprocessor": contract_manager_nonstatus_name,
            "visible": contract_manager_changeable,
            "row_action_urls": {
                "enter": "main.change_office_contract_manager",
                "change": "main.change_office_contract_manager",
            },
            "row_action_texts": {"enter": "Assign contract manager"},
        },
    ],
    "Chambers": [
        {
            "label": "Provider name",
            "id": "firm_name",
            "row_action_urls": {
                "enter": "main.change_legal_services_provider_name",
                "change": "main.change_legal_services_provider_name",
            },
        },
        {"label": "Provider number", "id": "firm_number"},
        {"label": "Chambers number", "id": "firm_office_code", "data_source": "head_office"},
        {"label": "Parent provider name", "id": "firm_name", "data_source": "parent_firm", "hide_if_null": True},
        {
            "label": "Parent provider number",
            "id": "firm_number",
            "data_source": "parent_firm",
            "hide_if_null": True,
        },
    ],
    "Barrister": [
        {
            "label": "Barrister name",
            "id": "firm_name",
            "row_action_urls": {
                "change": {
                    "link": "main.barrister_change_details",
                    "anchor": "barrister_name",
                },
                "enter": {
                    "link": "main.barrister_change_details",
                    "anchor": "barrister_name",
                },
            },
        },
        {"label": "Barrister number", "id": "firm_number"},
        {"label": "Account number", "id": "firm_office_code", "data_source": "head_office"},
        {
            "label": "Chambers",
            "id": "firm_name",
            "html_renderer": provider_name_html,
            "data_source": "parent_firm",
            "row_action_urls": {"enter": "main.assign_chambers", "change": "main.assign_chambers"},
        },
        {
            "label": "Barrister level",
            "id": "advocate_level",
            "formatter": format_advocate_level,
            "row_action_urls": {
                "change": {
                    "link": "main.barrister_change_details",
                    "anchor": "barrister_level",
                },
                "enter": {
                    "link": "main.barrister_change_details",
                    "anchor": "barrister_level",
                },
            },
        },
        {
            "label": "Bar Council roll number",
            "id": "bar_council_roll",
            "row_action_urls": {
                "change": {
                    "link": "main.barrister_change_details",
                    "anchor": "bar_council_roll_number",
                },
                "enter": {
                    "link": "main.barrister_change_details",
                    "anchor": "bar_council_roll_number",
                },
            },
        },
    ],
    "Advocate": [
        {
            "label": "Advocate name",
            "id": "firm_name",
            "row_action_urls": {
                "change": {"link": "main.change_advocate_details", "anchor": "advocate_name"},
                "enter": {"link": "main.change_advocate_details", "anchor": "advocate_name"},
            },
        },
        {"label": "Advocate number", "id": "firm_number"},
        {"label": "Account number", "id": "firm_office_code", "data_source": "head_office"},
        {
            "label": "Chambers",
            "id": "firm_name",
            "html_renderer": provider_name_html,
            "data_source": "parent_firm",
            "row_action_urls": {"enter": "main.assign_chambers", "change": "main.assign_chambers"},
        },
        {
            "label": "Advocate level",
            "id": "advocate_level",
            "formatter": format_advocate_level,
            "row_action_urls": {
                "change": {"link": "main.change_advocate_details", "anchor": "advocate_level"},
                "enter": {"link": "main.change_advocate_details", "anchor": "advocate_level"},
            },
        },
        {
            "label": "Solicitors Regulation Authority roll number",
            "id": "bar_council_roll",
            "row_action_urls": {
                "change": {"link": "main.change_advocate_details", "anchor": "sra_roll_number"},
                "enter": {"link": "main.change_advocate_details", "anchor": "sra_roll_number"},
            },
        },
    ],
}
