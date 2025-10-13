import datetime

import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_office(page: Page, provider_name: str, office_code: str):
    page.goto(url_for("main.providers", _external=True))

    # Search for "Smith" to find "SMITH & PARTNERS SOLICITORS"
    page.get_by_role("textbox", name="Find a provider").fill(provider_name)
    page.get_by_role("button", name="Search").click()

    # Click on the first provider (should be "SMITH & PARTNERS SOLICITORS" from fixtures)
    page.get_by_role("link", name=provider_name).click()

    # Click on the Offices sub-navigation
    page.get_by_role("link", name="Offices").click()

    # Click "A specific office" button
    page.get_by_role("link", name=office_code).click()

    # Verify we're on view office page
    expect(page.get_by_role("heading", name=f"Office: {office_code}")).to_be_visible()


def complete_add_bank_account_form(page: Page):
    # Complete the add bank account form with some dummy values
    page.get_by_role("textbox", name="Account name").fill("Functional Test Account")
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("08102025")
    page.get_by_role("button", name="Submit").click()

    # Check new bank account is on the office overview page
    bank_account_table = page.locator(".bank-account-table")
    bank_account_table.scroll_into_view_if_needed()
    expect(bank_account_table.locator("dd:text('123456')")).to_be_visible()
    expect(bank_account_table.locator("dd:text('08102025')")).to_be_visible()
    expect(bank_account_table.locator("dd:text('Functional Test Account')")).to_be_visible()
    expect(bank_account_table.locator(f"dd:text('{datetime.date.today().strftime('%d %b %Y')}')")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_bank_account_from_office_page(page: Page):
    navigate_to_office(page, "METROPOLITAN LAW CENTRE", "3A001L")

    # Click on the payment method sub-navigation and add the bank account
    expect(page.get_by_text("Bank accounts and payment")).to_be_visible()
    page.get_by_text("Bank accounts and payment").click()
    page.get_by_role("button", name="Add bank account").click()
    complete_add_bank_account_form(page)


@pytest.mark.usefixtures("live_server")
def test_add_bank_account_from_search_bank_account_page(page: Page):
    navigate_to_office(page, "SMITH & PARTNERS SOLICITORS", "1A001L")
    # Click on the payment method sub-navigation
    expect(page.get_by_text("Bank accounts and payment")).to_be_visible()
    page.get_by_text("Bank accounts and payment").click()
    # The office page should not display an “Add Bank Account” button if a bank account already exists
    expect(page.get_by_role("button", name="Add bank account")).not_to_be_visible()
    # Clicking the Change bank account should take us to the bank account search form
    page.get_by_role("link", name="Change bank account").click()
    expect(page.get_by_role("heading", name="Search for bank account")).to_be_visible()
    # Add a new bank account using the `Add a new bank account` button
    page.get_by_role("button", name="Add a new bank account").click()
    complete_add_bank_account_form(page)
