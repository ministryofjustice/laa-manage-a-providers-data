import logging
from typing import Literal, NoReturn, List, Dict

from flask import abort, current_app, redirect, render_template, request, url_for
from flask.views import MethodView

from app.components.tables import Card, DataTable, TableStructure, TransposedDataTable, add_field
from app.main.forms import firm_name_html, get_firm_statuses
from app.main.utils import create_provider_from_session
from app.models import Firm, Office
from app.utils.formatting import (
    format_advocate_level,
    format_constitutional_status,
    format_date,
    format_firm_type,
    format_head_office,
    format_office_address_multi_line_html,
    format_office_address_one_line,
    format_yes_no,
)
from app.views import BaseFormView

logger = logging.getLogger(__name__)


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
    templates = {
        "Legal Services Provider": "view-provider-legal-services-provider.html",
        "Chambers": "view-provider-chambers.html",
    }

    def __init__(self, subpage: Literal["contact", "offices", "barristers-and-advocates"] = "contact"):
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

        # Additional data

        if firm.firm_type == "Legal Services Provider":
            # Show these fields even without entries, so they can always be changed
            add_field(
                main_rows,
                main_data,
                firm.indemnity_received_date if firm.indemnity_received_date not in (None, "") else "Not provided",
                "Indemnity received date",
                format_date,
            )
            add_field(
                main_rows,
                main_data,
                firm.company_house_number if firm.company_house_number not in (None, "") else "Not provided",
                "Companies House number",
            )

        add_field(
            main_rows,
            main_data,
            firm.constitutional_status,
            "Constitutional status",
            format_constitutional_status,
        )
        if firm.firm_type != "Legal Services Provider":
            add_field(main_rows, main_data, firm.indemnity_received_date, "Indemnity received date", format_date)
        add_field(main_rows, main_data, firm.non_profit_organisation, "Not for profit organisation", format_yes_no)
        add_field(main_rows, main_data, firm.solicitor_advocate, "Solicitor advocate", format_yes_no)
        add_field(main_rows, main_data, firm.advocate_level, "Advocate level", format_advocate_level)
        if firm.firm_type != "Legal Services Provider":
            add_field(main_rows, main_data, firm.company_house_number, "Companies House number")
        add_field(main_rows, main_data, firm.bar_council_roll, "Bar Council roll number")
        add_field(main_rows, main_data, firm.contract_manager, "Contract manager")

        main_table = TransposedDataTable(structure=main_rows, data=main_data) if main_rows else None

        return main_table

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

    def get_chambers_contact_details_table(self, firm, head_office: Office) -> TransposedDataTable:
        """Gets information about the chambers head office"""
        contact_details_table_structure = []
        contact_details_data = {}

        add_field(
            contact_details_table_structure,
            contact_details_data,
            "test",
            "Address",
            html=format_office_address_multi_line_html(head_office),
        )
        add_field(contact_details_table_structure, contact_details_data, head_office.email_address, "Email address")
        add_field(
            contact_details_table_structure, contact_details_data, head_office.telephone_number, "Telephone number"
        )
        add_field(contact_details_table_structure, contact_details_data, head_office.dx_number, "DX number")
        add_field(contact_details_table_structure, contact_details_data, head_office.dx_centre, "DX centre")

        contact_details_table = (
            TransposedDataTable(structure=contact_details_table_structure, data=contact_details_data)
            if contact_details_data
            else None
        )
        return contact_details_table

    def get_contact_tables(self, firm: Firm, head_office: Office = None) -> list[DataTable]:
        if not head_office or not firm.firm_id:
            return []

        # Get contacts for the head office
        pda = current_app.extensions["pda"]
        contacts = pda.get_office_contacts(firm.firm_id, head_office.firm_office_code)

        if not contacts:
            return []

        # Sort contacts: primary first, then others
        primary_contacts = [c for c in contacts if c.primary == "Y"]
        other_contacts = [c for c in contacts if c.primary != "Y"]
        sorted_contacts = primary_contacts + other_contacts

        contact_tables = []

        for contact in sorted_contacts:
            contact_table_structure = []
            contact_data = {}

            add_field(contact_table_structure, contact_data, contact.job_title, "Job title")
            add_field(contact_table_structure, contact_data, contact.telephone_number, "Telephone number")
            add_field(contact_table_structure, contact_data, contact.email_address, "Email address")
            add_field(contact_table_structure, contact_data, contact.website, "Website")
            add_field(contact_table_structure, contact_data, contact.active_from, "Active from", format_date)

            card_title = f"{contact.first_name} {contact.last_name}"
            card: Card = {"title": card_title, "action_text": "Change liaison manager", "action_url": "#"}

            contact_table = TransposedDataTable(structure=contact_table_structure, data=contact_data, card=card)
            contact_tables.append(contact_table)

        return contact_tables

    @staticmethod
    def child_firm_office_html(row_data: dict[str, str]) -> str:
        """
        Renders the office account number as a link using an extra `office_firm` attribute in the data to link to the
        firm.
        """
        _office_code = row_data.get("account_number", "")
        _office_firm = row_data.get("_account_number_firm_id", "")
        if _office_code not in (None, ""):
            return f"<a class='govuk-link' href='{url_for('main.view_office', firm=_office_firm, office=_office_code)}'>{_office_code}</a>"
        return "Unknown"

    def get_child_firm_office_table_data(self, child_firms: List[Firm]) -> List[Dict]:
        """
        Adds the `account_number` to each child, which is taken from the `firm_office_code` value of the head office
        of the child.

        If the child does not have a head office, a warning will be logged and the `account_number` will be empty. For
        the link to the office to work, each child also has `_account_number_firm_id` populated with the child firm id.

        Args:
            child_firms: List of Firms to show in the table
        """
        pda = current_app.extensions["pda"]

        # Aggregate the child firm with its office
        aggregated_data = []
        for child in child_firms:
            child_data = child.to_internal_dict()
            child_head_office = pda.get_head_office(child.firm_id)
            if child_head_office:
                child_data["account_number"] = child_head_office.firm_office_code
                child_data["_account_number_firm_id"] = child.firm_id
            else:
                logger.warning(f"Firm {child.firm_id} does not have a head office.")
                child_data["account_number"] = ""
                child_data["_account_number_firm_id"] = ""

            aggregated_data.append(child_data)

        return aggregated_data

    def get_barristers_table(self, firm: Firm) -> DataTable | None:
        pda = current_app.extensions["pda"]
        child_barristers = pda.get_provider_children(firm_id=firm.firm_id, only_firm_type="Barrister")

        if len(child_barristers) == 0:
            return None

        columns: list[TableStructure] = [
            {"text": "Name", "id": "firm_name", "html_renderer": firm_name_html},
            {"text": "Account number", "id": "account_number", "html_renderer": self.child_firm_office_html},
            {"text": "Bar Council roll number", "id": "bar_council_roll"},
            {"text": "Status", "html_renderer": get_firm_statuses},  # Add status tags here when available.
        ]
        child_firm_office_table_data = self.get_child_firm_office_table_data(child_barristers)
        table = DataTable(structure=columns, data=child_firm_office_table_data)

        return table

    def get_advocates_table(self, firm: Firm) -> DataTable | None:
        pda = current_app.extensions["pda"]
        child_advocates = pda.get_provider_children(firm_id=firm.firm_id, only_firm_type="Advocate")

        if len(child_advocates) == 0:
            return None

        columns: list[TableStructure] = [
            {"text": "Name", "id": "firm_name", "html_renderer": firm_name_html},
            {"text": "Account number", "id": "firm_office_code", "html_renderer": self.child_firm_office_html},
            {"text": "SRA roll number", "id": "bar_council_roll"},
            {"text": "Status", "html_renderer": get_firm_statuses},  # Add status tags here when available.
        ]

        child_firm_office_table_data = self.get_child_firm_office_table_data(child_advocates)
        table = DataTable(structure=columns, data=child_firm_office_table_data)

        return table

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

        context = {"main_table": main_table, "firm": firm}

        if self.subpage == "offices":
            offices = pda.get_provider_offices(firm.firm_id)

            # Remove the head office from the list of offices
            other_offices = list(filter(lambda o: not o.get_is_head_office(), offices))

            office_tables = self.get_office_tables(firm, head_office, other_offices)
            context.update({"office_tables": office_tables})

        if self.subpage == "contact":
            if firm.firm_type == "Chambers" and head_office:
                context.update({"contact_details_table": self.get_chambers_contact_details_table(firm, head_office)})

            context.update({"contact_tables": self.get_contact_tables(firm, head_office)})
            if firm.firm_type == "Chambers" and head_office:
                context.update({"contact_details_table": self.get_chambers_contact_details_table(firm, head_office)})

        if self.subpage == "barristers-and-advocates":
            context.update({"barristers_table": self.get_barristers_table(firm)})
            context.update({"advocates_table": self.get_advocates_table(firm)})

        return context

    def get(self, firm: Firm | None = None):
        if not firm:
            if created_firm := create_provider_from_session():
                return redirect(url_for("main.view_provider", firm=created_firm))
            abort(404)

        context = self.get_context(firm)
        template = self.templates.get(firm.firm_type, "view-provider-legal-services-provider.html")

        return render_template(template, subpage=self.subpage, **context)


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
            overview_rows, overview_data, firm.firm_name, "Parent provider", html=self.parent_provider_name_html(firm)
        )
        add_field(overview_rows, overview_data, office.firm_office_code, "Account number")
        add_field(overview_rows, overview_data, office.head_office, "Head office", format_head_office)
        add_field(overview_rows, overview_data, firm.firm_type, "Supplier type", format_firm_type)

        # Create tables
        overview_table = TransposedDataTable(structure=overview_rows, data=overview_data) if overview_rows else None

        return render_template(self.template, overview_table=overview_table, firm=firm, office=office)
