import html
import json

from flask import current_app, flash, session

from app.models import BankAccount, Firm, Office
from app.pda.mock_api import MockProviderDataApi


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

    return firm
