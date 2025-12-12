import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import navigate_to_provider_page


@pytest.mark.usefixtures("live_server")
def test_change_lsp_name(page: Page):
    navigate_to_provider_page(page, "Smith & Partners Solicitors")
    page.get_by_role("link", name="Change provider name").click()
    expect(page.get_by_role("textbox", name="New provider name")).to_have_value("Smith & Partners Solicitors")
    page.get_by_role("textbox", name="New provider name").fill("Functional test provider")
    page.get_by_role("button", name="submit").click()

    expect(page.get_by_role("heading", name="Functional test provider")).to_be_visible()
    expect(page.get_by_text("Legal services provider name successfully updated")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_lsp_name_no_change(page: Page):
    navigate_to_provider_page(page, "Smith & Partners Solicitors")
    page.get_by_role("link", name="Change provider name").click()
    expect(page.get_by_role("textbox", name="New provider name")).to_have_value("Smith & Partners Solicitors")
    page.get_by_role("button", name="submit").click()

    expect(page.get_by_role("heading", name="Smith & Partners Solicitors")).not_to_be_visible()
    expect(page.get_by_role("heading", name="Change provider name")).to_be_visible()
    expect(
        page.get_by_role("link", name="You have not changed the provider name. Cancel if you do not want to change it.")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_lsp_name_cancel(page: Page):
    navigate_to_provider_page(page, "Smith & Partners Solicitors")
    page.get_by_role("link", name="Change provider name").click()
    expect(page.get_by_role("textbox", name="New provider name")).to_have_value("Smith & Partners Solicitors")
    page.get_by_role("link", name="Cancel").click()

    expect(page.get_by_role("heading", name="Smith & Partners Solicitors")).to_be_visible()
    expect(page.get_by_text("Legal services provider name successfully updated")).not_to_be_visible()
