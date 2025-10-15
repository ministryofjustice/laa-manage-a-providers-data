import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_offices(page: Page):
    """Helper function to navigate to the Office detail page."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    # List all providers"
    page.get_by_role("button", name="Search").click()

    # Click on the provider known to have more than one office
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()
    page.get_by_role("link", name="Offices").click()

    # Verify the expected offices are present
    expect(page.get_by_role("link", name="1A001L")).to_be_visible()
    expect(page.get_by_role("link", name="1A002L")).to_be_visible()

    # And the first office is head office
    expect(page.get_by_role("definition").filter(has_text="1A001L")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_reassign_head_office(page: Page):
    navigate_to_offices(page)

    # Click the button
    page.get_by_role("button", name="Reassign head office").click()
    # expect(page.get_by_role("row", name="Select this row  1A001L 1").locator("div")).to_be_visible()

    # Select the new head office...
    page.get_by_role("row", name="Select this row  1A002L 2").get_by_label("Select this row").check()
    page.get_by_role("button", name="Submit").click()
    # ...and see an update message...
    expect(page.get_by_text("SMITH & PARTNERS SOLICITORS head office reassigned to 1A002L")).to_be_visible()
    # ...and the provider account number changed.
    expect(page.get_by_role("definition").filter(has_text="1A002L")).to_be_visible()

    # Reset back to original
    page.get_by_role("button", name="Reassign head office").click()
    page.get_by_role("row", name="Select this row  1A001L 1").get_by_label("Select this row").check()
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_role("definition").filter(has_text="1A002L")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_reassign_head_office_cancel(page: Page):
    navigate_to_offices(page)

    # Click the button
    page.get_by_role("button", name="Reassign head office").click()

    # Check we have the expected view
    expect(page.get_by_role("row", name="Select this row  1A001L 1").locator("div")).to_be_visible()
    # Select the new head office...
    page.get_by_role("row", name="Select this row  1A002L 2").get_by_label("Select this row").check()
    # ...but cancel instead...
    page.get_by_role("link", name="Cancel").click()
    # ...and do not see any change messages...
    expect(page.get_by_text("No change made because 1A001L")).not_to_be_visible()
    expect(page.get_by_text("SMITH & PARTNERS SOLICITORS head office reassigned to 1A002L")).not_to_be_visible()
    # ...and the provider account number has not changed.
    expect(page.get_by_role("definition").filter(has_text="1A001L")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_reassign_head_office_nochange(page: Page):
    navigate_to_offices(page)

    # Click the button
    page.get_by_role("button", name="Reassign head office").click()

    # Check we have the expected view
    expect(page.get_by_role("row", name="Select this row  1A001L 1").locator("div")).to_be_visible()
    # Select the same head office...
    page.get_by_role("row", name="Select this row  1A001L 1").get_by_label("Select this row").check()
    # ...submit the same head office...
    page.get_by_role("button", name="Submit").click()
    # ...and see an appropriate message...
    expect(page.get_by_text("No change made because 1A001L")).to_be_visible()
    # ...and the provider account number has not changed.
    expect(page.get_by_role("definition").filter(has_text="1A001L")).to_be_visible()
