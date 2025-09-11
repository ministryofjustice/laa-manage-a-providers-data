import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_liaison_manager_via_lsp(page: Page):
    """Helper function to navigate to Liaison Manager form via the LSP flow."""
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

    # Fill VAT registration form (optional, skip by submitting empty)
    expect(page.get_by_role("heading", name="Head office: VAT Registration number (optional)")).to_be_visible()
    page.get_by_role("button", name="Submit").click()

    # Fill bank account form
    expect(page.get_by_role("heading", name="Head office: Bank account details")).to_be_visible()
    page.get_by_role("textbox", name="Account name").fill("Test Business Account")
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should now be on the Liaison Manager page
    expect(page.get_by_role("heading", name="Add liaison manager")).to_be_visible()
    expect(page.get_by_text("Test Legal Services Provider")).to_be_visible()  # Caption should show provider name


def navigate_to_liaison_manager_via_chambers(page: Page):
    """Helper function to navigate to Liaison Manager form via the Chambers flow."""
    # Start with add parent provider
    page.goto(url_for("main.add_parent_provider", _external=True))

    # Fill provider details form (Chambers flow is simpler)
    page.get_by_role("textbox", name="Provider name").fill("Test Chambers")
    page.get_by_role("radio", name="Chambers").click()
    page.get_by_role("button", name="Continue").click()

    # Fill chambers contact details form
    expect(page.get_by_role("heading", name="Add chambers contact details")).to_be_visible()
    page.get_by_role("textbox", name="Address line 1").fill("123 Chambers Street")
    page.get_by_role("textbox", name="Town or city").fill("Chambers City")
    page.get_by_role("textbox", name="Postcode").fill("CH1 2CE")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("chambers@testchambers.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Chambers Centre")
    page.get_by_role("button", name="Submit").click()

    # Should now be on the Liaison Manager page
    expect(page.get_by_role("heading", name="Add liaison manager")).to_be_visible()
    expect(page.get_by_text("Test Chambers")).to_be_visible()  # Caption should show provider name


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_loads_correctly_lsp_flow(page: Page):
    """Test that the Liaison Manager form loads correctly via LSP flow."""
    navigate_to_liaison_manager_via_lsp(page)

    # Verify the page title
    expect(page.get_by_role("heading", name="Add liaison manager")).to_be_visible()

    # Verify form elements are present
    expect(page.get_by_role("textbox", name="First name")).to_be_visible()
    expect(page.get_by_role("textbox", name="Last name")).to_be_visible()
    expect(page.get_by_role("textbox", name="Email address")).to_be_visible()
    expect(page.get_by_role("textbox", name="Telephone number")).to_be_visible()
    expect(page.get_by_role("textbox", name="Website (optional)")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_loads_correctly_chambers_flow(page: Page):
    """Test that the Liaison Manager form loads correctly via Chambers flow."""
    navigate_to_liaison_manager_via_chambers(page)

    # Verify the page title
    expect(page.get_by_role("heading", name="Add liaison manager")).to_be_visible()

    # Verify form elements are present
    expect(page.get_by_role("textbox", name="First name")).to_be_visible()
    expect(page.get_by_role("textbox", name="Last name")).to_be_visible()
    expect(page.get_by_role("textbox", name="Email address")).to_be_visible()
    expect(page.get_by_role("textbox", name="Telephone number")).to_be_visible()
    expect(page.get_by_role("textbox", name="Website (optional)")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_caption_shows_provider_name_lsp(page: Page):
    """Test that the Liaison Manager form caption shows the LSP provider name from the session."""
    navigate_to_liaison_manager_via_lsp(page)

    # The caption should show the provider name from the session
    expect(page.get_by_text("Test Legal Services Provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_caption_shows_provider_name_chambers(page: Page):
    """Test that the Liaison Manager form caption shows the Chambers provider name from the session."""
    navigate_to_liaison_manager_via_chambers(page)

    # The caption should show the provider name from the session
    expect(page.get_by_text("Test Chambers")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_successful_submission_lsp(page: Page):
    """Test successful Liaison Manager form submission with valid data via LSP flow."""
    navigate_to_liaison_manager_via_lsp(page)

    # Fill with valid liaison manager details
    page.get_by_role("textbox", name="First name").fill("John")
    page.get_by_role("textbox", name="Last name").fill("Smith")
    page.get_by_role("textbox", name="Email address").fill("john.smith@testlsp.com")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Website (optional)").fill("https://www.testlsp.com")
    page.get_by_role("button", name="Submit").click()

    # Should complete the flow successfully
    current_url = page.url
    assert "add-liaison-manager" not in current_url


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_successful_submission_chambers(page: Page):
    """Test successful Liaison Manager form submission with valid data via Chambers flow."""
    navigate_to_liaison_manager_via_chambers(page)

    # Fill with valid liaison manager details
    page.get_by_role("textbox", name="First name").fill("Jane")
    page.get_by_role("textbox", name="Last name").fill("Doe")
    page.get_by_role("textbox", name="Email address").fill("jane.doe@testchambers.com")
    page.get_by_role("textbox", name="Telephone number").fill("09876543210")
    page.get_by_role("textbox", name="Website (optional)").fill("https://www.testchambers.com")
    page.get_by_role("button", name="Submit").click()

    # Should complete the flow successfully
    current_url = page.url
    assert "add-liaison-manager" not in current_url


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_successful_submission_without_website(page: Page):
    """Test successful Liaison Manager form submission without optional website field."""
    navigate_to_liaison_manager_via_lsp(page)

    # Fill with valid details but skip optional website
    page.get_by_role("textbox", name="First name").fill("Alice")
    page.get_by_role("textbox", name="Last name").fill("Johnson")
    page.get_by_role("textbox", name="Email address").fill("alice.johnson@testlsp.com")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    # Leave website empty
    page.get_by_role("button", name="Submit").click()

    # Should complete the flow successfully
    current_url = page.url
    assert "add-liaison-manager" not in current_url


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_required_field_validation(page: Page):
    """Test Liaison Manager form validation for required fields."""
    navigate_to_liaison_manager_via_lsp(page)

    # Submit without filling required fields
    page.get_by_role("button", name="Submit").click()

    # Should show validation errors for required fields
    expect(page.get_by_text("Error: Enter the first name")).to_be_visible()
    expect(page.get_by_text("Error: Enter the last name")).to_be_visible()
    expect(page.get_by_text("Error: Enter the email address")).to_be_visible()
    expect(page.get_by_text("Error: Enter the telephone number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_invalid_email_validation(page: Page):
    """Test Liaison Manager form validation with invalid email."""
    navigate_to_liaison_manager_via_lsp(page)

    # Fill with invalid email
    page.get_by_role("textbox", name="First name").fill("John")
    page.get_by_role("textbox", name="Last name").fill("Smith")
    page.get_by_role("textbox", name="Email address").fill("invalid-email")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("button", name="Submit").click()

    # Should show email validation error
    expect(page.get_by_text("Error: Enter a valid email address")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_long_field_validation(page: Page):
    """Test Liaison Manager form validation with fields that are too long."""
    navigate_to_liaison_manager_via_lsp(page)

    # Fill with fields that are too long
    long_name = "A" * 101  # 101 characters
    long_phone = "1" * 21  # 21 characters
    long_website = "https://www." + "a" * 250 + ".com"  # Over 255 characters

    page.get_by_role("textbox", name="First name").fill(long_name)
    page.get_by_role("textbox", name="Last name").fill(long_name)
    page.get_by_role("textbox", name="Telephone number").fill(long_phone)
    page.get_by_role("textbox", name="Website (optional)").fill(long_website)
    page.get_by_role("button", name="Submit").click()

    # Should show validation errors
    expect(page.get_by_text("Error: First name must be 100 characters or less")).to_be_visible()
    expect(page.get_by_text("Error: Last name must be 100 characters or less")).to_be_visible()
    expect(page.get_by_text("Error: Telephone number must be 20 characters or less")).to_be_visible()
    expect(page.get_by_text("Error: Website must be 255 characters or less")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_liaison_manager_form_without_head_office_session_gives_error(page: Page):
    """Test that accessing Liaison Manager form without head office session data gives 400 error."""
    # Start provider flow but don't complete head office details
    page.goto(url_for("main.add_parent_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test LSP")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()

    # Try to access Liaison Manager form directly without completing head office details
    page.goto(url_for("main.add_liaison_manager", _external=True))

    # Should get 400 error since head office session data doesn't exist
    assert page.title() == "400 Bad Request"
