import datetime

from app.utils.formatting import format_date, format_uncapitalized


def test_format_uncapitalized():
    assert format_uncapitalized("VAT number") == "VAT number"
    assert format_uncapitalized("Primary MAPD account") == "primary MAPD account"
    assert format_uncapitalized("Correspondence address") == "correspondence address"

    assert format_uncapitalized("") == ""
    assert format_uncapitalized("A") == "a"
    assert format_uncapitalized("AB") == "AB"  # Two uppercase = acronym


def test_format_date_with_iso_string():
    assert format_date("2024-09-12") == "12 Sep 2024"
    assert format_date("2025-01-01") == "1 Jan 2025"
    assert format_date("2023-12-25") == "25 Dec 2023"
    assert format_date("2024-02-29") == "29 Feb 2024"


def test_format_date_with_date_object():
    assert format_date(datetime.date(2024, 1, 5)) == "5 Jan 2024"
    assert format_date(datetime.date(2025, 12, 31)) == "31 Dec 2025"
    assert format_date(datetime.date(2023, 7, 4)) == "4 Jul 2023"
    assert format_date(datetime.date(2024, 11, 15)) == "15 Nov 2024"


def test_format_date_with_none_returns_empty_string():
    assert format_date(None) == ""


def test_format_date_with_invalid_string_returns_original():
    assert format_date("not-a-date") == "not-a-date"
