import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_view_provider_contacts_primary_contact_displayed(page: Page):
    """Test that the primary contact is displayed directly on the contacts page."""
    # Navigate to provider 1 contacts page (has contacts in fixtures)
    page.goto(url_for("main.view_provider_contact", firm=1, _external=True))

    # Verify we're on the contacts page
    expect(page.get_by_role("heading", name="Contacts")).to_be_visible()

    # Check that the primary contact (Sarah Johnson) is displayed directly
    expect(page.get_by_text("Sarah Johnson", exact=True)).to_be_visible()
    expect(page.get_by_text("sarah.johnson@smithpartners.com")).to_be_visible()
    expect(page.get_by_text("0116 123 4567")).to_be_visible()
    expect(page.get_by_text("https://www.smithpartners.com")).to_be_visible()
    expect(page.get_by_text("Liaison manager", exact=True)).to_have_count(3)

    # Check that the active from date is displayed (Sarah Johnson's date: 2024-01-15)
    expect(page.get_by_text("15 Jan 2024")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_provider_contacts_multiple_contacts_with_details(page: Page):
    """Test that multiple contacts show primary first and others in details component."""
    # Navigate to provider 1 contacts page (has 3 contacts in fixtures)
    page.goto(url_for("main.view_provider_contact", firm=1, _external=True))

    # Verify the primary contact is shown directly
    expect(page.get_by_text("Sarah Johnson", exact=True)).to_be_visible()

    # Check that there's a details component for additional contacts (now 2 additional)
    expect(page.get_by_text("Show 2 additional contacts")).to_be_visible()

    # The secondary contacts should not be visible initially
    expect(page.get_by_text("David Smith", exact=True)).not_to_be_visible()
    expect(page.get_by_text("Alice Brown", exact=True)).not_to_be_visible()
    expect(page.get_by_text("david.smith@smithpartners.com")).not_to_be_visible()
    expect(page.get_by_text("alice.brown@smithpartners.com")).not_to_be_visible()

    # Click the details to reveal additional contacts
    page.get_by_text("Show 2 additional contacts").click()

    # Now both secondary contacts should be visible
    expect(page.get_by_text("David Smith", exact=True)).to_be_visible()
    expect(page.get_by_text("Alice Brown", exact=True)).to_be_visible()
    expect(page.get_by_text("david.smith@smithpartners.com")).to_be_visible()
    expect(page.get_by_text("alice.brown@smithpartners.com")).to_be_visible()
    expect(page.get_by_text("0116 123 4568")).to_be_visible()
    expect(page.get_by_text("0116 123 4569")).to_be_visible()

    # Check that active from dates are visible for additional contacts
    expect(page.get_by_text("10 Mar 2024")).to_be_visible()  # David Smith's date
    expect(page.get_by_text("22 Jun 2024")).to_be_visible()  # Alice Brown's date


@pytest.mark.usefixtures("live_server")
def test_view_provider_contacts_single_contact_no_details(page: Page):
    """Test that a provider with only one contact shows no details component."""
    # Navigate to provider 2 which has only 1 contact
    page.goto(url_for("main.view_provider_contact", firm=2, _external=True))

    # Verify the contact is displayed
    expect(page.get_by_role("heading", name="Contacts")).to_be_visible()
    expect(page.get_by_text("Robert MacLeod", exact=True)).to_be_visible()
    expect(page.get_by_text("robert.macleod@scottishlegal.com")).to_be_visible()

    # Should not show any details component
    expect(page.get_by_text("Show")).not_to_be_visible()
    expect(page.get_by_text("additional contact")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_provider_contacts_summary_list_structure(page: Page):
    """Test that contacts are displayed in proper summary list format."""
    page.goto(url_for("main.view_provider_contact", firm=2, _external=True))

    # Check that required fields are present in the summary list
    expect(page.get_by_text("Job title")).to_be_visible()
    expect(page.get_by_text("Telephone number")).to_be_visible()
    expect(page.get_by_text("Email address")).to_be_visible()
    expect(page.get_by_text("Website")).to_be_visible()
    expect(page.get_by_text("Active from")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_provider_contacts_details_component_functionality(page: Page):
    """Test that the details component can be opened and closed properly."""
    page.goto(url_for("main.view_provider_contact", firm=1, _external=True))

    # Details should start closed
    details = page.locator("details")
    # Additional contact should not be visible
    expect(page.get_by_text("David Smith", exact=True)).not_to_be_visible()

    # Click to open
    page.get_by_text("Show 2 additional contacts").click()

    # Details should now be open
    expect(page.get_by_text("David Smith", exact=True)).to_be_visible()

    # Click to close
    page.get_by_text("Show 2 additional contacts").click()

    # Details should be closed again
    expect(page.get_by_text("David Smith", exact=True)).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_provider_contacts_active_from_dates_displayed(page: Page):
    """Test that active from dates are properly displayed and formatted."""
    # Navigate to provider with a single contact to test date display
    page.goto(url_for("main.view_provider_contact", firm=2, _external=True))

    # Verify the contact is displayed
    expect(page.get_by_role("heading", name="Contacts")).to_be_visible()
    expect(page.get_by_text("Robert MacLeod", exact=True)).to_be_visible()

    # Check that the active from date is properly formatted (Robert MacLeod: 2023-12-20)
    expect(page.get_by_text("Active from")).to_be_visible()
    expect(page.get_by_text("20 Dec 2023")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_view_provider_contacts_no_contacts_provider(page: Page):
    """Test behavior when a provider has no contacts."""
    # Try accessing a provider that doesn't exist in contacts fixtures
    # This should show no contacts section
    page.goto(url_for("main.view_provider_contact", firm=10, _external=True))

    # Should not show the Contacts heading since there are no contacts
    expect(page.get_by_role("heading", name="Contacts")).not_to_be_visible()

    # Should not show any summary lists for contacts
    expect(page.locator(".govuk-summary-list")).not_to_be_visible()
