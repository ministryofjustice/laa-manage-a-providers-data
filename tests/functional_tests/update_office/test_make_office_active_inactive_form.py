import pytest
from flask import url_for
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import navigate_to_provider_page


@pytest.mark.usefixtures("live_server")
def test_change_office_from_active_to_inactive_to_active(page: Page):
    navigate_to_provider_page(page, provider_name="Birmingham Legal Aid Centre", office_code="6A002L")

    # Active -> Inactive
    page.get_by_role("link", name="Change active").click()

    # After clicking the 'make inactive' button, check we have the correct screen
    expect(page.get_by_text("Birmingham Legal Aid Centre")).to_be_visible()
    expect(page.get_by_role("heading", name="Office: 6A002L")).to_be_visible()
    expect(page.get_by_role("heading", name="Change active status")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()
    expect(page.get_by_role("link", name="Cancel")).to_be_visible()

    # Start with office active...
    expect(page.get_by_role("radio", name="Active", exact=True)).to_be_checked()
    expect(page.get_by_role("radio", name="Inactive")).not_to_be_checked()
    # ...make the office inactive...
    page.get_by_role("radio", name="Inactive").check()
    page.get_by_role("button", name="Submit").click()

    # ...see the success message on the office page...
    expect(page.get_by_text("Office marked as inactive", exact=True)).to_be_visible()

    # Inactive -> Active
    # Make the office active...
    page.get_by_role("link", name="Change active").click()
    expect(page.get_by_role("radio", name="Active", exact=True)).not_to_be_checked()
    page.get_by_role("radio", name="Active", exact=True).check()
    page.get_by_role("button", name="Submit").click()

    # Success message should not be visible for this page
    expect(page.get_by_text("Office marked as active", exact=True)).not_to_be_visible()

    # Expect to be taken to the contract manager assignment page
    assert page.url == url_for("main.change_office_contract_manager", firm=6, office="6A002L", _external=True)


@pytest.mark.usefixtures("live_server")
def test_change_office_active_status_cancel(page: Page):
    navigate_to_provider_page(page, provider_name="Birmingham Legal Aid Centre", office_code="6A002L")
    expect(page.get_by_role("heading", name="Office: 6A002L")).to_be_visible()

    # Start with an active office
    expect(page.get_by_text("Inactive")).not_to_be_visible()
    # Start the process to change the status...
    page.get_by_role("link", name="Change active").click()
    expect(page.get_by_role("heading", name="Change active status")).to_be_visible()
    expect(page.get_by_role("link", name="Cancel")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()
    # Change the value...
    expect(page.get_by_role("radio", name="Inactive")).not_to_be_checked()
    page.get_by_role("radio", name="Inactive").check()
    # ...but cancel the action...
    page.get_by_role("link", name="Cancel").click()
    # ...and see the status has not changed
    expect(page.get_by_text("Inactive")).not_to_be_visible()
    # ...on the same office...
    expect(page.get_by_role("heading", name="Office: 6A002L")).to_be_visible()
    # ...and without a success message
    expect(page.get_by_text("Office marked as active", exact=True)).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_active_status_nochange(page: Page):
    navigate_to_provider_page(page, provider_name="Birmingham Legal Aid Centre", office_code="6A002L")

    # Start with an active office
    expect(page.get_by_role("heading", name="Office: 6A002L")).to_be_visible()
    expect(page.get_by_text("Inactive")).not_to_be_visible()

    # Start the process to change the status...
    page.get_by_role("link", name="Change active").click()
    # ...check we have the expected status...
    expect(page.get_by_role("radio", name="Active", exact=True)).to_be_checked()
    # ...and submit with unchanged value...
    page.get_by_role("button", name="Submit").click()
    # ...and see the status has not changed
    expect(page.get_by_text("Inactive")).not_to_be_visible()
    # ...on the same office...
    expect(page.get_by_role("heading", name="Office: 6A002L")).to_be_visible()
    # ...and with a message letting us know there have been no changes
    expect(page.get_by_text("Office active status unchanged", exact=True)).to_be_visible()
