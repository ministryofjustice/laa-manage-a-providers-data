from datetime import date

import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import definition_list_to_dict, navigate_to_provider_page


def make_inactive(page: Page):
    page.get_by_role("link", name="Change active").click()
    page.get_by_role("radio", name="Inactive").click()
    page.get_by_role("button", name="Save").click()

    today = date.today().strftime("%d %b %Y")
    expect(page.get_by_text(f"Made inactive on {today}")).to_be_visible()


def change_and_confirm_false_balance(page: Page, false_balance: str):
    page.get_by_role("link", name="Change false balance").click()
    page.get_by_role("radio", name=false_balance).click()
    page.get_by_role("button", name="submit").click()
    dl = definition_list_to_dict(page, ".status-table")
    assert dl["False balance"] == false_balance


@pytest.mark.usefixtures("live_server")
def test_change_office_office_false_balance_visible_lsp(page: Page):
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS")
    data = definition_list_to_dict(page, dl_selector=".status-table")
    false_balance = data.get("False balance")
    assert false_balance is None


@pytest.mark.usefixtures("live_server")
def test_change_office_office_false_balance_visible_chambers(page: Page):
    navigate_to_provider_page(page, provider_name="JOHNSON LEGAL SERVICES")
    make_inactive(page)
    data = definition_list_to_dict(page, dl_selector=".status-table")
    false_balance = data.get("False balance")
    assert false_balance is None


@pytest.mark.usefixtures("live_server")
def test_change_office_office_false_balance_visible_barristers(page: Page):
    navigate_to_provider_page(page, provider_name="Karen Sillen")
    make_inactive(page)
    data = definition_list_to_dict(page, dl_selector=".status-table")
    false_balance = data.get("False balance")
    assert false_balance == "No"


@pytest.mark.usefixtures("live_server")
def test_change_office_office_false_balance_visible_advocate(page: Page):
    navigate_to_provider_page(page, provider_name="Finn O'Connor")
    make_inactive(page)
    data = definition_list_to_dict(page, dl_selector=".status-table")
    false_balance = data.get("False balance")
    assert false_balance == "No"


@pytest.mark.usefixtures("live_server")
def test_change_office_office_false_balance_change_advocate(app, page: Page):
    navigate_to_provider_page(page, provider_name="Finn O'Connor")
    make_inactive(page)

    data = definition_list_to_dict(page, dl_selector=".status-table")
    false_balance = data.get("False balance")
    assert false_balance == "No"

    # Change False balance to Yes
    change_and_confirm_false_balance(page, "Yes")

    # Change False balance to No
    change_and_confirm_false_balance(page, "No")


@pytest.mark.usefixtures("live_server")
def test_change_office_office_false_balance_change_barrister(app, page: Page):
    navigate_to_provider_page(page, provider_name="Karen Sillen")
    make_inactive(page)

    data = definition_list_to_dict(page, dl_selector=".status-table")
    false_balance = data.get("False balance")
    assert false_balance == "No"

    # Change False balance to Yes
    change_and_confirm_false_balance(page, "Yes")

    # Change False balance to No
    change_and_confirm_false_balance(page, "No")


@pytest.mark.usefixtures("live_server")
def test_change_office_office_false_balance_change_office(app, page: Page):
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")

    data = definition_list_to_dict(page, dl_selector=".status-table")
    assert data.get("Active") == "Made inactive on 25 Sep 2025"
    assert data.get("False balance") == "No"

    # Change False balance to Yes
    change_and_confirm_false_balance(page, "Yes")

    # Change False balance to No
    change_and_confirm_false_balance(page, "No")
