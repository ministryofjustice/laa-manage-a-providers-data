import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_barristers_and_advocates_visible(page: Page) -> None:
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Johnson Legal Services").click()
    expect(page.get_by_role("link", name="Barristers and advocates")).to_be_visible()
    page.get_by_role("link", name="Barristers and advocates").click()
    expect(page.get_by_role("cell", name="Karen Sillen")).to_be_visible()
    expect(page.get_by_role("cell", name="Sophie Lelièvre")).to_be_visible()
    expect(page.get_by_role("button", name="Add another barrister")).to_be_visible()
    expect(page.get_by_role("cell", name="Alan Davies")).to_be_visible()
    expect(page.get_by_role("cell", name="Finn O'Connor")).to_be_visible()
    expect(page.get_by_role("button", name="Add another advocate")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_correct_message_when_no_barristers_or_advocates(page: Page) -> None:
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Northern Legal Chambers").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    expect(page.locator("#main-content")).to_contain_text("No barristers assigned to this chambers")
    expect(page.locator("#main-content")).to_contain_text("No advocates assigned to this chambers")
    expect(page.get_by_role("button", name="Add a barrister")).to_be_visible()
    expect(page.get_by_role("button", name="Add an advocate")).to_be_visible()
