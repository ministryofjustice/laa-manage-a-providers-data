from datetime import datetime
from typing import Optional

from app.constants import ADVOCATE_LEVEL_CHOICES, CONSTITUTIONAL_STATUS_CHOICES, FIRM_TYPE_CHOICES


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


def format_sentence_case(value: str) -> str:
    """Format sentence case for display"""
    if not isinstance(value, str):
        return value
    return value.capitalize()
