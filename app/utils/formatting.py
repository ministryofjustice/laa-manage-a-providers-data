from datetime import datetime
from typing import Optional

from app.constants import CONSTITUTIONAL_STATUS_CHOICES, PROVIDER_TYPE_CHOICES


def format_provider_type(provider_type: str) -> str:
    """Format provider type for display"""
    if not provider_type:
        return ""

    choices_dict = dict(PROVIDER_TYPE_CHOICES)
    return choices_dict.get(provider_type.lower(), provider_type.title())


def format_constitutional_status(status: str) -> str:
    """Format constitutional status for display"""
    if not status:
        return ""

    choices_dict = dict(CONSTITUTIONAL_STATUS_CHOICES)
    return choices_dict.get(status.lower(), status.title())


def format_date(date_string: Optional[str]) -> str:
    """Format ISO date string for display"""
    if not date_string:
        return ""

    try:
        # Parse ISO format date
        date_obj = datetime.fromisoformat(date_string)
        # Format as DD/MM/YYYY
        return date_obj.strftime("%d/%m/%Y")
    except (ValueError, AttributeError):
        # If it's not a valid ISO date, return as-is
        return date_string


def format_yes_no(value: Optional[str]) -> str:
    """Format Yes/No values consistently"""
    if not value:
        return ""

    if value.lower() in ["yes", "true", "1"]:
        return "Yes"
    elif value.lower() in ["no", "false", "0"]:
        return "No"
    return value
