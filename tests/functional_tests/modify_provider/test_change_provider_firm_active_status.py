import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_provider_change_active_status_page(page: Page):
    """Helper function to navigate to the Provider detail page."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    # List all providers"
    page.get_by_role("button", name="Search").click()

    # Click on the provider known to have an active office
    page.get_by_role("link", name="BIRMINGHAM LEGAL AID CENTRE").click()
    expect(page.get_by_text("Inactive")).not_to_be_visible()

    # Click the Change active status link
    page.get_by_role("link", name="Change active").click()

    # Verify we're on Change active status page
    page.get_by_role("heading", name="Change active status").click()


@pytest.mark.usefixtures("live_server")
def test_change_provider_from_active_to_inactive_to_active(page: Page):
    navigate_to_provider_change_active_status_page(page)

    # Active -> Inactive
    expect(page.get_by_role("radio", name="Active", exact=True)).to_be_checked()
    expect(page.get_by_role("radio", name="Inactive")).not_to_be_checked()

    # ...make the provider inactive...
    page.get_by_role("radio", name="Inactive").check()
    page.get_by_role("button", name="Save").click()

    # ...see the success message on the provider page...
    page.get_by_label("Success").locator("div").filter(
        has_text="BIRMINGHAM LEGAL AID CENTRE marked as inactive"
    ).click()

    # Inactive -> Active
    # Make the provider active...
    page.get_by_role("link", name="Change active").click()
    expect(page.get_by_role("radio", name="Active", exact=True)).not_to_be_checked()
    page.get_by_role("radio", name="Active", exact=True).check()
    page.get_by_role("button", name="Save").click()

    # ...see the success message on the provider page...
    page.get_by_label("Success").locator("div").filter(has_text="BIRMINGHAM LEGAL AID CENTRE marked as active").click()


@pytest.mark.usefixtures("live_server")
def test_change_office_active_status_cancel(page: Page):
    navigate_to_provider_change_active_status_page(page)

    # Start the process to change the status...
    page.get_by_role("radio", name="Inactive").check()
    # Change the value...
    page.get_by_role("radio", name="Active", exact=True).check()
    # ...but cancel the action
    page.get_by_role("link", name="Cancel").click()
    # ...and see the status has not changed
    page.get_by_text("Active", exact=True).click()
    expect(page.get_by_text("Inactive")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_active_status_nochange(page: Page):
    navigate_to_provider_change_active_status_page(page)

    # Try to submit the form without changing the status
    page.get_by_role("button", name="Save").click()

    # Check for error summary at the top of the page
    expect(page.get_by_role("heading", name="There is a problem")).to_be_visible()

    # Check for the error message in the error summary (the link)
    expect(
        page.locator(".govuk-error-summary__list").get_by_text(
            "You have not changed the active status. Cancel if you do not want to change it."
        )
    ).to_be_visible()

    # ...verify we're still on the form page...
    expect(page.get_by_role("heading", name="Change active status")).to_be_visible()

    # ...and the status remains unchanged
    expect(page.get_by_role("radio", name="Active", exact=True)).to_be_checked()

    # ...and cancel with unchanged value...
    page.get_by_role("link", name="Cancel", exact=True).click()

    # ...and see the status has not changed
    page.get_by_text("Active", exact=True).click()
    expect(page.get_by_text("Inactive")).not_to_be_visible()
