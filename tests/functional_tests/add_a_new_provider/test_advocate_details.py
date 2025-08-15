import pytest
from playwright.sync_api import expect


def navigate_to_advocate_details_page(page):
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Add a new provider").click()
    page.get_by_role("textbox", name="Provider name").click()
    page.get_by_role("textbox", name="Provider name").fill("Test provider")
    page.get_by_role("radio", name="Advocate").check()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Assign to a chambers")).to_be_visible()
    page.get_by_role("row", name="Select this row JOHNSON").get_by_label("Select this row").check()
    page.get_by_role("button", name="Continue").click()


@pytest.mark.usefixtures("live_server")
def test_advocate_details_page(page):
    navigate_to_advocate_details_page(page)
    expect(page.get_by_text("Test provider")).to_be_visible()
    expect(page.get_by_role("heading", name="Advocate details")).to_be_visible()
    expect(page.get_by_text("Is the provider a solicitor advocate? (optional)")).to_be_visible()
    expect(page.get_by_text("Advocate level")).to_be_visible()
    expect(page.get_by_text("Pupil")).to_be_visible()
    expect(page.get_by_text("Junior")).to_be_visible()
    expect(page.get_by_text("King's Counsel (KC,")).to_be_visible()
    expect(page.get_by_text("Bar Council roll number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_valid_form_submission(page):
    navigate_to_advocate_details_page(page)
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("radio", name="Pupil").check()
    page.get_by_role("textbox", name="Bar Council roll number").click()
    page.get_by_role("textbox", name="Bar Council roll number").fill("123")
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_role("heading", name="Chambers details")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_blank_form_submission(page):
    navigate_to_advocate_details_page(page)
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text("Error: Select the advocate level")).to_be_visible()
    expect(page.get_by_text("Error: Enter the Bar Council Roll number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bar_council_max_characters_form_submission(page):
    navigate_to_advocate_details_page(page)
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("radio", name="King's Counsel (KC,").check()
    page.get_by_role("textbox", name="Bar Council roll number").fill("12345678911523456789")
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text("Error: Bar Council roll")).to_be_visible()
