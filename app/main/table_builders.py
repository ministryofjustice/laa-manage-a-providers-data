import datetime
import logging
from collections.abc import Callable
from typing import List

from flask import current_app, url_for

from app.components.tables import Card, DataTable, SummaryList
from app.constants import DISPLAY_DATE_FORMAT, STATUS_CONTRACT_MANAGER_DEFAULT, STATUS_CONTRACT_MANAGER_NAMES
from app.main.constants import MAIN_TABLE_FIELD_CONFIG, STATUS_TABLE_FIELD_CONFIG
from app.main.utils import provider_name_html
from app.models import BankAccount, Contact, Firm, Office
from app.utils.formatting import (
    format_date,
    format_firm_type,
    format_head_office,
    format_office_address_multi_line_html,
)

logger = logging.getLogger(__name__)


def _add_table_row_from_config(table: SummaryList, field: dict, data_source: dict, row_action_urls: dict = None):
    """
    Helper to add a row to a SummaryList table based on field configuration.

    Args:
        table: SummaryList to add row to
        field: Field configuration dict with label, id, formatter, html_renderer, text_renderer, etc.
        data_source: Data dict to extract values from
        row_action_urls: Optional row action URLs dict
    """
    # Skip row if visible callable returns False
    if field.get("visible", None):
        visible_callable: Callable = field.get("visible")
        if not visible_callable(data_source):
            return

    # Get value using text_renderer if provided, otherwise extract by id
    value = None
    if text_renderer := field.get("text_renderer"):
        if not isinstance(text_renderer, Callable):
            raise ValueError("text_renderer must be callable")
        value = text_renderer(data_source)
    elif field_id := field.get("id"):
        value = data_source.get(field_id)

    if value_preprocessor := field.get("value_preprocessor"):
        if not isinstance(value_preprocessor, Callable):
            raise ValueError("value_preprocessor must be callable")
        value = value_preprocessor(value)

    # Skip row if hide_if_null is set and value is empty
    if not value and field.get("hide_if_null", False):
        return

    # Get HTML if html_renderer is provided
    html_content = None
    if html_renderer := field.get("html_renderer"):
        if not isinstance(html_renderer, Callable):
            raise ValueError("html_renderer must be callable")
        html_content = html_renderer(data_source)

    # Add the row
    table.add_row(
        label=field.get("label"),
        value=value,
        formatter=field.get("formatter"),
        html=html_content,
        row_action_urls=row_action_urls,
        default_value=field.get("default", "No data"),
    )


def get_main_table(firm: Firm, head_office: Office | None, parent_firm: Firm | None) -> SummaryList:
    """Creates the main overview table for a firm."""
    data_source_map = {
        "firm": firm.to_internal_dict() if firm else {},
        "head_office": head_office.to_internal_dict() if head_office else {},
        "parent_firm": parent_firm.to_internal_dict() if parent_firm else {},
    }
    main_table = SummaryList()

    # Add firm type specific fields
    for field in MAIN_TABLE_FIELD_CONFIG.get(firm.firm_type, []):
        data_source = data_source_map.get(field.get("data_source", "firm"))
        if data_source is None:
            raise ValueError(f"{field.get('data_source', 'firm')} is not a valid data source")

        row_action_urls: dict = field.get("row_action_urls", None)
        # If we have row actions, replace endpoints with generated URLs
        if row_action_urls:
            for action_key, endpoint in row_action_urls.items():
                try:
                    url = url_for(endpoint, firm=firm.firm_id)
                    row_action_urls[action_key] = url
                except Exception as e:
                    logger.error(f"{e.__class__.__name__} whilst generating a url for ({action_key}) {endpoint}: {e}")

        _add_table_row_from_config(main_table, field, data_source, row_action_urls)

    return main_table


def get_status_table(entity: Firm | Office, firm: Firm | None = None, office: Office | None = None) -> SummaryList:
    """
    Creates a status table for an entity (firm or office).

    Args:
        entity: The Firm or Office entity
        firm: Firm object (required for office entities to generate change links)
        office: Office object (required for office entities to generate change links)
    """

    def _get_change_url(field: dict, entity: Firm | Office) -> str:
        change_link = field.get("change_link")
        # TODO: Temporary logic to always show a change link even when not all change pages have been built, remove this when all modification pages have been built
        if not change_link:
            return "#"
        # Generate the change URL based on entity type
        if entity_type == "Office" and firm and office:
            return url_for(change_link, firm=firm.firm_id, office=office.firm_office_code)
        elif entity_type != "Office" and isinstance(entity, Firm):
            return url_for(change_link, firm=entity)
        else:
            return url_for(change_link)

    entity_data = entity.to_internal_dict() if entity else {}

    # Determine entity type automatically using isinstance and firm_type
    if isinstance(entity, Firm):
        entity_type = entity.firm_type
    elif isinstance(entity, Office):
        entity_type = "Office"
    else:
        raise ValueError(f"Entity must be Firm or Office, got {type(entity)}")

    status_table = SummaryList()

    _all_fields = STATUS_TABLE_FIELD_CONFIG.get(entity_type, [])

    # Add entity type specific status fields
    for field in _all_fields:
        change_url = _get_change_url(field, entity)

        row_action_urls = {"change": change_url}

        _add_table_row_from_config(status_table, field, entity_data, row_action_urls)

    return status_table


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


