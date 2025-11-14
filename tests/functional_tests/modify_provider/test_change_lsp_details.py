import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def _navigate_to_provider_page(page: Page, provider_name: str):
    """Helper function to navigate to a given provider page."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    page.get_by_role("textbox", name="Find a provider").fill(provider_name)
    page.get_by_role("button", name="Search").click()

    # Click on the first provider
    page.get_by_role("link", name=provider_name).click()

    expect(page.get_by_role("heading", name=provider_name)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_lsp_details_constitutional_status(page: Page):
    _navigate_to_provider_page(page, "SMITH & PARTNERS SOLICITORS")
    page.get_by_role("link", name="Change constitutional status").click()
    expect(page.get_by_role("radio", name="Partnership", exact=True)).to_be_checked()
    page.get_by_role("radio", name="Limited Liability Partnership (LLP)").click()
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("Legal services provider overview successfully updated"))
    expect(page.get_by_text("Limited Liability Partnership (LLP)")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_lsp_details_indemnity_received_date(page: Page):
    _navigate_to_provider_page(page, "SMITH & PARTNERS SOLICITORS")
    page.get_by_role("link", name="Enter indemnity received date").click()

    expect(page.get_by_role("textbox", name="Day", exact=True)).to_be_empty()
    expect(page.get_by_role("textbox", name="Month", exact=True)).to_be_empty()
    expect(page.get_by_role("textbox", name="Year", exact=True)).to_be_empty()

    page.get_by_role("textbox", name="Day", exact=True).fill("10")
    page.get_by_role("textbox", name="Month", exact=True).fill("10")
    page.get_by_role("textbox", name="Year", exact=True).fill("2025")
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Legal services provider overview successfully updated"))
    expect(page.get_by_text("10 Oct 2025")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_lsp_details_companies_house_number(page: Page):
    _navigate_to_provider_page(page, "SMITH & PARTNERS SOLICITORS")
    page.get_by_role("link", name="Change companies House number").click()

    expect(page.get_by_role("textbox", name="Companies House number (optional)", exact=True)).to_have_value("12345678")
    page.get_by_role("textbox", name="Companies House number (optional)", exact=True).fill("09876543")
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Legal services provider overview successfully updated"))
    expect(page.get_by_text("09876543")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_lsp_details_no_changes(page: Page):
    _navigate_to_provider_page(page, "SMITH & PARTNERS SOLICITORS")

    expect(page.get_by_text("12345678")).to_be_visible()
    expect(page.get_by_text("Partnership")).to_be_visible()
    expect(page.get_by_role("link", name="Enter indemnity received date"))

    page.get_by_role("link", name="Change companies House number").click()
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("No changes made to legal services provider overview"))
    expect(page.get_by_text("12345678")).to_be_visible()
    expect(page.get_by_text("Partnership")).to_be_visible()
    expect(page.get_by_role("link", name="Enter indemnity received date"))
