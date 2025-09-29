import pytest
import re
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_head_office_contact_details(page: Page):
    """Helper function to navigate to Head Office Contact Details form via UI flow."""
    # Start with add parent provider
    page.goto(url_for("main.add_parent_provider", _external=True))

    # Fill provider details form
    page.get_by_role("textbox", name="Provider name").fill("Test Legal Services Provider")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()

    # Fill LSP details form
    page.get_by_role("radio", name="Limited company").click()
    page.get_by_role("textbox", name="Day").fill("01")
    page.get_by_role("textbox", name="Month").fill("01")
    page.get_by_role("textbox", name="Year").fill("2020")
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Continue").click()

    # Should now be on the head office contact details page
    expect(page.get_by_role("heading", name="Head office contact details")).to_be_visible()
    expect(page.get_by_text("Test Legal Services Provider")).to_be_visible()  # Caption should show provider name


@pytest.mark.usefixtures("live_server")
def test_form_loads_correctly(page: Page):
    """Test that the Head Office Contact Details form loads correctly."""
    navigate_to_head_office_contact_details(page)

    # Verify section heading is present
    expect(page.get_by_role("heading", name="Address")).to_be_visible()

    # Verify all form elements are present with correct labels
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
    expect(page.get_by_role("button", name="Continue")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_form_caption_shows_provider_name(page: Page):
    """Test that the form caption shows the provider name from the session."""
    navigate_to_head_office_contact_details(page)

    # The caption should show the provider name from the session
    expect(page.get_by_text("Test Legal Services Provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_required_fields_validation(page: Page):
    """Test that required fields show validation errors."""
    navigate_to_head_office_contact_details(page)

    # Try to submit without filling required fields
    page.get_by_role("button", name="Continue").click()

    # Should show validation errors for required fields
    expect(page.get_by_text("Error: Enter address line 1, typically the building and street")).to_be_visible()
    expect(page.get_by_text("Error: Enter the town or city")).to_be_visible()
    expect(page.get_by_text("Error: Enter the postcode")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_email_validation(page: Page):
    """Test email field validation."""
    navigate_to_head_office_contact_details(page)

    # Fill required fields and invalid email
    page.get_by_role("textbox", name="Address line 1").fill("123 Head Office Street")
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="Postcode").fill("HO1 2CE")
    page.get_by_role("textbox", name="Email address").fill("invalid-email")
    page.get_by_role("button", name="Continue").click()

    # Should show email validation error
    expect(page.get_by_text("Error: Enter a valid email address")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_postcode_validation(page: Page):
    """Test postcode field validation."""
    navigate_to_head_office_contact_details(page)

    # Fill required fields and invalid postcode
    page.get_by_role("textbox", name="Address line 1").fill("123 Head Office Street")
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="Postcode").fill("INVALID")
    page.get_by_role("button", name="Continue").click()

    # Should show postcode validation error
    expect(page.get_by_text("Error: Enter a valid UK postcode")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_field_length_validation(page: Page):
    """Test field length validation."""
    navigate_to_head_office_contact_details(page)

    # Fill with too long values
    long_address = "A" * 241  # Over 240 characters
    page.get_by_role("textbox", name="Address line 1").fill(long_address)
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="Postcode").fill("HO1 2CE")
    page.get_by_role("button", name="Continue").click()

    # Should show length validation error
    expect(page.get_by_text("Error: Address line 1 must be 240 characters or fewer")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_successful_form_submission_minimal_fields(page: Page):
    """Test successful form submission with required fields only."""
    navigate_to_head_office_contact_details(page)

    # Fill all required fields
    page.get_by_role("textbox", name="Address line 1").fill("123 Head Office Street")
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="Postcode").fill("HO1 2CE")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("headoffice@testlsp.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Head Office Centre")
    page.get_by_role("button", name="Continue").click()

    # Check we are on the VAT registration number page
    expect(page.get_by_role("heading", name="Head office: VAT registration number (optional)")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_successful_form_submission_all_fields(page: Page):
    """Test successful form submission with all fields filled."""
    navigate_to_head_office_contact_details(page)

    # Fill all fields
    page.get_by_role("textbox", name="Address line 1").fill("123 Head Office Street")
    page.get_by_role("textbox", name="Address line 2 (optional)").fill("Suite 789")
    page.get_by_role("textbox", name="Address line 3 (optional)").fill("Business Complex")
    page.get_by_role("textbox", name="Address line 4 (optional)").fill("Corporate District")
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="County (optional)").fill("Head Office County")
    page.get_by_role("textbox", name="Postcode").fill("HO1 2CE")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("headoffice@testlsp.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Head Office Centre")
    page.get_by_role("button", name="Continue").click()

    # Check we are on the VAT registration number page
    expect(page.get_by_role("heading", name="Head office: VAT registration number (optional)")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_optional_fields_not_required(page: Page):
    """Test that optional fields don't prevent form submission."""
    navigate_to_head_office_contact_details(page)

    # Fill required fields, leave optional fields empty
    page.get_by_role("textbox", name="Address line 1").fill("123 Head Office Street")
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="Postcode").fill("HO1 2CE")
    page.get_by_role("textbox", name="Email address").fill("headoffice@testlsp.com")
    # Leave optional fields empty: address_line_2-4, county, telephone number, DX number & centre
    page.get_by_role("button", name="Continue").click()

    # Check we are on the VAT registration number page
    expect(page.get_by_role("heading", name="Head office: VAT registration number (optional)")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_postcode_auto_capitalize(page: Page):
    """Test that postcode field auto-capitalizes input."""
    navigate_to_head_office_contact_details(page)

    postcode_field = page.get_by_role("textbox", name="Postcode")

    # The field should have the auto-capitalise CSS class applied
    assert "auto-capitalise" in postcode_field.get_attribute("class")


@pytest.mark.usefixtures("live_server")
def test_payment_method_selection_persists(page: Page):
    """Test successful form submission with required fields only."""
    navigate_to_head_office_contact_details(page)

    # Fill all required fields
    page.get_by_role("textbox", name="Address line 1").fill("123 Head Office Street")
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="Postcode").fill("HO1 2CE")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("headoffice@testlsp.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Head Office Centre")
    page.get_by_role("button", name="Continue").click()

    # Check we are on the VAT registration number page
    expect(page.get_by_role("heading", name="Head office: VAT registration number (optional)")).to_be_visible()
    page.get_by_role("button", name="Continue").click()

    # Fill bank account form
    expect(page.get_by_role("heading", name="Head office: Bank account details")).to_be_visible()
    page.get_by_role("textbox", name="Account name").fill("Test Business Account")
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("12345678")
    page.get_by_role("button", name="Continue").click()

    # Fill liaison manager form
    expect(page.get_by_role("heading", name="Add liaison manager")).to_be_visible()
    page.get_by_role("textbox", name="First name").fill("John")
    page.get_by_role("textbox", name="Last name").fill("Smith")
    page.get_by_role("textbox", name="Email address").fill("john.smith@testlsp.com")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("button", name="Continue").click()

    # Should now be on the Assign Contract Manager page
    page.get_by_role("textbox", name="Search for a contract manager").fill("Alice")
    page.get_by_role("button", name="Search").click()

    # Select the contract manager
    page.get_by_role("radio", name="Select this row").click()

    # Submit the form
    page.get_by_role("button", name="Submit").click()

    # Click on the Offices sub-navigation
    page.get_by_role("link", name="Offices").click()

    # Click on the first office link in the table
    page.locator("a.govuk-link").filter(has_text=re.compile(r"^[A-Z0-9]+[A-Z]$")).first.click()
    expect(page.get_by_text("Bank accounts and payment")).to_be_visible()
    page.get_by_text("Bank accounts and payment").click()
    expect(page.get_by_text("Payment Information")).to_be_visible()
    expect(page.get_by_text("Electronic")).to_be_visible()
