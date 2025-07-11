import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_example_form(page: Page):
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("textbox", name="Your full name").fill("Alice")
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text("Your name is Alice")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_example_form_errors(page: Page):
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text("Error: Enter your name")).to_be_visible()
