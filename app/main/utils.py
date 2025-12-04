import html
import json
import logging
from datetime import date

from flask import current_app, flash, session, url_for

from app.components.tag import Tag, TagType
from app.constants import (
    STATUS_CONTRACT_MANAGER_DEBT_RECOVERY,
    STATUS_CONTRACT_MANAGER_DEFAULT,
    STATUS_CONTRACT_MANAGER_NAMES,
)
from app.models import BankAccount, Contact, Firm, Office
from app.pda.errors import ProviderDataApiError
from app.pda.mock_api import MockProviderDataApi
from app.utils.formatting import format_date

logger = logging.getLogger(__name__)


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


def provider_name_html(provider: Firm | dict):
    if isinstance(provider, Firm):
        _firm_id = provider.firm_id
        _firm_name = provider.firm_name
    elif isinstance(provider, dict):
        _firm_id = int(provider.get("firm_id") or provider.get("advocate_number") or provider.get("barrister_number"))
        _firm_name = provider.get("firm_name") or provider.get("advocate_name") or provider.get("barrister_name")
    else:
        raise ValueError(f"Provider {provider} must be a Provider or dict")
    return f"<a class='govuk-link', href={url_for('main.view_provider', firm=_firm_id)}>{_firm_name}</a>"


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


def change_liaison_manager(
    contact: Contact, firm_id: int, show_success_message: bool = True, office: Office | None = None
) -> Contact:
    """Change the liaison manager, changing it for ALL offices of a firm if no individual office is specified, or just
     the specified office, making the new contact primary.

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

    if office:
        firm_offices = [
            office,
        ]
        head_office = office
    else:
        # Get all offices for this firm
        firm_offices = pda.get_provider_offices(firm_id)
        head_office = pda.get_head_office(firm_id)

    if not firm_offices:
        raise ProviderDataApiError(f"No offices found for firm {firm_id}")

    # Use head office for return value (or first office as fallback)
    return_office = head_office or firm_offices[0]

    # Set all existing liaison managers to non-primary across all offices
    for office in firm_offices:
        contacts = pda.get_office_contacts(firm_id, office.firm_office_code)
        for existing_contact in contacts:
            if existing_contact.job_title == "Liaison manager" and existing_contact.primary == "Y":
                # Set this contact to non-primary and add inactive_date
                updated_contact = existing_contact.model_copy(
                    update={"primary": "N", "inactive_date": date.today().isoformat()}
                )
                try:
                    pda.update_contact(firm_id, office.firm_office_code, updated_contact)
                except ProviderDataApiError:
                    error_message = (
                        f"Failed to update {existing_contact.job_title} for office {office.firm_office_code}"
                    )
                    logger.error(error_message)
                    flash(error_message, "error")

    # Create new primary liaison manager contact for each office
    contacts_by_office_id = {}
    for office in firm_offices:
        contact_updates = {
            "vendor_site_id": office.firm_office_id,
            "job_title": "Liaison manager",
            "primary": "Y",
            "creation_date": date.today().isoformat(),
        }

        office_contact = contact.model_copy(update=contact_updates)
        try:
            created_contact = pda.create_office_contact(firm_id, office.firm_office_code, office_contact)
            contacts_by_office_id[office.firm_office_id] = created_contact
        except ProviderDataApiError:
            error_message = f"Failed to create {office_contact.job_title} for office {office.firm_office_code}"
            logger.error(error_message)
            flash(error_message, "error")

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
        "advocate_level": barrister_level if barrister_level not in ("None", "N/A") else None,
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
        "advocate_level": advocate_level if advocate_level not in ("None", "N/A") else None,
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

    # Ensure payment method defaults to Electronic for newly created offices for child firms
    office_data["payment_method"] = "Electronic"

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


def get_firm_tags(firm: Firm | dict):
    tags: list[Tag] = []
    if hasattr(firm, "to_internal_dict"):
        firm_data = firm.to_internal_dict()
    elif isinstance(firm, dict):
        firm_data = firm
    else:
        raise TypeError("Firm must be of type dict or Firm")

    if firm_data.get("inactive_date"):
        tags.append(Tag(TagType.INACTIVE))
    if firm_data.get("hold_all_payments_flag", "N") == "Y":
        tags.append(Tag(TagType.ON_HOLD))
    return tags


def get_office_tags(office: Office | dict):
    tags: list[Tag] = []
    if hasattr(office, "to_internal_dict"):
        office_data = office.to_internal_dict()
    elif isinstance(office, dict):
        office_data = office
    else:
        raise TypeError("Office must be of type dict or Office")

    if office_data.get("inactive_date"):
        tags.append(Tag(TagType.INACTIVE))
    if office_data.get("hold_all_payments_flag", "N") == "Y":
        tags.append(Tag(TagType.ON_HOLD))
    return tags


def get_firm_account_number(firm: Firm | int) -> str | None:
    """Gets the account number for a given firm or firm_id.

    A firm's account number is the firm_office_code of that firm's head office.

    Args:
        firm: Either a Firm instance or a firm_id (int)

    Returns:
        The firm's account number (firm_office_code), or None if no head office exists

    Raises:
        RuntimeError: If Provider Data API is not initialized
        ValueError: If firm is neither a Firm instance nor an int
    """
    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    firm_id = firm.firm_id if isinstance(firm, Firm) else firm

    if not isinstance(firm_id, int):
        raise ValueError(f"Expected Firm or firm_id (int), got {type(firm)}")

    head_office = pda.get_head_office(firm_id)
    if not head_office:
        logger.warning(f"Firm {firm_id} does not have a head office, and therefore has no account number.")
        return None

    return head_office.firm_office_code


def assign_firm_to_a_new_chambers(firm: Firm | int, chambers: Firm | int) -> Firm:
    """Assigns an advocate or a barrister to a new chambers.

    Args:
        firm: Firm | int - Firm or firm_id of an advocate or barrister
        chambers: Firm | int - Firm or firm_id of new chambers to assign this firm to

    Returns:
        The updated advocate or barrister

    Raises:
        RuntimeError: If Provider Data API is not initialized
        ValueError: If firm is not an advocate or barrister
        ValueError: If new_chambers is not a Chambers
    """
    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    # Convert int to Firm if necessary
    if isinstance(firm, int):
        firm = pda.get_provider_firm(firm)

    if isinstance(chambers, int):
        chambers = pda.get_provider_firm(chambers)

    # Verify firm is an advocate or barrister
    if firm.firm_type not in ["Advocate", "Barrister"]:
        raise ValueError(f"firm must be an advocate or barrister, got firm_type: {firm.firm_type}")

    # Verify chambers is actually a chambers
    if chambers.firm_type != "Chambers":
        raise ValueError(f"chambers must be a Chambers, got firm_type: {chambers.firm_type}")

    new_provider_dict: dict = pda.patch_provider(firm.firm_id, {"parentFirmId": chambers.firm_id})
    new_provider = Firm(**new_provider_dict)

    flash(f"<b>{new_provider.firm_name} assigned to {chambers.firm_name}</b>", category="success")

    return new_provider


def get_entity_active_text(entity: dict) -> str:
    """Gets the display text for if the entity is active or not.
    If entity is active returns "Yes"
    If entity is inactive returns "Made inactive on [DD/MM/YYYY]"
    """
    if inactive_date := entity.get("inactive_date"):
        return f"Made inactive on {format_date(inactive_date)}"
    return "Yes"


def reassign_head_office(firm: Firm | int, new_head_office: Office | str) -> Office:
    """
    Updates the specified office to be the new head office, and updates all other provider offices
    to reference the new head office.

    Raises:
        ProviderDataApiError: If there is an issue within the PDA
        RuntimeError: If the PDA is not available
        ValueError: If the provider is a Chambers, or the new head office is already the head office
    """
    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    # Prepare firm and office
    if isinstance(firm, int):
        firm = pda.get_provider_firm(firm)

    if isinstance(new_head_office, str):
        new_head_office = pda.get_provider_office(new_head_office)

    # Validation
    if firm.firm_type == "Chambers":
        raise ValueError("Cannot assign a head office to a Chambers")

    if new_head_office.head_office == "N/A":
        raise ValueError(f"{new_head_office.firm_office_code} is already the head office")

    # Prepare the fields to be changed...
    # ...the head office does not point to any other office...
    make_head_office_data = {
        Office.model_fields["head_office"].alias: "N/A",
    }
    # ...and other offices point to the head office.
    reassign_head_office_data = {
        Office.model_fields["head_office"].alias: new_head_office.firm_office_code,
    }

    # Iterate through all of the provider's offices, updating them as head or sub offices
    offices = pda.get_provider_offices(firm.firm_id)
    for office in offices:
        if office.firm_office_code == new_head_office.firm_office_code:
            fields_to_update = make_head_office_data
        else:
            fields_to_update = reassign_head_office_data
        try:
            pda.patch_office(
                firm_id=firm.firm_id, office_code=office.firm_office_code, fields_to_update=fields_to_update
            )
        except ProviderDataApiError as e:
            logger.error(f"{e.__class__.__name__} whilst updating office {office.firm_office_code}: {e}")
            flash(f"Failed to update office {office.firm_office_code}", category="error")

    return pda.get_head_office(firm.firm_id)


def contract_manager_nonstatus_name(value: str | dict | Office) -> str | None:
    """
    Returns the contract manager name if it can be displayed, or None if it is one of the status workaround names.

    Parameters:
        entity: Can be the contract manager name, an office, or a dict with the 'contract_manager' key

    Returns:
        str unchanged contract manager name or None if the contract manager name is a status workaround
    """
    contract_manager = value
    if hasattr(value, "contract_manager"):
        contract_manager = value.contract_manager
    elif isinstance(value, dict):
        contract_manager = value.get("contract_manager", None)
    return None if contract_manager in STATUS_CONTRACT_MANAGER_NAMES else contract_manager


def contract_manager_changeable(entity: Office | dict | str):
    """
    Determines if the contract manager can be changed as a normal contract manager, returning False if it is one of
    the status workaround names.

    Parameters:
        entity: Can be an office, a dict with the 'contract_manager' key, or the contract manager name.

    Returns:
        bool True if the contract manager can be changed using a normal dialog, False is the contract manager is being
        used as a status workaround
    """
    contract_manager = entity
    if hasattr(entity, "contract_manager"):
        contract_manager = entity.contract_manager
    elif isinstance(entity, dict):
        contract_manager = entity.get("contract_manager", None)
    return contract_manager not in STATUS_CONTRACT_MANAGER_NAMES or contract_manager == STATUS_CONTRACT_MANAGER_DEFAULT


def get_entity_referred_to_debt_recovery_text(entity: dict) -> str:
    contract_manager = entity.get("contract_manager", None)
    if contract_manager is None and "firm_id" in entity:
        pda = current_app.extensions.get("pda")
        if not pda:
            raise RuntimeError("Provider Data API not initialized")
        head_office = pda.get_head_office(entity["firm_id"])
        if head_office:
            logger.warning(f"Firm {entity['firm_id']} does not have a head office")
            contract_manager = head_office.contract_manager

    if contract_manager == STATUS_CONTRACT_MANAGER_DEBT_RECOVERY:
        return "Yes"
    return "No"


def firm_office_url_for(endpoint, firm: Firm, **kwargs) -> str:
    kwargs["firm"] = firm
    if firm.is_advocate or firm.is_barrister:
        if "office" in kwargs:
            del kwargs["office"]

    if "office" in kwargs:
        if not kwargs["office"]:
            # Remove a null office from the url before generating otherwise it will be added as a querystring
            del kwargs["office"]
        else:
            include_office = any(
                ["office" in rule.arguments for rule in current_app.url_map._rules_by_endpoint[endpoint]]
            )
            if not include_office:
                # This endpoint does not take an office argument
                del kwargs["office"]

    return url_for(endpoint, **kwargs)
