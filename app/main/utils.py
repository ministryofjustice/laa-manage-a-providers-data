import html
import json
from datetime import date

from flask import current_app, flash, session

from app.models import BankAccount, Contact, Firm, Office
from app.pda.mock_api import MockProviderDataApi, ProviderDataApiError


def get_full_info_html(data):
    formatted_json = html.escape(json.dumps(data, indent=2))
    html_content = f"""
    <details class="govuk-details">
      <summary class="govuk-details__summary">
        <span class="govuk-details__summary-text">
            JSON
        </span>
      </summary>
      <div class="govuk-details__text">
        <pre style="background-color: #f3f4f6; padding: 10px; border-radius: 4px; overflow-x: auto;">{formatted_json}</pre>
      </div>
    </details>
    """
    return html_content


def add_new_provider(firm: Firm, show_success_message: bool = True) -> Firm:
    """Adds a new provider to the PDA, currently only the mock PDA supports this functionality."""

    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    if not isinstance(pda, MockProviderDataApi):
        raise RuntimeError("Provider Data API does not support this functionality yet.")

    new_firm: Firm = pda.create_provider_firm(firm)

    if show_success_message:
        firm_type: str = new_firm.firm_type.lower()
        flash(f"<b>New {firm_type} successfully created</b>", "success")

    return new_firm


def add_new_office(office: Office, firm_id: int, show_success_message: bool = True) -> Office:
    """Adds a new office to the PDA, currently only the mock PDA supports this functionality."""

    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    if not isinstance(pda, MockProviderDataApi):
        raise RuntimeError("Provider Data API does not support this functionality yet.")

    new_office = pda.create_provider_office(office, firm_id=firm_id)

    if show_success_message:
        flash(f"<b>New office {new_office.firm_office_code} successfully created</b>", "success")

    return new_office


def add_new_bank_account(
    bank_account: BankAccount, firm_id: int, office_code: str, show_success_message: bool = True
) -> BankAccount:
    """Adds a new bank account to an office in the PDA, currently only the mock PDA supports this functionality."""

    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    if not isinstance(pda, MockProviderDataApi):
        raise RuntimeError("Provider Data API does not support this functionality yet.")

    new_bank_account = pda.create_office_bank_account(firm_id, office_code, bank_account)

    if show_success_message:
        flash(f"<b>Bank account successfully created for office {office_code}</b>", "success")

    return new_bank_account


def add_new_contact(contact: Contact, firm_id: int, office_code: str, show_success_message: bool = True) -> Contact:
    """Adds a new contact to an office in the PDA, currently only the mock PDA supports this functionality."""

    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    if not isinstance(pda, MockProviderDataApi):
        raise RuntimeError("Provider Data API does not support this functionality yet.")

    new_contact = pda.create_office_contact(firm_id, office_code, contact)

    if show_success_message:
        flash(f"<b>Contact successfully created for office {office_code}</b>", "success")

    return new_contact


def change_liaison_manager(contact: Contact, firm_id: int, show_success_message: bool = True) -> Contact:
    """Change the liaison manager for ALL offices of a firm, making the new contact primary across the firm.

    Creates a new contact record for each office of the firm, making the new person the primary
    liaison manager for every office. All existing liaison managers across all offices become non-primary.

    Args:
        contact: Contact model instance for the new liaison manager
        firm_id: The firm ID
        show_success_message: Whether to show a success flash message (default: True)

    Returns:
        Contact: The contact record for the head office (or first office found if no head office)

    Raises:
        RuntimeError: If Provider Data API not initialized
        ValueError: If firm_id is not a positive integer
        ProviderDataApiError: If firm doesn't exist or has no offices
        NotImplementedError: If the API doesn't support contact management yet
    """
    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    if not isinstance(firm_id, int) or firm_id <= 0:
        raise ValueError("firm_id must be a positive integer")

    # Get all offices for this firm
    firm_offices = pda.get_provider_offices(firm_id)
    if not firm_offices:
        raise ProviderDataApiError(f"No offices found for firm {firm_id}")

    # Find head office for return value (use first office as fallback)
    head_office = pda.get_head_office(firm_id)
    return_office = head_office or firm_offices[0]

    # Set all existing liaison managers to non-primary across all offices
    for office in firm_offices:
        contacts = pda.get_office_contacts(firm_id, office.firm_office_code)
        for existing_contact in contacts:
            if existing_contact.job_title == "Liaison manager" and existing_contact.primary == "Y":
                # Set this contact to non-primary
                updated_contact = existing_contact.model_copy(update={"primary": "N"})
                pda.update_contact(firm_id, office.firm_office_code, updated_contact)

    # Create new primary liaison manager contact for each office
    contacts_by_office_id = {}
    for office in firm_offices:
        contact_updates = {
            "vendor_site_id": office.firm_office_id,
            "job_title": "Liaison manager",
            "primary": "Y",
            "active_from": date.today().isoformat(),
        }

        office_contact = contact.model_copy(update=contact_updates)
        created_contact = pda.create_office_contact(firm_id, office.firm_office_code, office_contact)
        contacts_by_office_id[office.firm_office_id] = created_contact

    # Return the contact for the head office (or first office)
    return_contact = contacts_by_office_id[return_office.firm_office_id]

    if show_success_message:
        flash(f"<b>{return_contact.first_name} {return_contact.last_name} is the new liaison manager</b>", "success")

    return return_contact


