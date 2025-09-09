import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_bank_account(page: Page):
    """Helper function to navigate to Bank Account form via UI flow."""
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

    # Should now be on the Bank Account page
    expect(page.get_by_role("heading", name="Head office: Bank account details")).to_be_visible()
    expect(page.get_by_text("Test Legal Services Provider")).to_be_visible()  # Caption should show provider name


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_loads_correctly(page: Page):
    """Test that the Bank Account form loads correctly."""
    navigate_to_bank_account(page)

    # Verify the page title with newline is rendered correctly
    expect(page.get_by_text("Head office: Bank account details")).to_be_visible()

    # Verify form elements are present
    expect(page.get_by_role("textbox", name="Account name")).to_be_visible()
    expect(page.get_by_role("textbox", name="Sort code")).to_be_visible()
    expect(page.get_by_role("textbox", name="Account number")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_caption_shows_provider_name(page: Page):
    """Test that the Bank Account form caption shows the provider name from the session."""
    navigate_to_bank_account(page)

    # The caption should show the provider name from the session
    expect(page.get_by_text("Test Legal Services Provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_hint_text_visible(page: Page):
    """Test that the Bank Account form shows hint text."""
    navigate_to_bank_account(page)

    expect(page.get_by_text("Must be 6 digits long")).to_be_visible()
    expect(page.get_by_text("Must be between 6 and 8 digits long")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_successful_submission(page: Page):
    """Test successful Bank Account form submission with valid data."""
    navigate_to_bank_account(page)

    # Fill with valid bank account details
    page.get_by_role("textbox", name="Account name").fill("Test Business Account")
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should redirect to create provider page (successful completion)
    expect(page.get_by_text("Head office: Bank account details")).not_to_be_visible()

    # Should see success flow
    current_url = page.url
    assert "add-bank-account" not in current_url


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_sort_code_with_spaces_validation(page: Page):
    """Test Bank Account form accepts sort codes with spaces."""
    navigate_to_bank_account(page)

    # Fill with sort code containing spaces (should be valid)
    page.get_by_role("textbox", name="Account name").fill("Test Account")
    page.get_by_role("textbox", name="Sort code").fill("12 34 56")
    page.get_by_role("textbox", name="Account number").fill("87654321")
    page.get_by_role("button", name="Submit").click()

    # Should submit successfully
    expect(page.get_by_text("Head office: Bank account details")).not_to_be_visible()
    current_url = page.url
    assert "add-bank-account" not in current_url


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_sort_code_with_hyphens_validation(page: Page):
    """Test Bank Account form accepts sort codes with hyphens."""
    navigate_to_bank_account(page)

    # Fill with sort code containing hyphens (should be valid)
    page.get_by_role("textbox", name="Account name").fill("Test Account")
    page.get_by_role("textbox", name="Sort code").fill("12-34-56")
    page.get_by_role("textbox", name="Account number").fill("87654321")
    page.get_by_role("button", name="Submit").click()

    # Should submit successfully
    expect(page.get_by_text("Head office: Bank account details")).not_to_be_visible()
    current_url = page.url
    assert "add-bank-account" not in current_url


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_required_field_validation(page: Page):
    """Test Bank Account form validation for required fields."""
    navigate_to_bank_account(page)

    # Submit without filling required fields
    page.get_by_role("button", name="Submit").click()

    # Should show validation errors
    expect(page.get_by_text("Error: Enter the account name")).to_be_visible()
    expect(page.get_by_text("Error: Enter a sort code")).to_be_visible()
    expect(page.get_by_text("Error: Enter an account number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_invalid_sort_code_validation(page: Page):
    """Test Bank Account form validation with invalid sort code."""
    navigate_to_bank_account(page)

    # Fill with invalid sort code (too short)
    page.get_by_role("textbox", name="Account name").fill("Test Account")
    page.get_by_role("textbox", name="Sort code").fill("12345")
    page.get_by_role("textbox", name="Account number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Enter a valid sort code like 309430")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_invalid_sort_code_letters_validation(page: Page):
    """Test Bank Account form validation with letters in sort code."""
    navigate_to_bank_account(page)

    # Fill with invalid sort code (contains letters)
    page.get_by_role("textbox", name="Account name").fill("Test Account")
    page.get_by_role("textbox", name="Sort code").fill("12AB56")
    page.get_by_role("textbox", name="Account number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Enter a valid sort code like 309430")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_invalid_account_number_validation(page: Page):
    """Test Bank Account form validation with invalid account number."""
    navigate_to_bank_account(page)

    # Fill with invalid account number (too short)
    page.get_by_role("textbox", name="Account name").fill("Test Account")
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("12345")  # 5 digits, too short
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Account number must be between 6 and 8 digits")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_invalid_account_number_letters_validation(page: Page):
    """Test Bank Account form validation with letters in account number."""
    navigate_to_bank_account(page)

    # Fill with invalid account number (contains letters)
    page.get_by_role("textbox", name="Account name").fill("Test Account")
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("1234567A")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Account number must be between 6 and 8 digits")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_six_digit_account_number_validation(page: Page):
    """Test Bank Account form accepts 6-digit account numbers."""
    navigate_to_bank_account(page)

    # Fill with valid 6-digit account number
    page.get_by_role("textbox", name="Account name").fill("Test Account")
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("123456")  # 6 digits, should be valid
    page.get_by_role("button", name="Submit").click()

    # Should submit successfully
    expect(page.get_by_text("Head office: Bank account details")).not_to_be_visible()
    current_url = page.url
    assert "add-bank-account" not in current_url


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_long_account_name_validation(page: Page):
    """Test Bank Account form validation with account name that's too long."""
    navigate_to_bank_account(page)

    # Fill with account name that's too long (over 100 characters)
    long_name = "A" * 101  # 101 characters
    page.get_by_role("textbox", name="Account name").fill(long_name)
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Account name must be 100 characters or less")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_without_head_office_session_gives_error(page: Page):
    """Test that accessing Bank Account form without head office session data gives 400 error."""
    # Start provider flow but don't complete head office details
    page.goto(url_for("main.add_parent_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test LSP")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()

    # Try to access Bank Account form directly without completing head office details
    page.goto(url_for("main.add_bank_account", _external=True))

    # Should get 400 error since head office session data doesn't exist
    assert page.title() == "400 Bad Request"


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_skip_button_visible(page: Page):
    """Test that the skip button is visible on the bank account form."""
    navigate_to_bank_account(page)

    # Verify the skip button is visible
    expect(page.get_by_role("button", name="Cheque payment: Skip this step")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_account_form_skip_functionality(page: Page):
    """Test that the skip button works and bypasses form validation."""
    navigate_to_bank_account(page)

    # Click skip button without filling any fields (should bypass validation)
    page.get_by_role("button", name="Cheque payment: Skip this step").click()

    # Should complete the flow without validation errors
    expect(page.get_by_text("Head office: Bank account details")).not_to_be_visible()

    # Should see success flow
    current_url = page.url
    assert "add-bank-account" not in current_url


@pytest.mark.usefixtures("live_server")
def test_lsp_flow_includes_bank_account_step(page: Page):
    """Test that LSP flow includes the Bank Account step after VAT registration."""
    # Complete the full LSP flow up to VAT registration
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

    # Complete VAT step (leave empty)
    expect(page.get_by_text("Head office: VAT Registration number (optional)")).to_be_visible()
    page.get_by_role("button", name="Submit").click()

    # Should reach Bank Account page
    expect(page.get_by_text("Head office: Bank account details")).to_be_visible()
    expect(page.get_by_text("Flow Test LSP")).to_be_visible()

    # Complete Bank Account step
    page.get_by_role("textbox", name="Account name").fill("Flow Test Account")
    page.get_by_role("textbox", name="Sort code").fill("111111")
    page.get_by_role("textbox", name="Account number").fill("11111111")
    page.get_by_role("button", name="Submit").click()

    # Should complete the flow
    current_url = page.url
    assert "add-bank-account" not in current_url


@pytest.mark.usefixtures("live_server")
def test_lsp_flow_with_skip_bank_account(page: Page):
    """Test complete LSP flow using the skip button for bank account."""
    # Complete the full LSP flow up to bank account
    page.goto(url_for("main.add_parent_provider", _external=True))

    page.get_by_role("textbox", name="Provider name").fill("Skip Test LSP")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()

    # LSP details
    page.get_by_role("radio", name="Partnership").click()
    page.get_by_role("button", name="Submit").click()

    # Head office contact details
    page.get_by_role("textbox", name="Address line 1").fill("456 Skip Street")
    page.get_by_role("textbox", name="Town or city").fill("Skip City")
    page.get_by_role("textbox", name="Postcode").fill("SK1 5IP")
    page.get_by_role("textbox", name="Telephone number").fill("09999999999")
    page.get_by_role("textbox", name="Email address").fill("skip@test.com")
    page.get_by_role("button", name="Submit").click()

    # Complete VAT step (leave empty)
    expect(page.get_by_text("Head office: VAT Registration number (optional)")).to_be_visible()
    page.get_by_role("button", name="Submit").click()

    # Should reach Bank Account page
    expect(page.get_by_text("Head office: Bank account details")).to_be_visible()
    expect(page.get_by_text("Skip Test LSP")).to_be_visible()

    # Skip Bank Account step using the skip button
    page.get_by_role("button", name="Cheque payment: Skip this step").click()

    # Should complete the flow
    current_url = page.url
    assert "add-bank-account" not in current_url
