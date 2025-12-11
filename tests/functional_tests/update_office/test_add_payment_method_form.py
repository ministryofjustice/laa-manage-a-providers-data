import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_payment_method_form(page: Page):
    """Helper function to navigate to the Add Office form via UI flow."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    # Search for "Smith" to find "Smith & Partners Solicitors"
    page.get_by_role("textbox", name="Find a provider").fill("smith")
    page.get_by_role("button", name="Search").click()

    # Click on the first provider (should be "Smith & Partners Solicitors" from fixtures)
    page.get_by_role("link", name="Smith & Partners Solicitors").click()

    # Click on the Offices sub-navigation
    page.get_by_role("link", name="Offices").click()

    # Click "A specific office" button
    page.get_by_role("link", name="1A001L").click()

    # Verify we're on view office page
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()
    expect(page.get_by_text("Bank accounts and payment")).to_be_visible()

    # Click on the payment method sub-navigation
    page.get_by_text("Bank accounts and payment").click()

    # Click either "Enter payment method" or "Change"
    enter_link = page.get_by_role("link", name="Enter payment method")
    if enter_link.is_visible():
        enter_link.click()
    else:
        page.get_by_role("link", name="Change payment method").click()

    # Verify we're on the payment method page
    expect(page.get_by_role("heading", name="Payment method")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_payment_method_form_loads_via_ui(page: Page):
    """Test that the Payment Method form loads correctly via UI navigation."""
    navigate_to_payment_method_form(page)

    # Verify form elements are present
    expect(page.get_by_role("heading", name="Payment method")).to_be_visible()
    expect(page.get_by_role("radio", name="Electronic")).to_be_visible()
    expect(page.get_by_role("radio", name="Cheque")).to_be_visible()
    expect(page.get_by_role("button", name="Save")).to_be_visible()

    # Verify initial state
    expect(page.get_by_role("radio", name="Electronic")).to_be_checked()
    expect(page.get_by_role("radio", name="Cheque")).not_to_be_checked()


@pytest.mark.usefixtures("live_server")
def test_valid_form_submission_payment_method_electronic(page: Page):
    """Test successful form submission when selecting 'Electronic' payment method."""
    # Navigate to the payment method form
    navigate_to_payment_method_form(page)

    # Select 'Electronic' payment method and submit
    page.get_by_role("radio", name="Electronic").click()
    page.get_by_role("button", name="Save").click()

    # Redirect to the bank-payment-details subpage
    expect(page).to_have_url(url_for("main.view_office_bank_payment_details", firm=1, office="1A001L", _external=True))

    # Verify success message is shown
    expect(page.get_by_text("Payment method updated successfully")).to_be_visible()

    # Verify the payment method is displayed correctly on bank-payment-details
    expect(page.get_by_text("Payment method").locator("xpath=following-sibling::*[1]")).to_have_text("Electronic")
    expect(page.get_by_text("Electronic", exact=True)).to_be_visible()

    # Now click Change and ensure Electronic is preselected
    page.get_by_role("link", name="Change payment method").click()
    expect(page.get_by_role("heading", name="Payment method")).to_be_visible()
    expect(page.get_by_role("radio", name="Electronic")).to_be_checked()
    expect(page.get_by_role("radio", name="Cheque")).not_to_be_checked()


@pytest.mark.usefixtures("live_server")
def test_valid_form_submission_payment_method_cheque(page: Page):
    """Test successful form submission when selecting 'Cheque' payment method."""
    # Navigate to the payment method form
    navigate_to_payment_method_form(page)

    # Select 'Cheque' payment method and submit
    page.get_by_role("radio", name="Cheque").click()
    page.get_by_role("button", name="Save").click()

    # Redirect to the bank-payment-details subpage
    expect(page).to_have_url(url_for("main.view_office_bank_payment_details", firm=1, office="1A001L", _external=True))

    # Verify success message is shown
    expect(page.get_by_text("Payment method updated successfully")).to_be_visible()

    # Verify the payment method is displayed correctly on bank-payment-details
    expect(page.get_by_text("Payment method").locator("xpath=following-sibling::*[1]")).to_have_text("Cheque")

    # Now click Change and ensure Cheque is preselected
    page.get_by_role("link", name="Change payment method").click()
    expect(page.get_by_role("heading", name="Payment method")).to_be_visible()
    expect(page.get_by_role("radio", name="Cheque")).to_be_checked()
    expect(page.get_by_role("radio", name="Electronic")).not_to_be_checked()
