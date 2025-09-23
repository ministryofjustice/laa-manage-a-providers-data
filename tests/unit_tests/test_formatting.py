from app.utils.formatting import format_uncapitalized


def test_format_uncapitalized():
    assert format_uncapitalized("VAT number") == "VAT number"
    assert format_uncapitalized("Primary MAPD account") == "primary MAPD account"
    assert format_uncapitalized("Correspondence address") == "correspondence address"

    assert format_uncapitalized("") == ""
    assert format_uncapitalized("A") == "a"
    assert format_uncapitalized("AB") == "AB"  # Two uppercase = acronym
