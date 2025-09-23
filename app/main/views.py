import logging
from typing import Dict, List, Literal, NoReturn

from flask import abort, current_app, redirect, render_template, request, url_for
from flask.views import MethodView

from app.components.tables import Card, DataTable, SummaryList, TableStructureItem
from app.main.forms import firm_name_html, get_firm_statuses
from app.main.utils import create_provider_from_session
from app.models import BankAccount, Firm, Office
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


def get_contact_tables(firm: Firm, head_office: Office = None) -> list[DataTable]:
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
        card_title = f"{contact.first_name} {contact.last_name}"
        card: Card = {
            "title": card_title,
        }

        if contact in primary_contacts:
            # Only the primary contact card has the action to change the Liaison Manager
            card.update(
                {
                    "action_text": "Change liaison manager",
                    "action_url": url_for("main.add_new_liaison_manager", firm=firm),
                }
            )

        contact_table = SummaryList(card=card)

        contact_table.add_row(contact.job_title, "Job title")
        contact_table.add_row(contact.telephone_number, "Telephone number")
        contact_table.add_row(contact.email_address, "Email address")
        contact_table.add_row(contact.website, "Website")
        contact_table.add_row(contact.active_from, "Active from", format_date)

        contact_tables.append(contact_table)

    return contact_tables


