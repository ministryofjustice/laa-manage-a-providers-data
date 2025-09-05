from datetime import datetime
from typing import Optional

from app.constants import ADVOCATE_LEVEL_CHOICES, CONSTITUTIONAL_STATUS_CHOICES, FIRM_TYPE_CHOICES
from app.models import Office


def format_firm_type(firm_type: str) -> str:
    """Format firm type for display"""
    if not firm_type:
        return ""

    choices_dict = dict(FIRM_TYPE_CHOICES)
    return choices_dict.get(firm_type.lower(), firm_type.title())


def format_constitutional_status(status: str) -> str:
    """Format constitutional status for display"""
    if not status:
        return ""

    choices_dict = dict(CONSTITUTIONAL_STATUS_CHOICES)
    return choices_dict.get(status)


def format_advocate_level(advocate_level: str) -> str:
    """Format advocate level for display"""
    if not advocate_level:
        return ""

    choices_dict = dict(ADVOCATE_LEVEL_CHOICES)
    return choices_dict.get(advocate_level)


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

    if value.lower() in ["yes", "true", "1", "y"]:
        return "Yes"
    elif value.lower() in ["no", "false", "0", "n"]:
        return "No"
    return value


def format_title_case(value: str) -> str:
    """Format title case for display"""
    if not isinstance(value, str):
        return value
    return value.title()


def format_head_office(head_office_value: str) -> str:
    """Format head office value for display.
    If this office is a head office the value will be "N/A"
    If this office is a child office the value will be the head office number
    """
    if not head_office_value:
        return "Unknown"
    if head_office_value.lower() in ["n/a", "N/A"]:
        return "Yes"
    return "No"


def format_office_address_one_line(office_data: dict | Office) -> str:
    """
    Format office address data into a single line string.

    Args:
        office_data: Office dictionary or object containing address fields

    Returns:
        Formatted address string with non-empty fields joined by commas
    """
    if isinstance(office_data, Office):
        office_data: dict = office_data.to_internal_dict()

    fields = [
        office_data.get("address_line_1") or office_data.get("addressLine1"),
        office_data.get("address_line_2") or office_data.get("addressLine2"),
        office_data.get("address_line_3") or office_data.get("addressLine3"),
        office_data.get("address_line_4") or office_data.get("addressLine4"),
        office_data.get("city"),
        office_data.get("postcode") or office_data.get("postCode"),
    ]

    # Filter out None and empty string values, then join with commas
    return ", ".join(field.strip() for field in fields if field and field.strip())
