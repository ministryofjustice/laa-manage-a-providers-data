import datetime
import re
from typing import Optional

from app.constants import (
    ADVOCATE_LEVEL_CHOICES,
    CONSTITUTIONAL_STATUS_CHOICES,
    FIRM_TYPE_CHOICES,
)
from app.models import Office


# TODO: Remove this function and replace with a proper wildcard search option
def normalize_for_search(value: str | None) -> str:
    """Normalize a string for fuzzy substring matching by:
    - Remove the '%' character
    """
    if not value:
        return ""
    return re.sub(r"%", "", str(value))


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


def format_date(date: str | datetime.date) -> str:
    """Format ISO date string for display"""
    if not date:
        return ""

    if isinstance(date, str):
        try:
            # Parse ISO format date
            date = datetime.date.fromisoformat(date)
        except (ValueError, TypeError):
            # If it's not a valid ISO date, return as-is
            return date

    if isinstance(date, datetime.date):
        # Format without leading zero, "1 Feb 2020", "20 Jan 2023"
        return date.strftime("%-d %b %Y")
    raise ValueError(f"{date} is not a valid date.")


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


def format_sentence_case(value: str) -> str:
    """Format sentence case for display"""
    if not isinstance(value, str):
        return value
    return value.capitalize()


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


def format_office_address_multi_line_html(office_data: dict | Office) -> str:
    """
    Format office address data into a multiple line HTML string.

    Args:
        office_data: Office dictionary or object containing address fields

    Returns:
        Formatted address string with non-empty fields joined by line breaks
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
    return ",<br>".join(field.strip() for field in fields if field and field.strip())


def format_uncapitalized(s: str) -> str:
    """
    Lower-case only the first character unless a heuristic detects the first word is an acronym.
    Almost the reverse of `str.capitalize` and useful when strings contain acronyms which should
    not be lower-cased.

    Handles strings starting with an acronym:
    >>> format_uncapitalized('VAT number')
    'VAT number'

    Handles acronyms inside strings
    >>> format_uncapitalized('Primary MAPD account')
    'primary MAPD account'

    Handles regular strings
    >>> format_uncapitalized('Correspondence address')
    'correspondence address'

    Args:
        s: String to be changed

    Returns:
        String
    """
    if not s:
        return s
    starts_with_acronym = len(s) > 1 and s[1].isupper()
    continuation_cased = s if starts_with_acronym else s.replace(s[0], s[0].lower(), 1)
    return continuation_cased
