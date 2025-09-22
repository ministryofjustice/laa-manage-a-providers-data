import pytest
from playwright.sync_api import expect


def navigate_to_office_page(page):
    """Helper function to navigate to an office page via UI flow."""
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()
    page.get_by_role("link", name="Offices").click()
    page.get_by_role("link", name="1A001L").click()


@pytest.mark.usefixtures("live_server")
def test_view_office_page_loads(page):
    """Test that the office page loads with correct information."""
    navigate_to_office_page(page)

    # Check page title and office code
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()
    expect(page.locator("span.govuk-caption-xl")).to_contain_text("SMITH & PARTNERS SOLICITORS")

    # Check office buttons are present
    expect(page.get_by_role("button", name="Make inactive")).to_be_visible()
    expect(page.get_by_role("button", name="Hold payments")).to_be_visible()
    expect(page.get_by_role("button", name="Record office intervention")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_office_navigation_tabs(page):
    """Test that office navigation tabs are displayed."""
    navigate_to_office_page(page)

    # Check sub-navigation tabs
    expect(page.get_by_role("link", name="Overview")).to_be_visible()
    expect(page.get_by_role("link", name="Contact")).to_be_visible()
    expect(page.get_by_role("link", name="Bank accounts and payment")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_office_overview_section(page):
    """Test that office overview section displays correctly."""
    navigate_to_office_page(page)

    # Check overview section
    expect(page.get_by_role("heading", name="Overview")).to_be_visible()

    # Check overview content
    expect(page.get_by_role("rowheader", name="Parent provider")).to_be_visible()
    expect(page.get_by_role("cell", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Account number")).to_be_visible()
    expect(page.get_by_role("row", name="Account number 1A001L").get_by_role("cell", name="1A001L")).to_be_visible()

    expect(page.get_by_role("rowheader", name="Head office")).to_be_visible()
    expect(page.get_by_role("cell", name="Yes")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_office_parent_provider_link(page):
    """Test that parent provider link navigates correctly."""
    navigate_to_office_page(page)

    # Click on parent provider link in overview section
    page.get_by_role("row", name="Parent provider SMITH & PARTNERS SOLICITORS").get_by_role(
        "link", name="SMITH & PARTNERS SOLICITORS"
    ).click()

    # Should navigate to provider page
    expect(page.get_by_role("heading", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_page_navigation_from_offices_list(page):
    """Test navigation from offices list to individual office page."""
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()
    page.get_by_role("link", name="Offices").click()

    # Click on office code link
    page.get_by_role("link", name="1A001L").click()

    # Should navigate to office page
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_breadcrumbs(page):
    """Test that office page has correct breadcrumbs and link destinations."""
    navigate_to_office_page(page)

    # Check breadcrumb links are visible
    expect(page.get_by_label("Breadcrumb").get_by_role("link", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("link", name="Office: 1A001L")).to_be_visible()

    # Test breadcrumb navigation - click on provider name should go to provider page
    page.get_by_label("Breadcrumb").get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    # Should navigate to provider page
    expect(page.get_by_role("heading", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("link", name="Contact")).to_be_visible()  # Provider nav tabs


@pytest.mark.usefixtures("live_server")
def test_office_bank_payment_details(page):
    navigate_to_office_page(page)
    page.get_by_role("link", name="Bank accounts and payment").click()

    expect(page.get_by_role("rowheader", name="Payment method")).to_be_visible()
    expect(page.get_by_role("link", name="Enter payment method")).to_be_visible()

    expect(page.get_by_role("cell", name="GB123456789")).to_be_visible()
    expect(page.get_by_role("link", name="Change   VAT registration")).to_be_visible()

    expect(page.get_by_text("Smith & Partners Solicitors Client Account Change bank account (Smith &")).to_be_visible()
    expect(page.get_by_role("definition").filter(has_text="Smith & Partners Solicitors")).to_be_visible()
    expect(page.get_by_text("12345678", exact=True)).to_be_visible()
    expect(page.get_by_text("203045")).to_be_visible()

    expect(page.get_by_role("button", name="Add bank account")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_contact(page):
    navigate_to_office_page(page)
    page.get_by_role("link", name="Contact").click()
    expect(page.get_by_role("heading", name="Sarah Johnson")).to_be_visible()
    expect(page.get_by_role("term").filter(has_text="Job title")).to_be_visible()
    expect(page.get_by_role("definition").filter(has_text="Liaison manager")).to_be_visible()
    expect(page.get_by_role("term").filter(has_text="Telephone number")).to_be_visible()
    expect(page.get_by_text("123 4567")).to_be_visible()
    expect(page.get_by_role("term").filter(has_text="Email address")).to_be_visible()
    expect(page.get_by_text("sarah.johnson@smithpartners.")).to_be_visible()
    expect(page.get_by_text("Show 2 additional contacts")).to_be_visible()

    page.get_by_text("Show 2 additional contacts").click()
    expect(page.get_by_role("link", name="Change liaison manager  (David Smith)")).to_be_visible()
    expect(page.get_by_role("link", name="Change liaison manager  (Alice Brown)")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_no_vat_registration_number(page):
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    page.get_by_role("link", name="METROPOLITAN LAW CENTRE").click()
    page.get_by_role("link", name="Offices").click()
    page.get_by_role("link", name="3A001L").click()
    page.get_by_role("link", name="Bank accounts and payment").click()
    expect(page.get_by_role("link", name="Enter vat registration number")).to_be_visible()
