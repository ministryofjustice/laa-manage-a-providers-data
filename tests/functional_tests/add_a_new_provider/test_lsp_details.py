import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_lsp_details(page: Page):
    page.goto(url_for("main.add_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test LSP")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Additional details")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_lsp_details_page_loads_via_ui(page: Page):
    navigate_to_lsp_details(page)
    expect(page.get_by_text("Test LSP")).to_be_visible()
    expect(page.get_by_role("combobox", name="Constitutional status")).to_be_visible()
    expect(page.get_by_role("textbox", name="Day")).to_be_visible()
    expect(page.get_by_role("textbox", name="Month")).to_be_visible()
    expect(page.get_by_role("textbox", name="Year")).to_be_visible()
    expect(page.get_by_role("radio", name="Yes").first).to_be_visible()
    expect(page.get_by_role("button", name="Continue")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_non_profit_organisation_validation_required(page: Page):
    """Test that non-profit organisation question is required."""
    navigate_to_lsp_details(page)

    # Fill constitutional status but not non-profit question
    page.get_by_label("Constitutional status").select_option("partnership")
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text("Error: Select yes if the provider is a not for profit organisation")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_high_risk_supplier_optional(page: Page):
    """Test that high risk supplier question is optional."""
    navigate_to_lsp_details(page)

    # Fill required fields but not optional high risk supplier
    page.get_by_label("Constitutional status").select_option("partnership")
    page.get_by_role("group", name="Is the provider a not for profit organisation?").get_by_label("No").check()
    page.get_by_role("button", name="Continue").click()


@pytest.mark.usefixtures("live_server")
def test_companies_house_number_validation_format(page: Page):
    """Test that Companies House number validates format."""
    navigate_to_lsp_details(page)

    page.get_by_label("Constitutional status").select_option("limited company")
    page.get_by_role("group", name="Is the provider a not for profit organisation?").get_by_label("No").check()
    page.get_by_role("textbox", name="Companies House number").fill("INVALID")
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text("Error: Enter a valid Companies House number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_companies_house_number_valid_format(page: Page):
    """Test that valid Companies House number is accepted."""
    navigate_to_lsp_details(page)

    page.get_by_label("Constitutional status").select_option("limited company")
    page.get_by_role("group", name="Is the provider a not for profit organisation?").get_by_label("No").check()
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text("Error: Enter a valid Companies House number")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_companies_house_number_validation(page: Page):
    """Test that Companies House number is required."""
    navigate_to_lsp_details(page)

    page.get_by_label("Constitutional status").select_option("limited company")
    page.get_by_role("group", name="Is the provider a not for profit organisation?").get_by_label("No").check()
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text("Error: Enter the Companies House number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_indemnity_date_future_date_validation(page: Page):
    """Test that future dates show validation errors."""
    navigate_to_lsp_details(page)

    page.get_by_label("Constitutional status").select_option("partnership")
    page.get_by_role("group", name="Is the provider a not for profit organisation?").get_by_label("No").check()
    page.locator("input[id='indemnity_received_date-day']").fill("1")
    page.locator("input[id='indemnity_received_date-month']").fill("1")
    page.locator("input[id='indemnity_received_date-year']").fill("2030")  # Future date
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Continue").click()

    expect(page.get_by_text("Error: Date must be today or in the past")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_indemnity_date_invalid_date_validation(page: Page):
    """Test that invalid dates show validation errors."""
    navigate_to_lsp_details(page)

    # Fill required fields and invalid date
    page.get_by_label("Constitutional status").select_option("partnership")
    page.get_by_role("group", name="Is the provider a not for profit organisation?").get_by_label("No").check()
    page.locator("input[id='indemnity_received_date-day']").fill("32")  # Invalid day
    page.locator("input[id='indemnity_received_date-month']").fill("13")  # Invalid month
    page.locator("input[id='indemnity_received_date-year']").fill("2023")
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Continue").click()

    # Should show validation error
    expect(page.get_by_text("Error: Date must be a real date")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_indemnity_date_valid_past_date(page: Page):
    """Test that past dates are accepted."""
    navigate_to_lsp_details(page)

    page.get_by_label("Constitutional status").select_option("partnership")
    page.get_by_role("group", name="Is the provider a not for profit organisation?").get_by_label("No").check()
    page.locator("input[id='indemnity_received_date-day']").fill("1")
    page.locator("input[id='indemnity_received_date-month']").fill("1")
    page.locator("input[id='indemnity_received_date-year']").fill("2020")  # Past date
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Continue").click()


@pytest.mark.usefixtures("live_server")
def test_successful_form_submission(page: Page):
    """Test successful form submission with all valid data."""
    navigate_to_lsp_details(page)

    # Fill all fields with valid data
    page.get_by_label("Constitutional status").select_option("limited company")
    page.locator("input[id='indemnity_received_date-day']").fill("15")
    page.locator("input[id='indemnity_received_date-month']").fill("6")
    page.locator("input[id='indemnity_received_date-year']").fill("2023")
    page.get_by_role("radio", name="No").first.click()  # No
    page.get_by_role("radio", name="Yes").last.click()  # Yes for high risk
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Continue").click()


@pytest.mark.usefixtures("live_server")
def test_minimal_valid_form_submission(page: Page):
    """Test successful form submission with only required fields."""
    navigate_to_lsp_details(page)

    page.get_by_label("Constitutional status").select_option("sole practitioner")
    page.get_by_role("group", name="Is the provider a not for profit organisation?").get_by_label("Yes").check()
    page.get_by_role("button", name="Continue").click()
