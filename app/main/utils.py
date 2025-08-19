import html
import json

from flask import current_app, flash

from app.models import Firm
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


def add_new_provider(firm: Firm) -> Firm:
    """Adds a new provider to the PDA, currently only the mock PDA supports this functionality."""

    pda = current_app.extensions.get("pda")
    if not pda:
        raise RuntimeError("Provider Data API not initialized")

    if not isinstance(pda, MockProviderDataApi):
        raise RuntimeError("Provider Data API does not support this functionality yet.")

    new_firm = pda.create_provider_firm(firm)
    flash("<b>New provider successfully created</b>", "success")
    return new_firm
