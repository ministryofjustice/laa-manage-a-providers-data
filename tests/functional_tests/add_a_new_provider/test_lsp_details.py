import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_lsp_details(page: Page):
    """Helper function to navigate to LSP details page via UI flow."""
    page.goto(url_for("main.add_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test LSP")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Legal services provider details")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_lsp_details_page_loads_via_ui(page: Page):
    """Test that the LSP details page loads correctly via UI navigation."""
    navigate_to_lsp_details(page)
    expect(page.get_by_text("Test LSP")).to_be_visible()
    expect(page.get_by_role("heading", name="Legal services provider details"))
    expect(page.get_by_role("radio", name="Government funded organisation")).to_be_visible()
    expect(page.get_by_role("radio", name="Sole practitioner")).to_be_visible()
    expect(page.get_by_role("radio", name="Charity")).to_be_visible()
    expect(page.get_by_role("radio", name="Partnership")).to_be_visible()
    expect(page.get_by_role("radio", name="LLP")).to_be_visible()
    expect(page.get_by_role("radio", name="Limited company")).to_be_visible()
    expect(page.get_by_role("textbox", name="Day")).to_be_visible()
    expect(page.get_by_role("textbox", name="Month")).to_be_visible()
    expect(page.get_by_role("textbox", name="Year")).to_be_visible()
    expect(page.get_by_role("textbox", name="Companies House number")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_constitutional_status_validation_required(page: Page):
    """Test that constitutional status is required."""
    navigate_to_lsp_details(page)

    # Fill other required fields but not constitutional status
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Continue").click()

    # Should show validation error
    expect(page.get_by_text("Error: Select the constitutional status")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_companies_house_number_validation_format(page: Page):
    """Test that Companies House number validates format."""
    navigate_to_lsp_details(page)

    # Fill required fields and invalid Companies House number
    page.get_by_role("radio", name="Limited company").click()
    page.get_by_role("textbox", name="Companies House number").fill("INVALID")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Companies House number must be 8 characters")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_companies_house_number_valid_format(page: Page):
    """Test that valid Companies House number is accepted."""
    navigate_to_lsp_details(page)

    # Fill all required fields with valid data
    page.get_by_role("radio", name="Limited company").click()
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should not show validation error and should navigate away
    expect(page.get_by_text("Error: Companies House number must be 8 characters")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_indemnity_date_future_date_validation(page: Page):
    """Test that future dates show validation errors."""
    navigate_to_lsp_details(page)

    # Fill required fields and future date
    page.get_by_role("radio", name="Partnership").click()
    page.locator("input[id='indemnity_received_date-day']").fill("1")
    page.locator("input[id='indemnity_received_date-month']").fill("1")
    page.locator("input[id='indemnity_received_date-year']").fill("2030")  # Future date
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Date must be today or in the past")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_indemnity_date_invalid_date_validation(page: Page):
    """Test that invalid dates show validation errors."""
    navigate_to_lsp_details(page)

    # Fill required fields and invalid date
    page.get_by_role("radio", name="Partnership").click()
    page.locator("input[id='indemnity_received_date-day']").fill("32")  # Invalid day
    page.locator("input[id='indemnity_received_date-month']").fill("13")  # Invalid month
    page.locator("input[id='indemnity_received_date-year']").fill("2023")
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(page.get_by_text("Error: Date must be a real date")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_indemnity_date_valid_past_date(page: Page):
    """Test that past dates are accepted."""
    navigate_to_lsp_details(page)

    # Fill all fields with valid past date
    page.get_by_role("radio", name="Partnership").click()
    page.locator("input[id='indemnity_received_date-day']").fill("1")
    page.locator("input[id='indemnity_received_date-month']").fill("1")
    page.locator("input[id='indemnity_received_date-year']").fill("2020")  # Past date
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Should not show date validation error and should navigate away
    expect(page.get_by_text("Error: Date must be today or in the past")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_successful_form_submission_with_all_fields(page: Page):
    """Test successful form submission with all fields filled."""
    navigate_to_lsp_details(page)

    # Fill all fields with valid data
    page.get_by_role("radio", name="Limited company").click()
    page.locator("input[id='indemnity_received_date-day']").fill("15")
    page.locator("input[id='indemnity_received_date-month']").fill("6")
    page.locator("input[id='indemnity_received_date-year']").fill("2023")
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Submit").click()


@pytest.mark.usefixtures("live_server")
def test_minimal_valid_form_submission(page: Page):
    """Test successful form submission with only required fields."""
    navigate_to_lsp_details(page)

    # Fill only required fields
    page.get_by_role("radio", name="Sole practitioner").click()
    page.get_by_role("textbox", name="Companies House number").fill("AB123456")
    page.get_by_role("button", name="Submit").click()


@pytest.mark.usefixtures("live_server")
def test_indemnity_date_optional(page: Page):
    """Test that indemnity date is optional."""
    navigate_to_lsp_details(page)

    # Fill only required fields, leave indemnity date empty
    page.get_by_role("radio", name="Charity").click()
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Submit").click()