def provider_name_html(provider: Firm):
    return (
        f"<a class='govuk-link', href={url_for('main.view_provider', firm=provider.firm_id)}>{provider.firm_name}</a>"
    )


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

    def get_main_table(self, firm, head_office, parent_provider) -> DataTable:
        main_table = SummaryList()

        main_table.add_row(firm.firm_name, "Provider name")
        main_table.add_row(firm.firm_number, "Provider number")

        if head_office:
            main_table.add_row(head_office.firm_office_code, "Account number")

        if parent_provider:
            main_table.add_row(
                parent_provider.firm_name,
                "Parent provider name",
                html=provider_name_html(parent_provider),
            )
            main_table.add_row(parent_provider.firm_number, "Parent provider number")

        # Additional data

        if firm.firm_type == "Legal Services Provider":
            # Show these fields even without entries, so they can always be changed
            main_table.add_row(
                firm.indemnity_received_date if firm.indemnity_received_date not in (None, "") else "Not provided",
                "Indemnity received date",
                format_date,
            )
            main_table.add_row(
                firm.company_house_number if firm.company_house_number not in (None, "") else "Not provided",
                "Companies House number",
            )

        main_table.add_row(
            firm.constitutional_status,
            "Constitutional status",
            format_constitutional_status,
        )
        if firm.firm_type != "Legal Services Provider":
            main_table.add_row(firm.indemnity_received_date, "Indemnity received date", format_date)
        main_table.add_row(firm.non_profit_organisation, "Not for profit organisation", format_yes_no)
        main_table.add_row(firm.solicitor_advocate, "Solicitor advocate", format_yes_no)
        main_table.add_row(firm.advocate_level, "Advocate level", format_advocate_level)
        if firm.firm_type != "Legal Services Provider":
            main_table.add_row(firm.company_house_number, "Companies House number")
        main_table.add_row(firm.bar_council_roll, "Bar Council roll number")
        main_table.add_row(firm.contract_manager, "Contract manager")

        return main_table if main_table.is_populated else None

    def get_office_tables(self, firm, head_office: Office, other_offices: list[Office]) -> dict[str, DataTable]:
        """Gets two data tables one for the main office and one for other offices."""
        office_tables = {}

        def firm_office_html(row_data: dict[str, str]) -> str:
            # Renders the office account number as a link
            _office_code = row_data.get("firm_office_code", "")
            return f"<a class='govuk-link' href='{url_for('main.view_office', firm=firm.firm_id, office=_office_code)}'>{_office_code}</a>"

        office_table_structure: list[TableStructureItem] = [
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

    def get_chambers_contact_details_table(self, firm, head_office: Office) -> SummaryList:
        """Gets information about the chambers head office"""
        table = SummaryList()

        table.add_row(
            "test",
            "Address",
            html=format_office_address_multi_line_html(head_office),
        )
        table.add_row(head_office.email_address, "Email address")
        table.add_row(head_office.telephone_number, "Telephone number")
        table.add_row(head_office.dx_number, "DX number")
        table.add_row(head_office.dx_centre, "DX centre")
        
        return table

    @staticmethod
    def get_account_number_or_default(account_number: str | None) -> str:
        """
        Renders the office account number, defaulting to "Unknown" if no account number is provided.
        """
        if account_number not in (None, ""):
            return account_number
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

        columns: list[TableStructureItem] = [
            {"text": "Name", "id": "firm_name", "html_renderer": firm_name_html},
            {"text": "Account number", "id": "account_number", "format_text": self.get_account_number_or_default},
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

        columns: list[TableStructureItem] = [
            {"text": "Name", "id": "firm_name", "html_renderer": firm_name_html},
            {"text": "Account number", "id": "account_number", "format_text": self.get_account_number_or_default},
            {"text": "Solicitors Regulation Authority roll number", "id": "bar_council_roll"},
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

            context.update({"contact_tables": get_contact_tables(firm, head_office)})
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

    def __init__(self, subpage: Literal["overview", "contact", "bank-payment-details"] = "overview"):
        if subpage:
            self.subpage = subpage

    def get_payment_information_table(self, firm: Firm, office: Office) -> DataTable:
        table = SummaryList()
        table.add_row(value=None, label="Payment method", row_action_urls={"enter": "#", "change": "#"})
        return table

    def get_vat_registration_table(self, firm: Firm, office: Office) -> DataTable:
        table = SummaryList()
        table.add_row(
            value=office.vat_registration_number,
            label="VAT registration number",
            row_action_urls={"enter": "#", "change": "#"},
        )
        return table

    def get_office_overview_table(self, firm: Firm, office: Office) -> DataTable:
        table = SummaryList()
        table.add_row(firm.firm_name, "Parent provider", html=provider_name_html(firm))
        table.add_row(office.firm_office_code, "Account number")
        table.add_row(office.head_office, "Head office", format_head_office)
        table.add_row(firm.firm_type, "Supplier type", format_firm_type)
        return table

    def get_bank_account_table(self, bank_account: BankAccount) -> DataTable | None:
        if bank_account is None:
            return None

        card: Card = {"title": bank_account.bank_account_name, "action_text": "Change bank account", "action_url": "#"}
        table = SummaryList(card=card)
        table.add_row(bank_account.bank_account_name, "Account name")
        table.add_row(bank_account.account_number, "Account number")
        table.add_row(bank_account.sort_code, "Sort code")
        # Effective date from still to be implemented
        return table

    def get_context(self, firm: Firm, office: Office) -> Dict:
        context = {"firm": firm, "office": office, "subpage": self.subpage}

        if self.subpage == "bank-payment-details":
            pda = current_app.extensions["pda"]
            bank_account: BankAccount = pda.get_office_bank_account(
                firm_id=firm.firm_id, office_code=office.firm_office_code
            )
            context.update(
                {
                    "vat_registration_table": self.get_vat_registration_table(firm, office),
                    "payment_information_table": self.get_payment_information_table(firm, office),
                    "bank_account_table": self.get_bank_account_table(bank_account),
                }
            )

        if self.subpage == "contact":
            context.update({"contact_tables": get_contact_tables(firm, office)})

        if self.subpage == "overview":
            context.update({"overview_table": self.get_office_overview_table(firm, office)})

        return context

    def get(self, firm: Firm, office: Office | None = None):
        if not firm or not office:
            abort(404)

        context = self.get_context(firm, office)

        return render_template(self.template, **context)
