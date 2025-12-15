import pytest
from flask import url_for
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import definition_list_to_dict


def navigate_to_existing_provider(page: Page, firm_id: int = 1):
    """Helper function to navigate to an existing provider's details page."""
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click on the first provider (Smith & Partners Solicitors - firm ID 1)
    page.get_by_role("link", name="Smith & Partners Solicitors").click()

    # Verify we're on the provider details page
    expect(page.get_by_role("heading", name="Smith & Partners Solicitors")).to_be_visible()


def navigate_to_change_contract_manager_form(page: Page, firm_id: int = 1, firm_office_code: str = "1A001L"):
    """Helper function to navigate to the change contract manager form."""
    # Direct navigation to the change liaison manager form
    page.goto(url_for("main.change_office_contract_manager", firm=firm_id, office=firm_office_code, _external=True))


@pytest.mark.usefixtures("live_server")
def test_change_contract_manager_form_loads_correctly(page: Page):
    """Test that the change liaison manager form loads with correct elements."""
    navigate_to_change_contract_manager_form(page)

    # Check page title and heading
    expect(page.get_by_role("heading", name="Assign contract manager")).to_be_visible()
    expect(page.get_by_role("textbox", name="Search for a contract manager")).to_be_visible()
    expect(page.get_by_role("button", name="Unknown: Skip this step")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_contract_manager_success(page: Page):
    """Test that the change contract manager form successfully loads with correct elements."""
    navigate_to_change_contract_manager_form(page)

    # Select a contract manger
    page.get_by_role("row", name="Select this row  Alice Johnson").get_by_label("Select this row").check()
    page.get_by_role("button", name="Submit").click()

    # See the success flash...
    expect(page.get_by_label("Success").locator("div").filter(has_text="Contract manager for ")).to_be_visible()

    # ...and the contract manager is set.
    overview_list = definition_list_to_dict(page, "h2:has-text('Overview') + dl")
    assert overview_list["Contract manager"] == "Alice Johnson"


@pytest.mark.usefixtures("live_server")
def test_change_contract_manager_skip_sets_default(page: Page):
    """Test that the change contract manager form sets the default contract manager when skipped."""
    navigate_to_change_contract_manager_form(page)

    # Use the Skip button to set the default...
    page.get_by_role("button", name="Unknown: Skip this step").click()

    # ...and see the contract manager is unset and can be changed.
    expect(page.get_by_role("link", name="Assign contract manager")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_contract_manager_on_head_office_changes_firm_overview(page: Page):
    """Test that clicking skip will set the default contract manager even if a contract manager is selected."""
    page.get_by_role("link", name="Manage a provider's data").click()
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Birmingham Legal Aid Centre").click()
    expect(page.get_by_role("heading", name="Birmingham Legal Aid Centre")).to_be_visible()

    # Check the contract manager shown for the firm...
    firm_overview = definition_list_to_dict(page, "h2:has-text('Overview') + dl")
    assert firm_overview["Contract manager"] == "Christopher Lee"
    # ...is taken from the head office...
    page.get_by_role("link", name="Offices").click()
    page.get_by_role("link", name="6A001L").click()
    office_overview = definition_list_to_dict(page, "h2:has-text('Overview') + dl")
    # ...head office...
    assert office_overview["Head office"] == "Yes"
    # ...has the contract manager.
    assert office_overview["Contract manager"] == "Christopher Lee"

    # When changing the contract manager on the head office...
    page.get_by_role("link", name="Change   contract manager").click()
    # ...to Alice Johnson...
    page.get_by_role("row", name="Select this row  Alice Johnson").get_by_label("Select this row").check()
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_label("Success").locator("div").filter(has_text="Contract manager for 6A001L")).to_be_visible()
    # ...we see on the parent firm...
    page.get_by_role("link", name="Manage a provider's data").click()
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Birmingham Legal Aid Centre").click()
    # ...the contract manager is shown as Alice Johnson.
    office_overview = definition_list_to_dict(page, "h2:has-text('Overview') + dl")
    assert office_overview["Contract manager"] == "Alice Johnson"
