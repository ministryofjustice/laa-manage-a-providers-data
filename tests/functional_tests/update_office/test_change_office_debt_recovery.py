import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import definition_list_to_dict, navigate_to_provider_page


def change_and_confirm_debt_recovery(
    page: Page, debt_recovery: str, office_code: str = None, provider_name: str = None
):
    page.get_by_role("link", name="Change referred to debt recovery").click()
    expect(page.get_by_role("heading", name="Has this office been referred to the Debt Recovery Unit?", exact=True))
    page.get_by_role("radio", name=debt_recovery).click()
    page.get_by_role("button", name="submit").click()
    if office_code:
        text = f"{office_code} is referred to the Debt Recovery Unit"
        if debt_recovery.lower() in "no":
            text = f"Office {office_code} is not referred to the Debt Recovery Unit."
        expect(page.get_by_text(text)).to_be_visible()
    elif provider_name:
        text = f"{provider_name} is referred to the Debt Recovery Unit"
        if debt_recovery.lower() in "no":
            text = f"{provider_name} is not referred to the Debt Recovery Unit."
        expect(page.get_by_text(text)).to_be_visible()

    # If we are changing from yes to no then we will be taken to the `assign contract manager` page which
    # does not have the status table
    if debt_recovery.lower() == "yes":
        dl = definition_list_to_dict(page, ".status-table")
        assert dl["Referred to debt recovery"] == "Yes"


@pytest.mark.usefixtures("live_server")
def test_change_office_debt_recovery_visible(page: Page):
    # `Referred to debt recovery` should be visible for active office
    navigate_to_provider_page(page, provider_name="BIRMINGHAM LEGAL AID CENTRE", office_code="6A001L")
    expect(page.get_by_text("Referred to debt recovery", exact=True)).to_be_visible()

    # `Referred to debt recovery` should NOT be visible for active office
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    expect(page.get_by_text("Referred to debt recovery", exact=True)).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_debt_recovery_no_change__no(page: Page):
    """Test correct message when submit a default form without any change"""

    navigate_to_provider_page(page, provider_name="BIRMINGHAM LEGAL AID CENTRE", office_code="6A001L")
    page.get_by_role("link", name="Change referred to debt recovery").click()
    page.get_by_role("button", name="submit").click()
    expect(
        page.get_by_role(
            "link",
            name="Select yes if the office has been referred to the Debt Recovery Unit. Cancel if you do not want to change the answer.",
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_debt_recovery_no_change__yes(page: Page):
    """Test correct message when submit a default form without any change"""

    navigate_to_provider_page(page, provider_name="BIRMINGHAM LEGAL AID CENTRE", office_code="6A001L")
    # First put the office into debt recovery
    change_and_confirm_debt_recovery(page, "Yes", office_code="6A001L")

    # Submit the form without making any change
    page.get_by_role("link", name="Change referred to debt recovery").click()
    page.get_by_role("button", name="submit").click()
    expect(
        page.get_by_role(
            "link",
            name="Select no if the office is no longer referred to the Debt Recovery Unit. Cancel if you do not want to change the answer.",
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_debt_recovery_cancel(page: Page):
    navigate_to_provider_page(page, provider_name="BIRMINGHAM LEGAL AID CENTRE", office_code="6A001L")
    url = page.url
    page.get_by_role("link", name="Change referred to debt recovery").click()
    page.get_by_role("link", name="Cancel").click()
    assert page.url == url
    expect(page.get_by_text("Success")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_debt_recovery_yes(page: Page):
    navigate_to_provider_page(page, provider_name="BIRMINGHAM LEGAL AID CENTRE", office_code="6A001L")
    change_and_confirm_debt_recovery(page, "Yes", office_code="6A001L")
    # Confirm the tag is displayed
    page.locator(".referred-to-debt-recovery", has_text="Referred to debt recovery")


@pytest.mark.usefixtures("live_server")
def test_change_office_debt_recovery_no(page: Page):
    navigate_to_provider_page(page, provider_name="BIRMINGHAM LEGAL AID CENTRE", office_code="6A001L")

    # First put the office into debt recovery
    change_and_confirm_debt_recovery(page, "Yes", office_code="6A001L")
    # Then take the firm out of debt recovery
    change_and_confirm_debt_recovery(page, "No", office_code="6A001L")

    # Check we are on the assign contract manager page
    expect(page.get_by_role("heading", name="Assign contract manager")).to_be_visible()
    expect(page.get_by_role("textbox", name="Search for a contract manager"))
