import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_search_bank_account(page: Page):
    """Helper function to navigate to the Add Office form via UI flow."""
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
    expect(page.get_by_text("Bank accounts and payment")).to_be_visible()

    # Click on the payment method sub-navigation
    page.get_by_text("Bank accounts and payment").click()

    bank_account_table = page.locator(".bank-account-table-primary-flag-y")
    bank_account_table.scroll_into_view_if_needed()
    # Confirm bank account is displayed
    expect(bank_account_table.locator("dd:text('203045')")).to_be_visible()
    expect(bank_account_table.locator("dd:text('12345678')")).to_be_visible()
    expect(bank_account_table.locator("dd:text('Smith & Partners Solicitors Client Account')")).to_be_visible()

    # Confirm the other account is NOT displayed
    expect(bank_account_table.locator("dd:text('404516')")).not_to_be_visible()
    expect(bank_account_table.locator("dd:text('87654321')")).not_to_be_visible()
    expect(bank_account_table.locator("dd:text('Johnson Legal Services Business Account')")).not_to_be_visible()

    # Click the add bank button to add a new account
    page.get_by_role("link", name="Change bank account").click()

    # We are now on the Search bank accounts page

    # Check all firm bank accounts are displayed
    # Account 1
    expect(page.locator("td:text('203045')")).to_be_visible()
    expect(page.locator("td:text('12345678')")).to_be_visible()
    expect(page.locator("td:text('Smith & Partners Solicitors Client Account')")).to_be_visible()
    # Account 2
    expect(page.locator("td:text('404516')")).to_be_visible()
    expect(page.locator("td:text('87654321')")).to_be_visible()
    expect(page.locator("td:text('Johnson Legal Services Business Account')")).to_be_visible()

    # Select a bank account
    page.locator('input[type="radio"][value="2"][name="bank_account"]').click()
    page.get_by_role("button", name="Submit").click()

    # We are now back viewing the office
    bank_account_table = page.locator(".bank-account-table-primary-flag-y")
    bank_account_table.scroll_into_view_if_needed()

    # Confirm the new bank is displayed
    expect(bank_account_table.locator("dd:text('404516')")).to_be_visible()
    expect(bank_account_table.locator("dd:text('87654321')")).to_be_visible()
    expect(bank_account_table.locator("dd:text('Johnson Legal Services Business Account')")).to_be_visible()

    # Confirm the old bank is NOT displayed
    expect(bank_account_table.locator("dd:text('203045')")).not_to_be_visible()
    expect(bank_account_table.locator("dd:text('12345678')")).not_to_be_visible()
    expect(bank_account_table.locator("dd:text('Smith & Partners Solicitors Client Account')")).not_to_be_visible()


def _test_search_bank_account_advocate_barrister(
    page: Page, provider_name, current_account_name, current_account_sortcode, current_account_number
):
    """Helper function to navigate to the Add Office form via UI flow."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    page.get_by_role("textbox", name="Find a provider").fill(provider_name)
    page.get_by_role("button", name="Search").click()

    # Click on the first provider
    page.get_by_role("link", name=provider_name).click()

    expect(page.get_by_text("Bank accounts and payment")).to_be_visible()
    # Click on the payment method sub-navigation
    page.get_by_text("Bank accounts and payment").click()
    expected_return_page_url = page.url

    if current_account_number:
        # Add bank account button should not be there
        expect(page.get_by_role("button", name="Add bank account")).not_to_be_visible()
        # Confirm bank account is displayed
        bank_account_table = page.locator(".bank-account-table-primary-flag-y")
        bank_account_table.scroll_into_view_if_needed()
        expect(bank_account_table.locator(f"dd:text('{current_account_number}')")).to_be_visible()
        expect(bank_account_table.locator(f"dd:text('{current_account_sortcode}')")).to_be_visible()
        expect(bank_account_table.locator(f"dd:text('{current_account_name}')")).to_be_visible()
        # Click the change bank account button
        page.get_by_role("link", name="Change bank account").click()
    else:
        # Bank info table should not be there
        expect(page.locator(".bank-account-table-primary-flag-y")).not_to_be_visible()
        # Click the add bank button to add a new account
        page.get_by_role("button", name="Add bank account").click()

    # We are now on the Search bank accounts page

    # Check accounts belonging to other firms are displayed
    # Smith & Partners Solicitors Client Account
    expect(page.locator("td:text('203045')")).to_be_visible()
    expect(page.locator("td:text('12345678')")).to_be_visible()
    expect(page.locator("td:text('Smith & Partners Solicitors Client Account')")).to_be_visible()
    # Johnson Legal Services Business Account
    expect(page.locator("td:text('404516')")).to_be_visible()
    expect(page.locator("td:text('87654321')")).to_be_visible()
    expect(page.locator("td:text('Johnson Legal Services Business Account')")).to_be_visible()
    # Brown & Associates Client Account
    expect(page.locator("td:text('309634')")).to_be_visible()
    expect(page.locator("td:text('11223344')")).to_be_visible()
    expect(page.locator("td:text('Brown & Associates Client Account')")).to_be_visible()

    # Select a bank account
    page.locator('input[type="radio"][value="3"][name="bank_account"]').click()
    page.get_by_role("button", name="Submit").click()

    assert page.url == expected_return_page_url
    # We are now back viewing the office
    bank_account_table = page.locator(".bank-account-table-primary-flag-y")
    bank_account_table.scroll_into_view_if_needed()

    # Confirm the new bank is displayed
    expect(bank_account_table.locator("dd:text('309634')")).to_be_visible()
    expect(bank_account_table.locator("dd:text('11223344')")).to_be_visible()
    expect(bank_account_table.locator("dd:text('Brown & Associates Client Account')")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_search_bank_account_barrister(page: Page):
    _test_search_bank_account_advocate_barrister(
        page,
        provider_name="Karen Sillen",
        current_account_name="Karen Sillen Main Account",
        current_account_number="33205723",
        current_account_sortcode="398334",
    )


@pytest.mark.usefixtures("live_server")
def test_search_bank_account_advocate(page: Page):
    _test_search_bank_account_advocate_barrister(
        page,
        provider_name="John Smith-Woods",
        current_account_name=None,
        current_account_number=None,
        current_account_sortcode=None,
    )
