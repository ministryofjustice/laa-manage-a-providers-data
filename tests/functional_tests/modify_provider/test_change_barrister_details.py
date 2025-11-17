import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def _navigate_to_provider_page(page: Page, provider_name: str):
    """Helper function to navigate to a given provider page."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    page.get_by_role("textbox", name="Find a provider").fill(provider_name)
    page.get_by_role("button", name="Search").click()

    # Click on the first provider
    page.get_by_role("link", name=provider_name).click()

    expect(page.get_by_role("heading", name=provider_name)).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_change_name(page: Page):
    _navigate_to_provider_page(page, "Karen Sillen")
    page.get_by_role("link", name="Change barrister name").click()
    expect(page.get_by_role("heading", name="Barrister details")).to_be_visible()
    assert "#barrister_name" in page.url

    expect(page.locator("#barrister_name")).to_have_value("Karen Sillen")
    page.locator("#barrister_name").fill("Functional test name")
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Barrister overview updated successfully")).to_be_visible()
    expect(page.get_by_role("heading", name="Functional test name")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_change_barrister_level(page: Page):
    _navigate_to_provider_page(page, "Karen Sillen")
    page.get_by_role("link", name="Enter barrister level").click()
    expect(page.get_by_role("heading", name="Barrister details")).to_be_visible()
    assert "#barrister_level" in page.url

    expect(page.get_by_role("radio", name="None of the above")).to_be_checked()
    page.get_by_role("radio", name="King's Counsel (KC, previously QC)").click()
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Barrister overview updated successfully")).to_be_visible()
    expect(page.get_by_text("King's Counsel (KC, previously QC)")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_change_bar_council_number(page: Page):
    _navigate_to_provider_page(page, "Karen Sillen")
    page.get_by_role("link", name="Enter barrister level").click()
    expect(page.get_by_role("heading", name="Barrister details")).to_be_visible()
    assert "#barrister_level" in page.url

    expect(page.get_by_role("textbox", name="Bar Council roll number")).to_have_value("5292932")
    page.get_by_role("textbox", name="Bar Council roll number").fill("112233445566778")
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Barrister overview updated successfully")).to_be_visible()
    expect(page.get_by_text("112233445566778")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_cancel(page: Page):
    _navigate_to_provider_page(page, "Karen Sillen")
    page.get_by_role("link", name="Change barrister name").click()

    page.get_by_role("link", name="Cancel").click()
    expect(page.get_by_text("Barrister overview updated successfully")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_no_changes(page: Page):
    _navigate_to_provider_page(page, "Karen Sillen")
    page.get_by_role("link", name="Change barrister name").click()

    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("There is a problem")).to_be_visible()
    expect(
        page.get_by_text("You have not changed anything. Cancel if you do not want to make a change.")
    ).to_be_visible()