def create_provider_from_session() -> Firm | None:
    """Create a new provider, office, and bank account from session data."""
    firm_data = session.get("new_provider")
    if not firm_data:
        return None

    # Clean up session and create firm
    del session["new_provider"]
    firm = add_new_provider(Firm(**firm_data))

    # Create head office if data exists
    if office_data := session.get("new_head_office"):
        del session["new_head_office"]

        # Create the office
        new_office = add_new_office(
            Office(**office_data), firm_id=firm.firm_id, show_success_message=False
        )  # Don't show success message as head office is created at the same time as the provider.

        # Create bank account if data exists in separate session key
        if bank_account_data := session.get("new_head_office_bank_account"):
            del session["new_head_office_bank_account"]

            bank_account = BankAccount(**bank_account_data)
            add_new_bank_account(
                bank_account,
                firm_id=firm.firm_id,
                office_code=new_office.firm_office_code,
                show_success_message=False,
            )

        # Create liaison manager contact if data exists
        if liaison_manager_data := session.get("new_liaison_manager"):
            del session["new_liaison_manager"]

            contact = Contact(**liaison_manager_data)
            add_new_contact(
                contact,
                firm_id=firm.firm_id,
                office_code=new_office.firm_office_code,
                show_success_message=False,
            )

    return firm


def create_barrister_from_form_data(
    barrister_name: str, barrister_level: str, bar_council_roll_number: str, parent_firm_id: int
) -> Firm:
    """Create a new barrister provider from form data."""
    firm_data = {
        "firm_name": barrister_name,
        "firm_type": "Barrister",
        "solicitor_advocate": "No",
        "advocate_level": barrister_level,
        "bar_council_roll": bar_council_roll_number,
        "parent_firm_id": parent_firm_id,
    }

    firm = Firm(**firm_data)
    new_firm = add_new_provider(firm)

    # Create head office with same address as parent chambers
    _create_head_office_from_parent(new_firm.firm_id, parent_firm_id)

    return new_firm


def create_advocate_from_form_data(
    advocate_name: str, advocate_level: str, sra_roll_number: str, parent_firm_id: int
) -> Firm:
    """Create a new advocate provider from form data."""
    firm_data = {
        "firm_name": advocate_name,
        "firm_type": "Advocate",
        "solicitor_advocate": "Yes",
        "advocate_level": advocate_level,
        "bar_council_roll": sra_roll_number,
        "parent_firm_id": parent_firm_id,
    }

    firm = Firm(**firm_data)
    new_firm = add_new_provider(firm)

    # Create head office with same address as parent chambers
    _create_head_office_from_parent(new_firm.firm_id, parent_firm_id)

    return new_firm


def replicate_office_for_child_firm(source_office: Office, new_firm_id: int, as_head_office: bool = True) -> Office:
    """Replicate an office for a child firm using the source office's address details.

    Args:
        source_office: The office to replicate from
        new_firm_id: The ID of the new firm to create the office for
        as_head_office: Whether the new office should be marked as a head office

    Returns:
        New Office object with same address but fresh IDs
    """
    # Fields to exclude when replicating (will be auto-generated or set differently)
    exclude_fields = {
        "firm_office_id",
        "ccms_firm_office_id",
        "firm_office_code",
        "creation_date",  # Should be current date for new office
    }

    # Get all office data
    office_data = source_office.to_internal_dict()

    # Remove excluded fields
    for field in exclude_fields:
        office_data.pop(field, None)

    # Set head office status based on parameter
    if as_head_office:
        office_data["head_office"] = "N/A"
        office_data["is_head_office"] = True
    else:
        office_data["is_head_office"] = False

    # Create new office
    new_office = Office(**office_data)
    return add_new_office(new_office, firm_id=new_firm_id, show_success_message=False)


def _create_head_office_from_parent(new_firm_id: int, parent_firm_id: int) -> Office:
    """Create a head office for a new barrister/advocate using the parent chambers' head office address and contacts."""
    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    # Get the parent firm's head office
    parent_offices = pda.get_provider_offices(parent_firm_id)
    parent_head_office = None

    for office in parent_offices:
        if office.get_is_head_office():
            parent_head_office = office
            break

    if not parent_head_office:
        raise RuntimeError(f"No head office found for parent firm {parent_firm_id}")

    # Create the new office
    new_office = replicate_office_for_child_firm(parent_head_office, new_firm_id, as_head_office=True)

    # Copy contacts from parent office to new office
    _replicate_office_contacts(
        parent_firm_id, parent_head_office.firm_office_code, new_firm_id, new_office.firm_office_code
    )

    return new_office


def _replicate_office_contacts(
    source_firm_id: int, source_office_code: str, target_firm_id: int, target_office_code: str
) -> list[Contact]:
    """Replicate contacts from a source office to a target office."""
    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    # Get contacts from source office
    source_contacts = pda.get_office_contacts(source_firm_id, source_office_code)

    if not source_contacts:
        return []

    replicated_contacts = []

    for contact in source_contacts:
        # Copy contact data, excluding fields that should be fresh for new office
        contact_data = contact.to_internal_dict()
        contact_data.pop("vendor_site_id", None)  # Will be set to new office ID

        # Create new contact for target office
        new_contact = Contact(**contact_data)
        replicated_contact = add_new_contact(
            new_contact, firm_id=target_firm_id, office_code=target_office_code, show_success_message=False
        )
        replicated_contacts.append(replicated_contact)

    return replicated_contacts
