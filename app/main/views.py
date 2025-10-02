import logging
from typing import Callable, Dict, List, Literal, NoReturn

from flask import abort, current_app, redirect, render_template, request, url_for
from flask.views import MethodView

from app.components.tables import Card, DataTable, SummaryList, TableStructureItem
from app.main.constants import MAIN_TABLE_FIELD_CONFIG
from app.main.forms import firm_name_html, get_firm_statuses
from app.main.utils import create_provider_from_session, get_firm_tags, get_office_tags, provider_name_html
from app.models import BankAccount, Contact, Firm, Office
from app.utils.formatting import (
    format_date,
    format_firm_type,
    format_head_office,
    format_office_address_multi_line_html,
    format_office_address_one_line,
)
from app.views import BaseFormView

logger = logging.getLogger(__name__)


def get_sorted_contacts(firm: Firm, office: Office = None) -> List[Contact]:
    """
    For the specified office (part of the specified firm), get a list of contacts with
    the contacts marked primary appearing first in the list.
    """
    if not firm.firm_id or not office:
        return []

    pda = current_app.extensions["pda"]
    contacts = pda.get_office_contacts(firm.firm_id, office.firm_office_code)

    if not contacts:
        return []

    # Sort contacts: primary first, then others
    primary_contacts = [c for c in contacts if c.primary == "Y"]
    other_contacts = [c for c in contacts if c.primary != "Y"]
    sorted_contacts = primary_contacts + other_contacts

    return sorted_contacts


def get_contact_tables(firm: Firm, head_office: Office = None) -> list[DataTable]:
    sorted_contacts = get_sorted_contacts(firm, head_office)
    if not sorted_contacts:
        return []

    contact_tables = []

    for contact in sorted_contacts:
        card_title = f"{contact.first_name} {contact.last_name}"
        card: Card = {
            "title": card_title,
        }

        if contact.primary == "Y":
            # Only the primary contact card has the action to change the Liaison Manager
            card.update(
                {
                    "action_text": "Change liaison manager",
                    "action_url": url_for("main.add_new_liaison_manager", firm=firm),
                }
            )

        contact_table = SummaryList(card=card)

        contact_table.add_row("Job title", contact.job_title)
        contact_table.add_row("Telephone number", contact.telephone_number)
        contact_table.add_row("Email address", contact.email_address)
        contact_table.add_row("Website", contact.website)
        contact_table.add_row("Active from", contact.active_from, format_date)

        contact_tables.append(contact_table)

    return contact_tables


def get_payment_information_table(firm: Firm, office: Office) -> DataTable:
    table = SummaryList()
    table.add_row(
        label="Payment method",
        value=office.payment_method,
        row_action_urls={
            "enter": url_for("main.payment_method_form", firm=firm.firm_id, office=office.firm_office_code),
            "change": url_for("main.payment_method_form", firm=firm.firm_id, office=office.firm_office_code),
        },
    )
    return table


def get_vat_registration_table(firm: Firm, office: Office) -> DataTable:
    table = SummaryList()
    url = url_for("main.add_office_vat_number", firm=firm, office=office)
    table.add_row(
        label="VAT registration number",
        value=office.vat_registration_number,
        row_action_urls={"enter": url, "change": url},
    )
    return table


def get_office_overview_table(firm: Firm, office: Office) -> DataTable:
    table = SummaryList()
    table.add_row("Parent provider", firm.firm_name, html=provider_name_html(firm))
    table.add_row("Account number", office.firm_office_code)
    table.add_row("Head office", office.head_office, format_head_office)
    table.add_row("Supplier type", firm.firm_type, format_firm_type)
    return table


def get_bank_account_table(bank_account: BankAccount) -> DataTable | None:
    if bank_account is None:
        return None

    card: Card = {"title": bank_account.bank_account_name, "action_text": "Change bank account", "action_url": "#"}
    table = SummaryList(card=card)
    table.add_row("Account name", bank_account.bank_account_name)
    table.add_row("Account number", bank_account.account_number)
    table.add_row("Sort code", bank_account.sort_code)
    # Effective date from still to be implemented
    return table


def get_office_contact_table(firm: Firm, office: Office) -> DataTable | None:
    """
    Gets a DataTable for the primary contact for the specified office.

    If the office has multiple primary contacts, the
    """
    sorted_contacts = get_sorted_contacts(firm, office)
    if not sorted_contacts:
        return None

    # Take the first contact, which should be either the primary contact or,
    # if there is no primary contact, the next available contact
    contact_to_display = sorted_contacts[0]

    office_contact_table = SummaryList()
    office_contact_table.add_row(
        label="Address",
        html=format_office_address_multi_line_html(office),
        row_action_urls={"enter": "#", "change": "#"},
    )
    office_contact_table.add_row(
        label="Email address", value=contact_to_display.email_address, row_action_urls={"enter": "#", "change": "#"}
    )
    office_contact_table.add_row(
        label="Telephone number",
        value=contact_to_display.telephone_number,
        row_action_urls={"enter": "#", "change": "#"},
    )
    office_contact_table.add_row(
        label="DX number", value=office.dx_number, row_action_urls={"enter": "#", "change": "#"}
    )
    office_contact_table.add_row(
        label="DX centre", value=office.dx_centre, row_action_urls={"enter": "#", "change": "#"}
    )
    return office_contact_table


