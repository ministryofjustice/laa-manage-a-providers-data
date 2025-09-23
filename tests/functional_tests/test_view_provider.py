import pytest
from playwright.sync_api import expect


@pytest.mark.usefixtures("live_server")
def test_view_provider_page_ui_loads(page):
    page.get_by_role("button", name="Sign in").click()

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


@pytest.mark.usefixtures("live_server")
def test_view_parent_provider(page):
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click child provider
    page.get_by_role("link", name="DAVIES & ASSOCIATES").click()

    # Assert we can see the parent provider
    expect(page.get_by_role("rowheader", name="Chambers")).to_be_visible()
    expect(page.get_by_role("row", name="Chambers JOHNSON LEGAL SERVICES").get_by_role("link")).to_be_visible()

    # Click parent provider
    page.get_by_role("row", name="Chambers JOHNSON LEGAL SERVICES").get_by_role("link").click()
    expect(page.get_by_role("rowheader", name="Provider name")).to_be_visible()
    expect(page.get_by_role("cell", name="JOHNSON LEGAL SERVICES")).to_be_visible()
    expect(page.get_by_role("rowheader", name="Provider number")).to_be_visible()
    expect(page.get_by_role("cell", name="2", exact=True)).to_be_visible()
    expect(page.get_by_role("rowheader", name="Account number")).to_be_visible()
    expect(page.get_by_role("cell", name="2R006L")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_new_lsp(page):
    # Add a legal services provider
    page.get_by_role("button", name="Sign in").click()
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
    page.get_by_role("button", name="Continue").click()

    # Add head office information
    page.get_by_role("textbox", name="Address line 1").fill("Address line 1")
    page.get_by_role("textbox", name="Town or city").fill("London")
    page.get_by_role("textbox", name="Postcode").fill("SW1A 1AA")
    page.get_by_role("button", name="Continue").click()

    # Add VAT number
    page.get_by_role("textbox").fill("123456789")
    page.get_by_role("button", name="Continue").click()

    # Skip adding bank account information
    page.get_by_role("button", name="Cheque payment: Skip this step").click()

    # Add liaison manager details
    page.get_by_role("textbox", name="First name").fill("Bob")
    page.get_by_role("textbox", name="Last name").fill("Jones")
    page.get_by_role("textbox", name="Email address").fill("bob.jones@testlsp.com")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("button", name="Continue").click()

    # Assign a contract manager
    page.get_by_role("textbox", name="Search for a contract manager").fill("Alice")
    page.get_by_role("button", name="Search").click()
    # Select the contract manager
    page.get_by_role("radio", name="Select this row").click()
    page.get_by_role("button", name="Submit").click()

    # Assert our LSP information is displayed correctly
    expect(page.get_by_text("New legal services provider successfully created")).to_be_visible()
    expect(page.get_by_role("alert", name="Success").locator("div").first).to_be_visible()
    expect(page.get_by_text("Legal services provider", exact=True)).to_be_visible()
    expect(page.get_by_role("heading", name="Test provider")).to_be_visible()
    expect(page.get_by_role("cell", name="Test provider")).to_be_visible()
    expect(page.get_by_role("cell", name="Charity")).to_be_visible()
    expect(page.get_by_role("cell", name="12345678")).to_be_visible()
    expect(page.get_by_role("cell", name="Alice Johnson")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_lsp_contact(page):
    page.get_by_role("button", name="Sign in").click()
    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    # Contact subpage visible on landing
    expect(page.get_by_role("heading", name="Contacts")).to_be_visible()

    # Summary list of liaison manager
    expect(page.locator("dl")).to_contain_text("Job title")
    expect(page.locator("dl")).to_contain_text("Telephone number")
    expect(page.locator("dl")).to_contain_text("Email address")
    expect(page.locator("dl")).to_contain_text("Website")
    expect(page.locator("dl")).to_contain_text("Active from")
    expect(page.get_by_role("link", name="Change liaison manager")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_back_link_lsp(page):
    page.get_by_role("button", name="Sign in").click()
    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    page.get_by_role("link", name="Back to all providers").click()
    expect(page.get_by_role("heading", name="Provider records")).to_be_visible()

    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    page.get_by_role("link", name="Offices").click()
    page.get_by_role("link", name="Back to all providers").click()
    expect(page.get_by_role("heading", name="Provider records")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_advocate_provider_main_table(page):
    page.get_by_role("button", name="Start now").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click on an Advocate provider
    page.get_by_role("link", name="DAVIES & ASSOCIATES").click()

    # Check Advocate-specific main table fields
    expect(page.get_by_role("rowheader", name="Advocate name")).to_be_visible()
    expect(page.get_by_role("cell", name="DAVIES & ASSOCIATES")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Advocate number")).to_be_visible()
    expect(page.get_by_role("cell", name="4", exact=True)).to_be_visible()

    expect(page.get_by_role("rowheader", name="Account number")).to_be_visible()

    # Check that Chambers link is visible and clickable
    expect(page.get_by_role("rowheader", name="Chambers")).to_be_visible()
    expect(page.get_by_role("cell").locator("a[href*='/provider/2']")).to_be_visible()

    # Check for Advocate level field (even if no data)
    expect(page.get_by_role("rowheader", name="Advocate level")).to_be_visible()

    # Check for SRA roll number field
    expect(page.get_by_role("rowheader", name="Solicitors Regulation Authority roll number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_barrister_provider_main_table(page):
    page.get_by_role("button", name="Start now").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click on a Barrister provider - need to navigate via Chambers first
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()

    # Click on a barrister
    page.get_by_role("link", name="Karen Sillen").click()

    # Check Barrister-specific main table fields
    expect(page.get_by_role("rowheader", name="Barrister name")).to_be_visible()
    expect(page.get_by_role("cell", name="Karen Sillen")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Barrister number")).to_be_visible()
    expect(page.get_by_role("cell", name="13", exact=True)).to_be_visible()

    expect(page.get_by_role("rowheader", name="Account number")).to_be_visible()

    # Check that Chambers link is visible and clickable
    expect(page.get_by_role("rowheader", name="Chambers")).to_be_visible()
    expect(page.get_by_role("cell").locator("a[href*='/provider/2']")).to_be_visible()

    # Check for Barrister level field
    expect(page.get_by_role("rowheader", name="Barrister level")).to_be_visible()

    # Check for Bar Council roll number field
    expect(page.get_by_role("rowheader", name="Bar Council roll number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_chambers_provider_main_table(page):
    page.get_by_role("button", name="Start now").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click on a Chambers provider
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    # Check Chambers-specific main table fields (simplified compared to LSP)
    expect(page.get_by_role("rowheader", name="Provider name")).to_be_visible()
    expect(page.get_by_role("cell", name="JOHNSON LEGAL SERVICES")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Provider number")).to_be_visible()
    expect(page.get_by_role("cell", name="2", exact=True)).to_be_visible()

    expect(page.get_by_role("rowheader", name="Account number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_back_link_chambers(page):
    page.get_by_role("button", name="Sign in").click()
    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    page.get_by_role("link", name="Back to all providers").click()
    expect(page.get_by_role("heading", name="Provider records")).to_be_visible()

    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("link", name="Back to all providers").click()
    expect(page.get_by_role("heading", name="Provider records")).to_be_visible()
