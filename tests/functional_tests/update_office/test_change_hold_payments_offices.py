import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import navigate_to_provider_page


@pytest.mark.usefixtures("live_server")
def test_changing_hold_payment_sub_office(page: Page):
    navigate_to_provider_page(page, "Birmingham Legal Aid Centre")

    # Select non-Head Office
    page.get_by_role("link", name="Offices").click()
    page.get_by_role("link", name="6A002L").click()

    # Change provider Hold Payments from NO to YES
    page.get_by_role("link", name="Change   payments on hold").click()
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("textbox", name="Why do you want to hold").fill("Test")
    page.get_by_role("button", name="Submit").click()

    # Success message appears... and On Hold label exists
    expect(page.get_by_text("On hold", exact=True)).to_be_visible()

    # Remove the HOLD in the account...
    page.get_by_role("link", name="Change   payments on hold").click()
    page.get_by_role("radio", name="No").check()
    page.get_by_role("button", name="Submit").click()

    # # ...see the success message on the provider page and the On Hold removed...
    page.get_by_label("Success").locator("div").filter(
        has_text="Birmingham Legal Aid Centre payments put on hold successfully"
    )
    expect(page.get_by_text("On hold", exact=True)).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_changing_hold_payments_head_office(page: Page):
    navigate_to_provider_page(page, "Birmingham Legal Aid Centre")

    # Select non-Head Office
    page.get_by_role("link", name="Offices").click()
    page.get_by_role("link", name="6A001L").click()

    # Go to Head Office Hold Payments Table
    page.get_by_role("link", name="Change   payments on hold").click()
    expect(page.get_by_role("heading", name="Hold payments to Birmingham")).to_be_visible()

    # Head Office pre-selected so no need to click on any checkbox
    page.get_by_role("cell", name="6A001L").nth(1)
    page.get_by_role("cell", name="6A002L")
    page.get_by_role("button", name="Hold payments for selected").click()
    page.get_by_text("On hold", exact=True).click()

    expect(page.get_by_text("On hold", exact=True)).to_be_visible()