def get_main_table(firm: Firm, head_office: Office | None, parent_firm: Firm | None) -> SummaryList:
    data_source_map = {
        "firm": firm.to_internal_dict() if firm else {},
        "head_office": head_office.to_internal_dict() if head_office else {},
        "parent_firm": parent_firm.to_internal_dict() if parent_firm else {},
    }
    main_table = SummaryList()

    # Add firm type specific fields
    for field in MAIN_TABLE_FIELD_CONFIG.get(firm.firm_type, []):
        data_source = data_source_map.get(field.get("data_source", "firm"), None)
        if data_source is None:
            raise ValueError(f"{field.get('data_source', 'firm')} is not a valid data source")

        value = data_source.get(field["id"])

        if not value and field.get("hide_if_null", False):
            continue

        if html_renderer := field.get("html_renderer"):
            if not isinstance(html_renderer, Callable):
                raise ValueError("html_renderer must be callable")
            field["html"] = html_renderer(data_source)

        main_table.add_row(
            value=value,
            label=field.get("label"),
            formatter=field.get("formatter"),
            html=field.get("html"),
            default_value=field.get("default", "No data"),
        )

    return main_table


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
        "Advocate": "view-provider-advocate-barrister.html",
        "Barrister": "view-provider-advocate-barrister.html",
    }

    def __init__(
        self, subpage: Literal["contact", "offices", "barristers-advocates", "bank-accounts-payment"] = "contact"
    ):
        if subpage:
            self.subpage = subpage

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

        table.add_row("Address", "test", html=format_office_address_multi_line_html(head_office))
        table.add_row("Email address", head_office.email_address)
        table.add_row("Telephone number", head_office.telephone_number)
        table.add_row("DX number", head_office.dx_number)
        table.add_row("DX centre", head_office.dx_centre)

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

        context = {"firm": firm, "firm_tags": get_firm_tags(firm)}

        if firm.firm_id:
            # Get head office for account number
            head_office: Office = pda.get_head_office(firm.firm_id)
            context.update({"head_office": head_office})

        if firm.parent_firm_id:
            # Get parent provider
            parent_provider: Firm = pda.get_provider_firm(firm.parent_firm_id)
            context.update({"parent_provider": parent_provider})

        main_table = get_main_table(firm, head_office, parent_provider)
        context.update({"main_table": main_table})

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

        if self.subpage == "barristers-advocates":
            context.update({"barristers_table": self.get_barristers_table(firm)})
            context.update({"advocates_table": self.get_advocates_table(firm)})

        if self.subpage == "bank-accounts-payment":
            if head_office:
                bank_account: BankAccount = pda.get_office_bank_account(
                    firm_id=firm.firm_id, office_code=head_office.firm_office_code
                )
                context.update(
                    {
                        "vat_registration_table": get_vat_registration_table(firm, head_office),
                        "payment_information_table": get_payment_information_table(firm, head_office),
                        "bank_account_table": get_bank_account_table(bank_account),
                    }
                )

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

    def get_context(self, firm: Firm, office: Office) -> Dict:
        context = {
            "firm": firm,
            "office": office,
            "subpage": self.subpage,
            "office_tags": get_office_tags(office),
            "add_bank_account_url": url_for("main.search_bank_account", firm=firm, office=office.firm_office_code),
        }

        if self.subpage == "bank-payment-details":
            pda = current_app.extensions["pda"]
            bank_account: BankAccount = pda.get_office_bank_account(
                firm_id=firm.firm_id, office_code=office.firm_office_code
            )
            context.update(
                {
                    "vat_registration_table": get_vat_registration_table(firm, office),
                    "payment_information_table": get_payment_information_table(firm, office),
                    "bank_account_table": get_bank_account_table(bank_account),
                }
            )

        if self.subpage == "contact":
            contact_table = get_office_contact_table(firm, office)
            context.update(
                {
                    "contact_tables": [
                        contact_table,
                    ]
                    if contact_table
                    else None
                }
            )

        if self.subpage == "overview":
            context.update({"overview_table": get_office_overview_table(firm, office)})

        return context

    def change_link_for_payment_method(self, row_data: Dict[str, str]) -> str | None:
        firm_id = row_data.get("firm_id", None)
        office_id = row_data.get("firm_office_id", None)
        existing_payment_method = row_data.get("payment_method", None)
        link_action = "Add" if existing_payment_method in ("", " ", None) else "Change"
        if firm_id and office_id:
            return f"<a class='govuk-link', href='#'>{link_action}</a>"
        return None

    def change_link_for_vat_registration(self, row_data: Dict[str, str]):
        office_id = row_data.get("firm_office_id", None)
        existing_vat_registration = row_data.get("vat_registration_number", None)
        link_action = "Add VAT registration number" if existing_vat_registration in ("", " ", None) else "Change"
        if office_id:
            return f"<a class='govuk-link', href='#'>{link_action}</a>"
        return None

    def get(self, firm: Firm, office: Office | None = None):
        if not firm or not office:
            abort(404)

        context = self.get_context(firm, office)

        return render_template(self.template, **context)
