import pytest
from playwright.sync_api import expect

from tests.functional_tests.utils import definition_list_to_dict


def navigate_to_inactive_office_page(page):
    """Helper function to navigate to an office page via UI flow."""
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()
    page.get_by_role("link", name="Offices").click()
    page.get_by_role("link", name="1A001L").click()


def navigate_to_active_office_page(page):
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="BIRMINGHAM LEGAL AID CENTRE").click()
    page.get_by_role("link", name="Offices").click()
    page.get_by_role("link", name="6A002L").click()


@pytest.mark.usefixtures("live_server")
def test_view_office_page_loads(page):
    """Test that the office page loads with correct information."""
    navigate_to_inactive_office_page(page)

    # Check page title and office code
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()
    expect(page.locator("span.govuk-caption-xl")).to_contain_text("SMITH & PARTNERS SOLICITORS")

    # Check status table is present
    expect(page.get_by_text("Active", exact=True).first).to_be_visible()
    expect(page.get_by_text("Payments on hold", exact=True).first).to_be_visible()
    expect(page.get_by_text("Intervened", exact=True).first).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_office_navigation_tabs(page):
    """Test that office navigation tabs are displayed."""
    navigate_to_active_office_page(page)

    # Check sub-navigation tabs
    expect(page.get_by_role("link", name="Overview")).to_be_visible()
    expect(page.get_by_role("link", name="Contact")).to_be_visible()
    expect(page.get_by_role("link", name="Bank accounts and payment")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_office_overview_section(page):
    """Test that office overview section displays correctly."""
    navigate_to_inactive_office_page(page)

    # Check overview section
    expect(page.get_by_role("heading", name="Overview")).to_be_visible()

    # Check overview content
    overview_list = definition_list_to_dict(page, "h2:has-text('Overview') + dl")
    assert overview_list["Parent provider"] == "SMITH & PARTNERS SOLICITORS"
    assert overview_list["Account number"] == "1A001L"
    assert overview_list["Head office"] == "Yes"


@pytest.mark.usefixtures("live_server")
def test_view_office_parent_provider_link(page):
    """Test that parent provider link navigates correctly."""
    navigate_to_inactive_office_page(page)

    # Click on parent provider link in overview section
    page.locator("#main-content").get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

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
    navigate_to_inactive_office_page(page)

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
    navigate_to_inactive_office_page(page)
    page.get_by_role("link", name="Bank accounts and payment").click()

    expect(page.get_by_role("definition").filter(has_text="Payment method")).to_be_visible()
    expect(page.get_by_role("link", name="Enter payment method")).to_be_visible()

    expect(page.get_by_role("definition").filter(has_text="VAT registration number")).to_be_visible()
    expect(page.get_by_text("GB123456789")).to_be_visible()
    expect(page.get_by_role("link", name="Change   VAT registration")).to_be_visible()

    expect(page.get_by_text("Smith & Partners Solicitors Client Account Change bank account (Smith &")).to_be_visible()
    expect(page.get_by_role("definition").filter(has_text="Smith & Partners Solicitors")).to_be_visible()
    expect(page.get_by_text("12345678", exact=True)).to_be_visible()
    expect(page.get_by_text("203045")).to_be_visible()

    # Do not show 'Add bank account' button if there is an account
    expect(page.get_by_role("button", name="Add bank account")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_contact(page):
    navigate_to_inactive_office_page(page)
    page.get_by_role("link", name="Contact").click()

    expect(page.get_by_role("heading", name="Office contact details")).to_be_visible()

    expect(page.get_by_text("1 Skyscraper,1 Some Road,")).to_be_visible()
    expect(page.get_by_role("link", name="Change   address")).to_be_visible()

    expect(page.get_by_text("sarah.johnson@smithpartners.").first).to_be_visible()
    expect(page.get_by_role("link", name="Change   email address")).to_be_visible()

    expect(page.get_by_text("123 4567").first).to_be_visible()
    expect(page.get_by_role("link", name="Change   telephone number")).to_be_visible()

    expect(page.get_by_text("DX number", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Enter DX number")).to_be_visible()

    expect(page.get_by_text("DX centre", exact=True)).to_be_visible()
    expect(page.get_by_role("link", name="Enter DX centre")).to_be_visible()

    # View more detailed liaison manager info
    expect(page.get_by_role("heading", name="Contact", exact=True)).to_be_visible()
    expect(page.get_by_role("heading", name="Sarah Johnson")).to_be_visible()
    expect(page.get_by_text("Previous contacts")).to_be_visible()
    page.get_by_text("Previous contacts").click()
    expect(page.get_by_role("heading", name="David Smith")).to_be_visible()
    expect(page.get_by_role("heading", name="Alice Brown")).to_be_visible()


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


@pytest.mark.usefixtures("live_server")
def test_office_inactive(page):
    navigate_to_inactive_office_page(page)

    # Tag
    expect(page.get_by_text("Inactive", exact=True)).to_be_visible()

    # Status table should show "No" for Active (since inactive)
    status_table = page.locator(".govuk-summary-list").first
    expect(status_table.get_by_text("Active", exact=True)).to_be_visible()
    expect(status_table.get_by_text("No", exact=True).first).to_be_visible()

    # Check for change link on Active row
    expect(status_table.get_by_role("link", name="Change").first).to_have_attribute(
        "href", "/provider/1/office/1A001L/confirm-office-status"
    )

    # For inactive offices, "False balance" should be visible
    expect(page.get_by_text("False balance", exact=True).first).to_be_visible()

    # For inactive offices, "Referred to debt recovery" should not be visible
    expect(page.get_by_text("Referred to debt recovery", exact=True)).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_active(page):
    navigate_to_active_office_page(page)

    # Tag - should not show inactive tag
    expect(page.get_by_text("Inactive", exact=True)).not_to_be_visible()

    # Status table should be visible with Active row
    expect(page.get_by_text("Active", exact=True).first).to_be_visible()
    expect(page.get_by_text("Payments on hold", exact=True).first).to_be_visible()
    expect(page.get_by_text("Intervened", exact=True).first).to_be_visible()

    # For active offices, "Referred to debt recovery" should be visible
    expect(page.get_by_text("Referred to debt recovery", exact=True).first).to_be_visible()

    # For active offices, "False balance" should not be visible
    expect(page.get_by_text("False balance", exact=True)).not_to_be_visible()