def get_sorted_office_bank_accounts(firm: Firm, office: Office = None) -> List[BankAccount]:
    pda = current_app.extensions["pda"]
    bank_accounts = pda.get_office_bank_accounts(firm_id=firm.firm_id, office_code=office.firm_office_code)
    primary_bank_accounts = [bank_account for bank_account in bank_accounts if bank_account.primary_flag.lower() == "y"]
    other_bank_accounts = [bank_account for bank_account in bank_accounts if bank_account.primary_flag.lower() == "n"]
    primary_bank_accounts.sort(key=lambda bank_account: bank_account.start_date)
    other_bank_accounts.sort(key=lambda bank_account: bank_account.end_date, reverse=True)
    return primary_bank_accounts + other_bank_accounts


def get_bank_account_tables(firm: Firm, office: Office, action_url="#") -> List[DataTable]:
    bank_accounts = get_sorted_office_bank_accounts(firm, office)
    bank_accounts_table = []
    for bank_account in bank_accounts:
        card: Card = {
            "title": bank_account.bank_account_name,
            "classes": f"bank-account-table bank-account-table-primary-flag-{bank_account.primary_flag.lower()}",
        }

        if bank_account.primary_flag.lower() == "y":
            # Only the primary bank account has the action to change the bank account link
            card.update(
                {
                    "action_text": "Change bank account",
                    "action_url": action_url,
                }
            )

        bank_account_table = SummaryList(
            card=card,
        )
        bank_account_table.add_row("Account name", bank_account.bank_account_name)
        bank_account_table.add_row("Account number", bank_account.account_number)
        bank_account_table.add_row("Sort code", bank_account.sort_code)
        dt = bank_account.start_date
        if isinstance(dt, datetime.date):
            dt = dt.strftime(DISPLAY_DATE_FORMAT)
        bank_account_table.add_row("Effective date from", dt)

        dt = bank_account.end_date
        if isinstance(dt, datetime.date):
            dt = dt.strftime(DISPLAY_DATE_FORMAT)
        if dt:
            bank_account_table.add_row("Effective date to", dt)

        bank_accounts_table.append(bank_account_table)
    return bank_accounts_table


def get_contact_tables(
    firm: Firm, head_office: Office = None, include_change_link=True, changing_office: bool = False
) -> list[DataTable]:
    sorted_contacts = get_sorted_contacts(firm, head_office)
    if not sorted_contacts:
        return []

    contact_tables = []

    for contact in sorted_contacts:
        card_title = f"{contact.first_name} {contact.last_name}"
        card: Card = {
            "title": card_title,
            "classes": f"liaison-manager-card liaison-manager-card-primary-{contact.primary.lower()}",
        }

        if contact.primary == "Y" and include_change_link:
            if changing_office:
                action_url = url_for("main.add_new_office_liaison_manager", firm=firm, office=head_office)
            else:
                action_url = url_for("main.add_new_liaison_manager", firm=firm)
            # Only the primary contact card has the action to change the Liaison Manager
            card.update(
                {
                    "action_text": "Change liaison manager",
                    "action_url": action_url,
                }
            )

        contact_table = SummaryList(card=card)

        contact_table.add_row("Job title", contact.job_title)
        contact_table.add_row("Telephone number", contact.telephone_number)
        contact_table.add_row("Email address", contact.email_address)
        contact_table.add_row("Website", contact.website)
        contact_table.add_row("Active from", contact.creation_date, format_date)

        if contact.inactive_date:
            contact_table.add_row("Active to", contact.inactive_date, format_date)

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
    if firm.is_advocate or firm.is_barrister:
        url = url_for("main.add_office_vat_number", firm=firm)
    else:
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
    if (
        office.contract_manager not in STATUS_CONTRACT_MANAGER_NAMES
        or office.contract_manager == STATUS_CONTRACT_MANAGER_DEFAULT
    ):
        table.add_row("Contract manager", office.contract_manager)
    return table


def get_office_contact_table(firm: Firm, office: Office) -> DataTable | None:
    """
    Gets a DataTable for the primary contact for the specified office.

    If the office has multiple primary contacts, the
    """
    office_contact_table = SummaryList()
    office_contact_table.add_row(
        label="Address",
        html=format_office_address_multi_line_html(office),
        row_action_urls={
            "enter": url_for("main.change_office_contact_details_form", firm=firm, office=office),
            "change": url_for(
                "main.change_office_contact_details_form", firm=firm, office=office, _anchor="address_line_1"
            ),
        },
    )
    office_contact_table.add_row(
        label="Email address",
        value=office.email_address,
        row_action_urls={
            "enter": url_for("main.change_office_contact_details_form", firm=firm, office=office),
            "change": url_for(
                "main.change_office_contact_details_form", firm=firm, office=office, _anchor="email_address"
            ),
        },
    )

    office_contact_table.add_row(
        label="Telephone number",
        value=office.telephone_number,
        row_action_urls={
            "enter": url_for("main.change_office_contact_details_form", firm=firm, office=office),
            "change": url_for(
                "main.change_office_contact_details_form", firm=firm, office=office, _anchor="telephone_number"
            ),
        },
    )

    office_contact_table.add_row(
        label="DX number",
        value=office.dx_number,
        row_action_urls={
            "enter": url_for("main.change_office_contact_details_form", firm=firm, office=office, _anchor="dx_number"),
            "change": url_for("main.change_office_contact_details_form", firm=firm, office=office, _anchor="dx_number"),
        },
    )
    office_contact_table.add_row(
        label="DX centre",
        value=office.dx_centre,
        row_action_urls={
            "enter": url_for("main.change_office_contact_details_form", firm=firm, office=office, _anchor="dx_centre"),
            "change": url_for("main.change_office_contact_details_form", firm=firm, office=office, _anchor="dx_centre"),
        },
    )
    return office_contact_table
