import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import navigate_to_provider_page


@pytest.mark.usefixtures("live_server")
def test_change_provider_hold_payments_to_yes_then_no(page: Page):
    navigate_to_provider_page(page, "Alan Davies")
    # Change provider Hold Payments from NO to YES
    page.get_by_role("link", name="Change   payments on hold").click()
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("textbox", name="Why do you want to hold").fill("Test")
    page.get_by_role("button", name="Submit").click()

    # Success message appears... and On Hold label exists
    page.get_by_label("Success").locator("div").filter(has_text="Alan Davies payments put on")
    expect(page.get_by_text("On hold", exact=True)).to_be_visible()

    # Remove the HOLD in the account...
    page.get_by_role("link", name="Change   payments on hold").click()
    page.get_by_role("radio", name="No").check()
    page.get_by_role("button", name="Submit").click()

    # ...see the success message on the provider page and the On Hold removed...
    page.get_by_label("Success").locator("div").filter(has_text="Alan Davies hold on payments removed successfully")
    expect(page.get_by_text("On hold", exact=True)).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_submitign_hold_unchanged(page: Page):
    navigate_to_provider_page(page, "Finn O'Connor")

    # Try submitting the form without changing No to Yes
    page.get_by_role("link", name="Change   payments on hold").click()
    page.get_by_role("button", name="Submit").click()

    # Validation success for when trying to submit No when is already No.
    expect(page.get_by_role("heading", name="There is a problem")).to_be_visible()
    expect(page.get_by_role("link", name="Select yes to put payments on")).to_be_visible()

    # Change it to Yes and without a text
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("button", name="Submit").click()
    page.get_by_role("textbox", name="Why do you want to hold")

    # Validate cannot submit a blank reason text
    expect(page.locator("#main-content")).to_contain_text("Explain why you want to hold all payments")

    # Insert a text in the box
    page.get_by_role("textbox", name="Why do you want to hold").fill("Now with a text")
    page.get_by_role("button", name="Submit").click()

    # Successful change
    page.get_by_label("Success").locator("div").filter(has_text="Finn O'Connor payments put on").click()
    expect(page.get_by_text("On hold", exact=True)).to_have_count(1)


@pytest.mark.usefixtures("live_server")
def test_cancel_action_hold_payments(page: Page):
    navigate_to_provider_page(page, "Karen Sillen")

    # Go to hold payments page
    page.get_by_role("link", name="Change   payments on hold").click()
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("textbox", name="Why do you want to hold").click()
    page.get_by_role("textbox", name="Why do you want to hold").fill("Testing cancelling a change")

    # Cancel form...
    page.get_by_role("link", name="Cancel").click()

    # Validating On Hold is not showing
    expect(page.get_by_text("On hold", exact=True)).to_have_count(0)
