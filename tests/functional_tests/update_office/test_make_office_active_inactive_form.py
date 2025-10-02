import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_office_active_status_form(page: Page):
    """Helper function to navigate to the Office detail page."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    # Search for "Smith" to find "SMITH & PARTNERS SOLICITORS"
    page.get_by_role("textbox", name="Find a provider").fill("smith")
    page.get_by_role("button", name="Search").click()

    # Click on the first provider (should be "SMITH & PARTNERS SOLICITORS" from fixtures)
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    # Click on the Offices sub-navigation
    page.get_by_role("link", name="Offices").click()

    # Click "A specific office" button
    page.get_by_role("link", name="1A001L").click()

    # Verify we're on view office page
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_from_active_to_inactive(page: Page):
    navigate_to_office_active_status_form(page)
    expect(page.get_by_role("button", name="Make inactive")).to_be_visible()
    page.get_by_role("button", name="Make inactive").click()

    # After clicking the 'make inactive' button, check we have the correct screen
    expect(page.get_by_text("SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()
    expect(page.get_by_text("1 Skyscraper, 1 Some Road,")).to_be_visible()
    expect(page.get_by_role("heading", name="Change active status")).to_be_visible()

    expect(page.get_by_role("radio", name="Inactive")).not_to_be_checked()
    expect(page.get_by_role("radio", name="Active", exact=True)).to_be_checked()
    expect(page.get_by_role("radio", name="Active", exact=True)).to_be_visible()

    expect(page.get_by_role("button", name="Submit")).to_be_visible()
    expect(page.get_by_role("link", name="Cancel")).to_be_visible()

    # Make the office inactive
    page.get_by_role("radio", name="Inactive").check()
    page.get_by_role("button", name="Submit").click()

    # See the success message on the office page
    expect(page.get_by_text("Office active status updated")).to_be_visible()
    # With the status updated
    expect(page.get_by_text("Inactive", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Make active")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_from_inactive_to_active(page: Page):
    navigate_to_office_active_status_form(page)
    make_inactive_button = page.get_by_role("button", name="Make inactive")
    if make_inactive_button.is_visible():
        page.get_by_role("button", name="Make inactive").click()
        # After clicking the 'make inactive' button, check we have the correct screen
        expect(page.get_by_text("SMITH & PARTNERS SOLICITORS")).to_be_visible()
        expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()
        expect(page.get_by_text("1 Skyscraper, 1 Some Road,")).to_be_visible()
        expect(page.get_by_role("heading", name="Change active status")).to_be_visible()
        expect(page.get_by_role("radio", name="Inactive")).not_to_be_checked()
    else:
        expect(page.get_by_role("button", name="Make active")).to_be_visible()
        page.get_by_role("button", name="Make active").click()

    # Make the office inactive
    page.get_by_role("radio", name="Inactive").check()
    page.get_by_role("button", name="Submit").click()

    # See the success message on the office page...
    expect(page.get_by_text("Office active status updated")).to_be_visible()
    # Check the status is inactive
    expect(page.get_by_text("Inactive", exact=True)).to_be_visible()
    expect(page.get_by_role("button", name="Make active")).to_be_visible()

    # Change back to active
    page.get_by_role("button", name="Make active").click()
    expect(page.get_by_role("heading", name="Change active status")).to_be_visible()
    page.get_by_role("radio", name="Active", exact=True).check()
    page.get_by_role("button", name="Submit").click()

    # See the success message...
    expect(page.get_by_text("Office active status updated")).to_be_visible()
    # ...and the status changed
    expect(page.get_by_role("button", name="Make inactive")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_active_status_cancel(page: Page):
    navigate_to_office_active_status_form(page)
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()

    # Start with an active office
    expect(page.get_by_role("button", name="Make inactive")).to_be_visible()
    # Start the process to change the status...
    page.get_by_role("button", name="Make inactive").click()
    expect(page.get_by_role("heading", name="Change active status")).to_be_visible()
    expect(page.get_by_role("link", name="Cancel")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()
    # Change the value...
    expect(page.get_by_role("radio", name="Inactive")).not_to_be_checked()
    page.get_by_role("radio", name="Inactive").check()
    # ...but cancel the action...
    page.get_by_role("link", name="Cancel").click()
    # ...and see the status has not changed
    expect(page.get_by_role("button", name="Make inactive")).to_be_visible()
    # ...on the same office...
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()
    # ...and without a success message
    expect(page.get_by_text("Office active status updated")).not_to_be_visible()
