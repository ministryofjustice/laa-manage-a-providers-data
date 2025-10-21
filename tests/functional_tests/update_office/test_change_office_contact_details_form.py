import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_example(page: Page) -> None:
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    # Search for "Smith" to find "SMITH & PARTNERS SOLICITORS"
    page.get_by_role("textbox", name="Find a provider").fill("smith")
    page.get_by_role("button", name="Search").click()

    # Click on the first provider (should be "SMITH & PARTNERS SOLICITORS" from fixtures)
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    # Click on the Offices sub-navigation
    page.get_by_role("link", name="Offices").click()

    # Click "A specific office" button
    page.get_by_role("link", name="1A001L").click()

    # Verify we're on view office page
    expect(page.get_by_role("heading", name="Office: 1A001L")).to_be_visible()

    page.get_by_text("Contact").click()
    expect(page.get_by_role("heading", name="Office contact details")).to_be_visible()

    page.get_by_role("link", name="Change   address").click()
    page.get_by_role("textbox", name="Address line 1").fill("14 Apple Street")
    page.get_by_role("textbox", name="Address line 2 (optional)").fill("Fifth Floor")
    page.get_by_role("textbox", name="Address line 3 (optional)").fill("Door 11")
    page.get_by_role("textbox", name="Address line 4 (optional)").fill("Doorbell 7")
    page.get_by_role("textbox", name="Town or city").fill("Newbury")
    page.get_by_role("textbox", name="County (optional)").fill("Berkshire")
    page.get_by_role("textbox", name="Postcode").fill("NE12 7SD")
    page.get_by_role("button", name="Submit").click()
    expect(page.locator("dd").filter(has_text="14 Apple Street")).to_be_visible()
    expect(page.locator("dd").filter(has_text="Fifth Floor")).to_be_visible()
    expect(page.locator("dd").filter(has_text="Door 11")).to_be_visible()
    expect(page.locator("dd").filter(has_text="Doorbell 7")).to_be_visible()
    expect(page.locator("dd").filter(has_text="Newbury")).to_be_visible()
    expect(page.locator("dd").filter(has_text="NE12 7SD")).to_be_visible()

    page.get_by_role("link", name="Change   email address").click()
    expect(page.get_by_role("textbox", name="Email address (optional)")).to_be_visible()
    page.get_by_role("textbox", name="Email address (optional)").fill("exampleemail@example.com")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("exampleemail@example.com")).to_be_visible()

    page.get_by_role("link", name="Change   telephone number").click()
    expect(page.get_by_role("textbox", name="Telephone number (optional)")).to_be_visible()
    page.get_by_role("textbox", name="Telephone number (optional)").fill("0475984125")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("0475984125")).to_be_visible()

    page.get_by_role("link", name="Enter DX number").click()
    page.get_by_role("textbox", name="DX number (optional)").fill("5481587")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("5481587")).to_be_visible()

    page.get_by_role("link", name="Enter DX centre").click()
    page.get_by_role("textbox", name="DX centre (optional)").fill("Leeds")
    page.get_by_role("button", name="Submit").click()
    expect(page.get_by_text("Leeds")).to_be_visible()
