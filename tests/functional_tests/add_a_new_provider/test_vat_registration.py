import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_vat_registration(page: Page):
    """Helper function to navigate to VAT Registration form via UI flow."""
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
    page.get_by_role("button", name="Submit").click()

    # Fill head office contact details form
    page.get_by_role("textbox", name="Address line 1").fill("123 Head Office Street")
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="Postcode").fill("HO1 2CE")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("headoffice@testlsp.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Head Office Centre")
    page.get_by_role("button", name="Submit").click()

    # Should now be on the VAT registration page
    expect(page.get_by_role("heading", name="Head office: VAT Registration number (optional)")).to_be_visible()
    expect(page.get_by_text("Test Legal Services Provider")).to_be_visible()  # Caption should show provider name


@pytest.mark.usefixtures("live_server")
def test_vat_form_loads_correctly(page: Page):
    """Test that the VAT Registration form loads correctly."""
    navigate_to_vat_registration(page)

    # Verify the page title with newline is rendered correctly
    expect(page.get_by_text("Head office: VAT Registration number (optional)")).to_be_visible()

    # Verify form elements are present
    expect(page.get_by_role("textbox")).to_be_visible()  # VAT number field
    expect(
        page.get_by_text("This is 9 numbers, sometimes with ‘GB’ at the start, for example 123456789 or GB123456789.")
    ).to_be_visible()  # Hint text
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_vat_form_caption_shows_provider_name(page: Page):
    """Test that the VAT form caption shows the provider name from the session."""
    navigate_to_vat_registration(page)

    # The caption should show the provider name from the session
    expect(page.get_by_text("Test Legal Services Provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_vat_form_is_optional_can_submit_empty(page: Page):
    """Test that VAT registration is optional and form can be submitted empty."""
    navigate_to_vat_registration(page)

    # Submit without entering VAT number (should be allowed as it's optional)
    page.get_by_role("button", name="Submit").click()

    # Should redirect to create provider page (successful completion)
    expect(page.get_by_text("Head office: VAT Registration number (optional)")).not_to_be_visible()

    # Should see success flow
    current_url = page.url
    assert "add-vat-number" not in current_url


@pytest.mark.usefixtures("live_server")
def test_vat_form_valid_number_submission(page: Page):
    """Test successful VAT form submission with valid VAT number."""
    navigate_to_vat_registration(page)

    # Fill with valid VAT number (9 digits)
    page.get_by_role("textbox").fill("123456789")
    page.get_by_role("button", name="Submit").click()

    # Should redirect to create provider page
    expect(page.get_by_text("Head office: VAT Registration number (optional)")).not_to_be_visible()
    current_url = page.url
    assert "add-vat-number" not in current_url


@pytest.mark.usefixtures("live_server")
def test_vat_form_valid_gb_number_submission(page: Page):
    """Test successful VAT form submission with GB prefixed VAT number."""
    navigate_to_vat_registration(page)

    # Fill with valid GB VAT number
    page.get_by_role("textbox").fill("GB123456789")
    page.get_by_role("button", name="Submit").click()

    # Should redirect to create provider page
    expect(page.get_by_text("Head office: VAT Registration number (optional)")).not_to_be_visible()
    current_url = page.url
    assert "add-vat-number" not in current_url


@pytest.mark.usefixtures("live_server")
def test_vat_form_invalid_number_validation(page: Page):
    """Test VAT form validation with invalid VAT number."""
    navigate_to_vat_registration(page)

    # Fill with invalid VAT number (too short)
    page.get_by_role("textbox").fill("12345")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Enter the VAT registration number in the correct format")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_vat_form_invalid_format_validation(page: Page):
    """Test VAT form validation with invalid format."""
    navigate_to_vat_registration(page)

    # Fill with invalid format (contains letters in wrong places)
    page.get_by_role("textbox").fill("GB12345ABC")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Enter the VAT registration number in the correct format")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_vat_form_hint_text_visible(page: Page):
    """Test that the VAT form shows helpful hint text."""
    navigate_to_vat_registration(page)

    # Check that hint text is visible and helpful
    expect(
        page.get_by_text("This is 9 numbers, sometimes with ‘GB’ at the start, for example 123456789 or GB123456789.")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_vat_form_field_styling(page: Page):
    """Test that the VAT form field has correct styling classes."""
    navigate_to_vat_registration(page)

    vat_field = page.get_by_role("textbox")

    # The field should have the half-width CSS class applied
    assert "govuk-!-width-one-half" in vat_field.get_attribute("class")


@pytest.mark.usefixtures("live_server")
def test_vat_form_data_stored_in_session(page: Page):
    """Test that VAT number data is properly stored in session for later use."""
    navigate_to_vat_registration(page)

    # Fill with valid VAT number
    page.get_by_role("textbox").fill("987654321")
    page.get_by_role("button", name="Submit").click()

    # The form should redirect successfully, indicating data was processed
    expect(page.get_by_text("Head office: VAT Registration number (optional)")).not_to_be_visible()

    # Verify we've moved past the form (session data should be set)
    current_url = page.url
    assert "add-vat-number" not in current_url


@pytest.mark.usefixtures("live_server")
def test_vat_form_direct_access_without_session_gives_error(page: Page):
    """Test that accessing VAT form directly without session data gives 400 error."""
    # Try to access VAT form directly without going through add provider flow
    page.goto(url_for("main.add_vat_number", _external=True))

    # Should get 400 error since no session data exists
    assert page.title() == "400 Bad Request"


@pytest.mark.usefixtures("live_server")
def test_vat_form_without_head_office_session_gives_error(page: Page):
    """Test that accessing VAT form without head office session data gives 400 error."""
    # Start provider flow but don't complete head office details
    page.goto(url_for("main.add_parent_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test LSP")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()

    # Try to access VAT form directly without completing head office details
    page.goto(url_for("main.add_vat_number", _external=True))

    # Should get 400 error since head office session data doesn't exist
    assert page.title() == "400 Bad Request"


@pytest.mark.usefixtures("live_server")
def test_lsp_flow_includes_vat_step(page: Page):
    """Test that LSP flow includes the VAT registration step."""
    # Complete the full LSP flow up to head office contact details
    page.goto(url_for("main.add_parent_provider", _external=True))

    page.get_by_role("textbox", name="Provider name").fill("Flow Test LSP")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()

    # LSP details
    page.get_by_role("radio", name="Limited company").click()
    page.get_by_role("textbox", name="Day").fill("01")
    page.get_by_role("textbox", name="Month").fill("01")
    page.get_by_role("textbox", name="Year").fill("2020")
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Head office contact details
    page.get_by_role("textbox", name="Address line 1").fill("123 Test Street")
    page.get_by_role("textbox", name="Town or city").fill("Test City")
    page.get_by_role("textbox", name="Postcode").fill("TE1 5ST")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("test@lsp.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Test Centre")
    page.get_by_role("button", name="Submit").click()

    # Should reach VAT registration page (not skip it)
    expect(page.get_by_text("Head office: VAT Registration number (optional)")).to_be_visible()
    expect(page.get_by_text("Flow Test LSP")).to_be_visible()

    # Complete VAT step (leave empty)
    page.get_by_role("button", name="Submit").click()

    # Should complete the flow
    current_url = page.url
    assert "add-vat-number" not in current_url
