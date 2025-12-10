from datetime import date

import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import definition_list_to_dict, navigate_to_provider_page


def change_and_confirm_intervened(
    page: Page, intervened_date: str | None, office_code: str, fail_on_purpose: bool = False
):
    status = "Yes" if intervened_date else "No"
    page.get_by_role("link", name="Change intervened").click()
    page.get_by_role("radio", name=status).click()

    expect(page.get_by_text("Date intervened")).to_be_visible(visible=status == "Yes")
    expect(page.get_by_role("textbox", name="Day")).to_be_visible(visible=status == "Yes")
    expect(page.get_by_role("textbox", name="Month")).to_be_visible(visible=status == "Yes")
    expect(page.get_by_role("textbox", name="Year")).to_be_visible(visible=status == "Yes")

    if intervened_date:
        day, month, year = intervened_date.split("/")
        page.get_by_role("textbox", name="Day").fill(day)
        page.get_by_role("textbox", name="Month").fill(month)
        page.get_by_role("textbox", name="Year").fill(year)

    page.get_by_role("button", name="Submit").click()

    if fail_on_purpose:
        expect(page.get_by_text("There is a problem")).to_be_visible()
    else:
        message = (
            f"Office {office_code} marked as intervened."
            if intervened_date
            else f"Office {office_code} marked as not intervened."
        )
        expect(page.get_by_text(message)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened_default_value(page: Page):
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    data = definition_list_to_dict(page, dl_selector=".status-table")
    assert data["Intervened"] == "No"


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened_yes(page: Page):
    "Intervened changed from no to yes"
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    # Make office intervened
    change_and_confirm_intervened(page, date.today().strftime("%d/%m/%Y"), office_code="1A001L")
    # We should then be taken to the Apply intervention to other offices page
    expect(page.get_by_text("Apply intervention on SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("button", name="Apply intervention for provider and selected offices")).to_be_visible()
    # Make sure firms other offices are shown
    table = page.locator(".govuk-table--checkbox")
    expect(table.get_by_text("1A001L")).to_be_visible()
    expect(table.get_by_text("1A002L")).to_be_visible()
    # Make sure no other firms offices are displayed
    expect(table.get_by_text("3A001L")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened_no(page: Page):
    "Intervened changed from yes to no"
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    # Make office intervened
    change_and_confirm_intervened(page, date.today().strftime("%d/%m/%Y"), office_code="1A001L")

    # Take office out of intervention
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    change_and_confirm_intervened(page, intervened_date=None, office_code="1A001L")

    # We should then be taken to the Apply intervention to other offices page
    expect(page.get_by_text("Office 1A001L marked as not intervened.")).to_be_visible()
    expect(page.get_by_text("Remove intervention on SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("button", name="Remove intervention for provider and selected offices")).to_be_visible()
    # Make sure firms other offices are shown
    table = page.locator(".govuk-table--checkbox")
    expect(table.get_by_text("1A001L")).to_be_visible()
    expect(table.get_by_text("1A002L")).to_be_visible()
    # Make sure no other firms offices are displayed
    expect(table.get_by_text("3A001L")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened_no_changes__no(page: Page):
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A002L")
    change_and_confirm_intervened(page, intervened_date=None, office_code="1A002L", fail_on_purpose=True)
    expect(page.get_by_text("There is a problem")).to_be_visible()
    expect(
        page.get_by_text(
            "Select yes if this office has been intervened. Cancel if you do not want to change the answer."
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened_no_changes__yes(page: Page):
    # Set intervened to Yes
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A002L")
    change_and_confirm_intervened(page, "10/12/2025", "1A002L")

    # Submit without making changes
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A002L")
    change_and_confirm_intervened(page, "10/12/2025", office_code="1A002L", fail_on_purpose=True)

    expect(page.get_by_text("There is a problem")).to_be_visible()
    expect(
        page.get_by_text(
            "Select no if this office has not been intervened. Cancel if you do not want to change the answer."
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened_cancel(page: Page):
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A002L")
    url = page.url
    page.get_by_role("link", name="Change intervened").click()
    page.get_by_role("link", name="Cancel").click()
    assert url == page.url
