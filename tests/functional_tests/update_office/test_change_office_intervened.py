from datetime import date

import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import definition_list_to_dict, navigate_to_provider_page


def change_and_confirm_intervened(
    page: Page,
    intervened_date: str | None,
    office_code: str,
    is_head_office: bool = False,
    fail_on_purpose: bool = False,
):
    """
    Helper function to change and confirm and intervention change of an office
    Args:
        page: Page element
        intervened_date: The date of the intervention or None if removing an intervention
        office_code: The code of the office to intervene
        is_head_office: Whether the office is head-office
        fail_on_purpose: Set true if when clicking the submit button will fail with the no changes made error
    """

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
        # Success messages
        if intervened_date:
            if is_head_office:
                expect(page.get_by_text(f"Head office {office_code} set as intervened.")).to_be_visible()
            else:
                expect(page.get_by_text(f"Office {office_code} marked as intervened.")).to_be_visible()
        else:
            if is_head_office:
                expect(page.get_by_text(f"Intervention removed from head office {office_code}.")).to_be_visible()
            else:
                expect(page.get_by_text(f"Office {office_code} marked as not intervened.")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened_default_value(page: Page):
    """Test the default display value is No"""

    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    data = definition_list_to_dict(page, dl_selector=".status-table")
    assert data["Intervened"] == "No"


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened__head_office_intervened(page: Page):
    """Test setting head office as intervened"""

    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    # Make office intervened
    change_and_confirm_intervened(page, date.today().strftime("%d/%m/%Y"), office_code="1A001L", is_head_office=True)

    # We should be taken to the Apply intervention to other offices page
    expect(page.get_by_text("Select other offices to be intervened")).to_be_visible()
    expect(page.get_by_role("button", name="Set selected offices as intervened")).to_be_visible()
    # Make sure firms other offices are shown
    table = page.locator(".govuk-table--checkbox")
    # Head office in the list as the user already selected the head office on the previous screen
    expect(table.get_by_text("1A001L")).not_to_be_visible()
    # The firms other offices should be listed
    expect(table.get_by_text("1A002L")).to_be_visible()
    # Make sure no other firms offices are displayed
    expect(table.get_by_text("3A001L")).not_to_be_visible()

    # Make sure the office has the intervened tag
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    expect(page.locator(".govuktag-intervened")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened__head_office_remove_intervention(page: Page):
    """Test removing intervention from head office"""

    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    # Make office intervened
    change_and_confirm_intervened(page, date.today().strftime("%d/%m/%Y"), office_code="1A001L", is_head_office=True)

    # Take office out of intervention
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    change_and_confirm_intervened(page, intervened_date=None, office_code="1A001L", is_head_office=True)

    # We should be taken to the Remove intervention for other offices page
    expect(page.get_by_text("Select other offices to remove intervention from")).to_be_visible()
    expect(page.get_by_role("button", name="Remove intervention from selected offices")).to_be_visible()
    # Make sure firms other offices are shown
    table = page.locator(".govuk-table--checkbox")
    # Head office in the list as the user already selected the head office on the previous screen
    expect(table.get_by_text("1A001L")).not_to_be_visible()
    # The firms other offices should be listed
    expect(table.get_by_text("1A002L")).to_be_visible()
    # Make sure no other firms offices are displayed
    expect(table.get_by_text("3A001L")).not_to_be_visible()

    # Make sure the office does not have the intervened tag
    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A001L")
    expect(page.locator(".govuktag-intervened")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened__office_intervened(page: Page):
    """Test setting normal office to be intervened"""

    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A002L")
    office_view_url = page.url
    # Make office intervened
    change_and_confirm_intervened(page, date.today().strftime("%d/%m/%Y"), office_code="1A002L")
    # Check we can see the confirmation message for the intervention
    expect(page.get_by_text("Office 1A002L marked as intervened.")).to_be_visible()
    # Make sure we are not on the Apply intervention page
    expect(page.get_by_text("Select other offices to be intervened")).not_to_be_visible()
    expect(page.get_by_role("heading", name="SMITH & PARTNERS SOLICITORS"))
    assert office_view_url == page.url

    # Make sure the office has the intervened tag
    expect(page.locator(".govuktag-intervened")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_office_intervened_no_changes__no(page: Page):
    """Test making no changes displays the correct `No` specific message"""

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
    """Test making no changes displays the correct `Yes` specific message"""

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
    """Test cancelling intervention takes you back to the office view page"""

    navigate_to_provider_page(page, provider_name="SMITH & PARTNERS SOLICITORS", office_code="1A002L")
    url = page.url
    page.get_by_role("link", name="Change intervened").click()
    page.get_by_role("link", name="Cancel").click()
    assert url == page.url
