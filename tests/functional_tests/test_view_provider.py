import pytest
from playwright.sync_api import expect


@pytest.mark.usefixtures("live_server")
def test_view_provider_page_ui_loads(page):
    page.get_by_role("button", name="Start now").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    expect(page.get_by_role("link", name="Offices")).to_be_visible()

    # Buttons
    expect(page.get_by_role("button", name="Make provider inactive")).to_be_visible()
    # Main table
    expect(page.get_by_role("rowheader", name="Provider name")).to_be_visible()
    expect(page.get_by_role("cell", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Provider number")).to_be_visible()
    expect(page.get_by_role("cell", name="1", exact=True)).to_be_visible()

    expect(page.get_by_role("rowheader", name="Account number")).to_be_visible()
    expect(page.get_by_role("cell", name="1A001L")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Constitutional status")).to_be_visible()
    expect(page.get_by_role("cell", name="Partnership")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Not for profit organisation")).to_be_visible()
    expect(page.get_by_role("cell", name="No", exact=True)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_parent_provider(page):
    page.get_by_role("button", name="Start now").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click child provider
    page.get_by_role("link", name="DAVIES & ASSOCIATES").click()

    # Assert we can see the parent provider
    expect(page.get_by_role("rowheader", name="Parent provider name")).to_be_visible()
    expect(page.get_by_role("cell", name="JOHNSON LEGAL SERVICES")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Parent provider number")).to_be_visible()
    expect(page.get_by_role("cell", name="2")).to_be_visible()

    # Click parent provider
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    expect(page.get_by_role("rowheader", name="Provider name")).to_be_visible()
    expect(page.get_by_role("cell", name="JOHNSON LEGAL SERVICES")).to_be_visible()
    expect(page.get_by_role("rowheader", name="Provider number")).to_be_visible()
    expect(page.get_by_role("cell", name="2", exact=True)).to_be_visible()
    expect(page.get_by_role("rowheader", name="Account number")).to_be_visible()
    expect(page.get_by_role("cell", name="2R006L")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_new_lsp(page):
    # Add a legal services provider
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Add a new parent provider").click()
    page.get_by_role("textbox", name="Provider name").fill("Test provider")
    page.get_by_role("radio", name="Legal services provider").check()
    page.get_by_role("button", name="Continue").click()
    page.get_by_role("radio", name="Charity").check()
    page.get_by_role("textbox", name="Day").click()
    page.get_by_role("textbox", name="Day").fill("1")
    page.get_by_role("textbox", name="Month").fill("1")
    page.get_by_role("textbox", name="Year").fill("2020")
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Submit").click()

    # Add head office information
    page.get_by_role("textbox", name="Address line 1").fill("Address line 1")
    page.get_by_role("textbox", name="Town or city").fill("London")
    page.get_by_role("textbox", name="Postcode").fill("SW1A 1AA")
    page.get_by_role("button", name="Submit").click()

    # Add VAT number
    page.get_by_role("textbox").fill("123456789")
    page.get_by_role("button", name="Submit").click()

    # Skip adding bank account information
    page.get_by_role("button", name="Cheque payment: Skip this step").click()

    # Add liaison manager information
    page.get_by_role("textbox", name="Address line 1").fill("123 Provider Street")
    page.get_by_role("textbox", name="Town or city").fill("Provider City")
    page.get_by_role("textbox", name="Postcode").fill("PR1 2MB")
    page.get_by_role("textbox", name="Email address").fill("contact@testprovider.com")
    # Leave optional fields empty: address_line_2-4, county, telephone number, DX number & centre
    page.get_by_role("button", name="Submit").click()

    # Assert our LSP information is displayed correctly
    expect(page.get_by_text("New legal services provider successfully created")).to_be_visible()
    expect(page.get_by_role("alert", name="Success").locator("div").first).to_be_visible()
    expect(page.get_by_text("Legal services provider", exact=True)).to_be_visible()
    expect(page.get_by_role("heading", name="Test provider")).to_be_visible()
    expect(page.get_by_role("cell", name="Test provider")).to_be_visible()
    expect(page.get_by_role("cell", name="Charity")).to_be_visible()
    expect(page.get_by_role("cell", name="/01/2020")).to_be_visible()
    expect(page.get_by_role("cell", name="12345678")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_lsp_contact(page):
    page.get_by_role("button", name="Start now").click()
    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    page.get_by_role("link", name="METROPOLITAN LAW CENTRE").click()

    # Contact subpage visible on landing
    expect(page.get_by_role("heading", name="Contacts")).to_be_visible()

    # Summary list of liaison manager
    expect(page.locator("dl")).to_contain_text("Job title")
    expect(page.locator("dl")).to_contain_text("Telephone number")
    expect(page.locator("dl")).to_contain_text("Email address")
    expect(page.locator("dl")).to_contain_text("Website")
    expect(page.locator("dl")).to_contain_text("Active from")
    expect(page.get_by_role("link", name="Change liaison manager")).to_be_visible()
