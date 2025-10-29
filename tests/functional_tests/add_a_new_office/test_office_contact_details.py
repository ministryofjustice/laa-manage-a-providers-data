import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def table_to_dict(page: Page, table_selector: str) -> dict:
    """Convert a two-column table (<th> + <td>) into a Python dict."""
    table_dict = {}
    rows = page.locator(f"{table_selector} tr")

    for i in range(rows.count()):
        row = rows.nth(i)
        header = row.locator("th").inner_text().strip()
        cell = row.locator("td").inner_text().strip()
        table_dict[header] = cell

    return table_dict


def navigate_to_office_contact_details(page: Page, provider_name="SMITH & PARTNERS SOLICITORS", has_office=True):
    """Helper function to navigate to the Office Contact Details form via UI flow."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    # Search for "Smith" to find "SMITH & PARTNERS SOLICITORS"
    page.get_by_role("textbox", name="Find a provider").fill(provider_name)
    page.get_by_role("button", name="Search").click()

    # Click on the first provider
    page.get_by_role("link", name=provider_name).click()

    # Click on the Offices sub-navigation
    page.get_by_role("link", name="Offices").click()

    if has_office:
        # Click "Add another office" button
        page.get_by_role("button", name="Add another office").click()
        expect(page.get_by_role("button", name="Add an office")).not_to_be_visible()
    else:
        # Click "Add an office" button
        page.get_by_role("button", name="Add an office").click()
        expect(page.get_by_role("button", name="Add another office")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_form_loads_correctly(page: Page):
    """Test that the Office Details form loads correctly."""
    navigate_to_office_contact_details(page)

    # Verify section heading is present
    expect(page.get_by_role("heading", name="Address")).to_be_visible()

    # Verify all form elements are present with updated labels
    expect(page.get_by_role("textbox", name="Address line 1")).to_be_visible()
    expect(page.get_by_role("textbox", name="Address line 2 (optional)")).to_be_visible()
    expect(page.get_by_role("textbox", name="Address line 3 (optional)")).to_be_visible()
    expect(page.get_by_role("textbox", name="Address line 4 (optional)")).to_be_visible()
    expect(page.get_by_role("textbox", name="Town or city")).to_be_visible()
    expect(page.get_by_role("textbox", name="County (optional)")).to_be_visible()
    expect(page.get_by_role("textbox", name="Postcode")).to_be_visible()
    expect(page.get_by_role("textbox", name="Telephone number")).to_be_visible()
    expect(page.get_by_role("textbox", name="Email address")).to_be_visible()
    expect(page.get_by_role("textbox", name="DX number")).to_be_visible()
    expect(page.get_by_role("textbox", name="DX centre")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_required_fields_validation(page: Page):
    """Test that required fields show validation errors."""
    navigate_to_office_contact_details(page)

    # Try to submit without filling required fields
    page.get_by_role("button", name="Submit").click()

    # Should show validation errors for required fields
    expect(page.get_by_text("Error: Enter address line 1, typically the building and street")).to_be_visible()
    expect(page.get_by_text("Error: Enter the town or city")).to_be_visible()
    expect(page.get_by_text("Error: Enter the postcode")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_email_validation(page: Page):
    """Test email field validation."""
    navigate_to_office_contact_details(page)

    # Fill required fields and invalid email
    page.get_by_role("textbox", name="Address line 1").fill("123 Test Street")
    page.get_by_role("textbox", name="Town or city").fill("Test City")
    page.get_by_role("textbox", name="Postcode").fill("TE1 5ST")
    page.get_by_role("textbox", name="Email address").fill("invalid-email")
    page.get_by_role("button", name="Submit").click()

    # Should show email validation error
    expect(page.get_by_text("Error: Enter a valid email address")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_field_length_validation(page: Page):
    """Test field length validation."""
    navigate_to_office_contact_details(page)

    # Fill with too long values
    long_address = "A" * 241  # Over 240 characters
    page.get_by_role("textbox", name="Address line 1").fill(long_address)
    page.get_by_role("textbox", name="Town or city").fill("Test City")
    page.get_by_role("textbox", name="Postcode").fill("TE1 5ST")
    page.get_by_role("button", name="Submit").click()

    # Should show length validation error
    expect(page.get_by_text("Error: Address line 1 must be 240 characters or fewer")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_postcode_validation(page: Page):
    """Test postcode field validation."""
    navigate_to_office_contact_details(page)

    # Fill required fields and invalid postcode
    page.get_by_role("textbox", name="Address line 1").fill("123 Test Street")
    page.get_by_role("textbox", name="Town or city").fill("Test City")
    page.get_by_role("textbox", name="Postcode").fill("INVALID")
    page.get_by_role("button", name="Submit").click()

    # Should show postcode validation error
    expect(page.get_by_text("Error: Enter a valid UK postcode")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_postcode_auto_capitalize(page: Page):
    """Test that postcode field auto-capitalizes input."""
    navigate_to_office_contact_details(page)

    postcode_field = page.get_by_role("textbox", name="Postcode")

    # The field should have the auto-capitalise CSS class applied
    assert "auto-capitalise" in postcode_field.get_attribute("class")


@pytest.mark.usefixtures("live_server")
def test_successful_form_submission_minimal(page: Page):
    """Test successful form submission with all required fields."""
    navigate_to_office_contact_details(page)

    # Fill all required fields
    page.get_by_role("textbox", name="Address line 1").fill("123 Test Street")
    page.get_by_role("textbox", name="Town or city").fill("Test City")
    page.get_by_role("textbox", name="Postcode").fill("TE1 5ST")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("test@office.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Test Centre")
    page.get_by_role("button", name="Submit").click()

    # Should redirect to the new office
    expect(page.locator("span").filter(has_text="SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("heading", name="Office: ")).to_be_visible()
    expect(page.get_by_text("123 Test Street")).to_be_visible()
    expect(page.get_by_text("Test City")).to_be_visible()
    expect(page.get_by_text("TE1 5ST")).to_be_visible()

    # Verify payment method defaults to Electronic
    page.get_by_role("link", name="Bank accounts and payment").click()
    expect(page.get_by_text("Payment method").locator("xpath=following-sibling::*[1]")).to_have_text("Electronic")


@pytest.mark.usefixtures("live_server")
def test_successful_form_submission_all_fields(page: Page):
    """Test successful form submission with all fields filled."""
    navigate_to_office_contact_details(page)

    # Fill all fields
    page.get_by_role("textbox", name="Address line 1").fill("123 Test Street")
    page.get_by_role("textbox", name="Address line 2 (optional)").fill("Suite 456")
    page.get_by_role("textbox", name="Address line 3 (optional)").fill("Business Park")
    page.get_by_role("textbox", name="Address line 4 (optional)").fill("Industrial Estate")
    page.get_by_role("textbox", name="Town or city").fill("Test City")
    page.get_by_role("textbox", name="County (optional)").fill("Test County")
    page.get_by_role("textbox", name="Postcode").fill("TE1 5ST")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("test@office.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Test Centre")
    page.get_by_role("button", name="Submit").click()

    # Should redirect to the new office
    expect(page.locator("span").filter(has_text="SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("heading", name="Office: ")).to_be_visible()
    expect(page.get_by_text("123 Test Street")).to_be_visible()
    expect(page.get_by_text("Suite 456")).to_be_visible()
    expect(page.get_by_text("Business Park")).to_be_visible()
    expect(page.get_by_text("Test City")).to_be_visible()
    expect(page.get_by_text("TE1 5ST")).to_be_visible()

    # Verify payment method defaults to Electronic
    page.get_by_role("link", name="Bank accounts and payment").click()
    expect(page.get_by_text("Payment method").locator("xpath=following-sibling::*[1]")).to_have_text("Electronic")


@pytest.mark.usefixtures("live_server")
def test_optional_fields_not_required(page: Page):
    """Test that optional fields don't prevent form submission."""
    navigate_to_office_contact_details(page)

    # Fill required fields, leave optional fields empty
    page.get_by_role("textbox", name="Address line 1").fill("123 Test Street")
    page.get_by_role("textbox", name="Town or city").fill("Test City")
    page.get_by_role("textbox", name="Postcode").fill("TE1 5ST")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("test@office.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Test Centre")
    # Leave optional fields empty: address_line_2-4, county
    page.get_by_role("button", name="Submit").click()

    # Should redirect to the new office
    expect(page.locator("span").filter(has_text="SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("heading", name="Office: ")).to_be_visible()
    expect(page.get_by_text("123 Test Street")).to_be_visible()
    expect(page.get_by_text("Test City")).to_be_visible()
    expect(page.get_by_text("TE1 5ST")).to_be_visible()

    # Make sure the new office is NOT marked as the head office because this provider has a head office.
    overview_table = table_to_dict(page, "h2:has-text('Overview') + table")
    assert overview_table["Head office"] == "No"


@pytest.mark.usefixtures("live_server")
def test_add_head_office(page: Page):
    """If the firm has no offices then office new being added becomes the head office"""
    navigate_to_office_contact_details(page, provider_name="LIVERPOOL LEGAL CENTRE", has_office=False)

    # Fill required fields, leave optional fields empty
    page.get_by_role("textbox", name="Address line 1").fill("123 Test Street")
    page.get_by_role("textbox", name="Town or city").fill("Test City")
    page.get_by_role("textbox", name="Postcode").fill("TE1 5ST")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("test@office.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Test Centre")
    # Leave optional fields empty: address_line_2-4, county
    page.get_by_role("button", name="Submit").click()

    # Make sure the new office is marked as the head office because this provider did not have head office.
    overview_table = table_to_dict(page, "h2:has-text('Overview') + table")
    assert overview_table["Head office"] == "Yes"
