import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_office(page: Page, provider_name: str, office_code: str | None):
    page.goto(url_for("main.providers", _external=True))

    # Search for "Smith" to find "SMITH & PARTNERS SOLICITORS"
    page.get_by_role("textbox", name="Find a provider").fill(provider_name)
    page.get_by_role("button", name="Search").click()

    # Click on the first provider (should be "SMITH & PARTNERS SOLICITORS" from fixtures)
    page.get_by_role("link", name=provider_name).click()

    if office_code:
        # Click on the Offices sub-navigation
        page.get_by_role("link", name="Offices").click()

        # Click "A specific office" button
        page.get_by_role("link", name=office_code).click()

        # Verify we're on view office page
        expect(page.get_by_role("heading", name=f"Office: {office_code}")).to_be_visible()

    else:
        expect(page.get_by_role("link", name="Offices")).not_to_be_visible()

    page.get_by_role("link", name="Bank accounts and payment").click()


def _test_change_vat(page, has_vat=True, should_contain_office=False):
    current_page_url = page.url
    vat_link_text = "Change" if has_vat else "Enter VAT registration number"
    vat_table = page.locator("h2:has-text('VAT registration number') + dl")
    current_vat_number = None

    if has_vat:
        # Get current VAT number
        current_vat_number = vat_table.locator("dt:has-text('VAT registration number') + dd").text_content().strip()

    # CLick change VAT link and add new VAT number
    vat_table.get_by_role("link", name=vat_link_text).click()

    # LSP and Chambers VAT change page should have office in the url
    if should_contain_office:
        assert "office/" in page.url

    vat_input = page.locator("#vat_registration_number")
    if has_vat:
        expect(vat_input).to_have_value(current_vat_number)

    vat_input.fill("GB112233445")
    page.get_by_role("button", name="Continue").click()
    page.get_by_text("Updated VAT registration number")

    if has_vat:
        # The old vat number should not be on the page
        expect(page.get_by_text(current_vat_number)).not_to_be_visible()

    # New vat number should be on the page
    expect(page.get_by_text("GB112233445")).to_be_visible()

    # Make sure the user is back to where they started
    expect(page).to_have_url(current_page_url)


@pytest.mark.usefixtures("live_server")
def test_lsp_change_vat(page: Page):
    navigate_to_office(page, "SMITH & PARTNERS SOLICITORS", "1A001L")
    _test_change_vat(page, has_vat=True, should_contain_office=True)


@pytest.mark.usefixtures("live_server")
def test_barristers_change_vat(page: Page):
    navigate_to_office(page, "Karen Sillen", office_code=None)
    _test_change_vat(page, has_vat=False, should_contain_office=False)


@pytest.mark.usefixtures("live_server")
def test_advocates_change_vat(page: Page):
    navigate_to_office(page, "John Smith-Woods", office_code=None)
    _test_change_vat(page, has_vat=False, should_contain_office=False)
