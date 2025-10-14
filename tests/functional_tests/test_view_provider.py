import pytest
from playwright.sync_api import expect


@pytest.mark.usefixtures("live_server")
def test_view_provider_page_ui_loads(page):
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    expect(page.get_by_role("link", name="Offices")).to_be_visible()

    # Tags
    expect(page.locator("strong.govuk-tag", has_text="Inactive")).to_be_visible()

    # Status table - Check for status rows
    expect(page.get_by_text("Active", exact=True).first).to_be_visible()
    expect(page.get_by_text("Payments on hold", exact=True).first).to_be_visible()
    expect(page.get_by_text("Intervened", exact=True).first).to_be_visible()

    # Status table should show "No" for Active (since inactive)
    status_table = page.locator(".govuk-summary-list").first
    expect(status_table.get_by_text("No", exact=True).first).to_be_visible()

    # Check for change link on Active row - should have actual URL, not '#'
    expect(status_table.get_by_role("link", name="Change").first).to_have_attribute(
        "href", "/provider/1/confirm-provider-status"
    )

    # Overview heading
    expect(page.get_by_role("heading", name="Overview")).to_be_visible()

    # Main table
    expect(page.get_by_text("Provider name", exact=True).first).to_be_visible()
    expect(page.get_by_text("SMITH & PARTNERS SOLICITORS", exact=True).first).to_be_visible()

    expect(page.get_by_text("Provider number", exact=True).first).to_be_visible()
    expect(page.get_by_text("1", exact=True).first).to_be_visible()

    expect(page.get_by_text("Account number", exact=True).first).to_be_visible()
    expect(page.get_by_text("1A001L", exact=True).first).to_be_visible()

    expect(page.get_by_text("Constitutional status", exact=True).first).to_be_visible()
    expect(page.get_by_text("Partnership", exact=True).first).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_parent_provider(page):
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click child provider
    page.get_by_role("link", name="ALAN DAVIES").click()

    # Assert we can see the parent provider
    expect(page.get_by_text("Chambers", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="JOHNSON LEGAL SERVICES").first).to_be_visible()

    # Click parent provider
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").first.click()
    expect(page.get_by_text("Provider name", exact=True).first).to_be_visible()
    expect(page.get_by_text("JOHNSON LEGAL SERVICES", exact=True).first).to_be_visible()
    expect(page.get_by_text("Provider number", exact=True).first).to_be_visible()
    expect(page.get_by_text("2", exact=True).first).to_be_visible()
    expect(page.get_by_text("Account number", exact=True).first).to_be_visible()
    expect(page.get_by_text("2R006L", exact=True).first).to_be_visible()


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
    expect(page.get_by_text("Test provider", exact=True).first).to_be_visible()
    expect(page.get_by_text("Charity", exact=True).first).to_be_visible()
    expect(page.get_by_text("12345678", exact=True).first).to_be_visible()
    expect(page.get_by_text("Alice Johnson", exact=True).first).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_lsp_contact(page):
    page.get_by_role("button", name="Sign in").click()
    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    # Contact subpage visible on landing
    expect(page.get_by_role("heading", name="Contacts")).to_be_visible()

    # Summary list of liaison manager
    contact_section = page.locator(".govuk-summary-card").first
    expect(contact_section).to_contain_text("Job title")
    expect(contact_section).to_contain_text("Telephone number")
    expect(contact_section).to_contain_text("Email address")
    expect(contact_section).to_contain_text("Website")
    expect(contact_section).to_contain_text("Active from")
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
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click on an Advocate provider
    page.get_by_role("link", name="ALAN DAVIES").click()

    # Check Advocate-specific main table fields
    expect(page.get_by_text("Advocate name", exact=True).first).to_be_visible()
    expect(page.get_by_text("ALAN DAVIES", exact=True).first).to_be_visible()

    expect(page.get_by_text("Advocate number", exact=True).first).to_be_visible()
    expect(page.get_by_text("4", exact=True).first).to_be_visible()

    expect(page.get_by_text("Account number", exact=True).first).to_be_visible()

    # Check that Chambers link is visible and clickable
    expect(page.get_by_text("Chambers", exact=True).first).to_be_visible()
    expect(page.get_by_role("link", name="JOHNSON LEGAL SERVICES").first).to_be_visible()

    # Check for Advocate level field (even if no data)
    expect(page.get_by_text("Advocate level", exact=True).first).to_be_visible()

    # Check for SRA roll number field
    expect(page.get_by_text("Solicitors Regulation Authority roll number", exact=True).first).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_barrister_provider_main_table(page):
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click on a Barrister provider - need to navigate via Chambers first
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()

    # Click on a barrister
    page.get_by_role("link", name="Karen Sillen").click()

    # Check Barrister-specific main table fields
    expect(page.get_by_text("Barrister name", exact=True).first).to_be_visible()
    expect(page.get_by_text("Karen Sillen", exact=True).first).to_be_visible()

    expect(page.get_by_text("Barrister number", exact=True).first).to_be_visible()
    expect(page.get_by_text("13", exact=True).first).to_be_visible()

    expect(page.get_by_text("Account number", exact=True).first).to_be_visible()

    # Check that Chambers link is visible and clickable
    expect(page.get_by_text("Chambers", exact=True).first).to_be_visible()
    expect(page.get_by_role("link", name="JOHNSON LEGAL SERVICES").first).to_be_visible()

    # Check for Barrister level field
    expect(page.get_by_text("Barrister level", exact=True).first).to_be_visible()

    # Check for Bar Council roll number field
    expect(page.get_by_text("Bar Council roll number", exact=True).first).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_chambers_provider_main_table(page):
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click on a Chambers provider
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    # Check Chambers-specific main table fields (simplified compared to LSP)
    expect(page.get_by_text("Provider name", exact=True).first).to_be_visible()
    expect(page.get_by_text("JOHNSON LEGAL SERVICES", exact=True).first).to_be_visible()

    expect(page.get_by_text("Provider number", exact=True).first).to_be_visible()
    expect(page.get_by_text("2", exact=True).first).to_be_visible()

    expect(page.get_by_text("Account number", exact=True).first).to_be_visible()


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


@pytest.mark.usefixtures("live_server")
def test_barrister_without_office(page):
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("link", name="Sophie Lelièvre").click()
    page.get_by_role("link", name="Bank accounts and payment").click()
    expect(page.get_by_text("Warning Bank account")).to_be_visible()
    expect(page.get_by_role("strong")).to_contain_text(
        "Warning Bank account information not available. Contact mapd@justice.gov.uk for more information."
    )
