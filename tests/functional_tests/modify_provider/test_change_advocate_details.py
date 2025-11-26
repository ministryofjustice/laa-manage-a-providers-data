import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import navigate_to_provider_page


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_change_name(page: Page):
    navigate_to_provider_page(page, "Finn O'Connor")
    page.get_by_role("link", name="Change advocate name").click()
    expect(page.get_by_role("heading", name="Advocate details")).to_be_visible()
    assert "#advocate_name" in page.url

    expect(page.get_by_role("textbox", name="Advocate name")).to_have_value("Finn O'Connor")
    page.get_by_role("textbox", name="Advocate name").fill("Functional test name")
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Advocate overview successfully updated")).to_be_visible()
    expect(page.get_by_role("heading", name="Functional test name")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_change_advocate_level(page: Page):
    navigate_to_provider_page(page, "Finn O'Connor")
    page.get_by_role("link", name="Change advocate level").click()
    expect(page.get_by_role("heading", name="Advocate details")).to_be_visible()
    assert "#advocate_level" in page.url

    expect(page.get_by_role("radio", name="Junior")).to_be_checked()
    page.get_by_role("radio", name="King's Counsel (KC, previously QC)").check()
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Advocate overview successfully updated")).to_be_visible()
    expect(page.get_by_text("King's Counsel (KC, previously QC)")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_change_sra_roll_number(page: Page):
    navigate_to_provider_page(page, "Finn O'Connor")
    page.get_by_role("link", name="Change solicitors Regulation Authority roll number").click()
    expect(page.get_by_role("heading", name="Advocate details")).to_be_visible()
    assert "#sra_roll_number" in page.url

    expect(page.get_by_role("textbox", name="Solicitors Regulation Authority roll number")).to_have_value("5292932")
    page.get_by_role("textbox", name="Solicitors Regulation Authority roll number").fill("1122334")
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Advocate overview successfully updated")).to_be_visible()
    expect(page.get_by_text("1122334")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_cancel(page: Page):
    navigate_to_provider_page(page, "Finn O'Connor")
    page.get_by_role("link", name="Change advocate name").click()

    page.get_by_role("link", name="Cancel").click()
    expect(page.get_by_text("Advocate overview successfully updated")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_barrister_details_no_changes(page: Page):
    navigate_to_provider_page(page, "Finn O'Connor")
    page.get_by_role("link", name="Change advocate name").click()

    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("There is a problem")).to_be_visible()
    expect(
        page.get_by_text("You have not changed anything. Cancel if you do not want to make a change.")
    ).to_be_visible()
