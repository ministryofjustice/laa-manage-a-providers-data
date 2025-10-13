import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_office_contact_details(page: Page):
    """Helper function to navigate to the Office Contact Details form via UI flow."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    # Search for "Smith" to find "SMITH & PARTNERS SOLICITORS"
    page.get_by_role("textbox", name="Find a provider").fill("smith")
    page.get_by_role("button", name="Search").click()

    # Click on the first provider
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    # Click on the Offices sub-navigation
    page.get_by_role("link", name="Offices").click()

    # Click "Add an office" button
    page.get_by_role("button", name="Add another office").click()

    # Fill the add office form
    page.get_by_role("textbox", name="Office name").fill("Test Office")
    page.get_by_role("radio", name="Yes").click()
    page.get_by_role("button", name="Continue").click()

    # Should now be on the office contact details page
    expect(page.get_by_role("heading", name="Office contact details")).to_be_visible()
    expect(page.get_by_text("Test Office")).to_be_visible()  # Caption should show office name


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


@pytest.mark.usefixtures("live_server")
def test_form_caption_shows_office_name(page: Page):
    """Test that the form caption shows the office name from the previous step."""
    navigate_to_office_contact_details(page)

    # The caption should show the office name from the session
    expect(page.get_by_text("Test Office")).to_be_visible()


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


@pytest.mark.usefixtures("live_server")
def test_direct_access_without_session_redirects(page: Page):
    """Test that accessing contact details directly without session data gives 404."""
    # Try to access contact details page directly without going through add office flow
    resp = page.goto(url_for("main.add_office_contact_details", firm=1, _external=True))
    assert resp is not None
    assert resp.status == 400
    # Should get 400 error since no session data exists
    expect(page.get_by_role("heading", name="Sorry, there is a problem with the service")).to_be_visible
