import pytest
from flask import url_for
from playwright.sync_api import Page, expect

ROUTING = [
    {"link_text": "Barrister", "next_page_heading": "Assign to parent provider"},
    {"link_text": "Advocate", "next_page_heading": "Assign to parent provider"},
    {"link_text": "Chambers", "next_page_heading": "Chambers details"},
    {"link_text": "Legal services provider", "next_page_heading": "Legal services provider details"},
]


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("routing", ROUTING)
def test_add_provider_routing(page: Page, routing: dict):
    page.goto(url_for("main.add_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test")
    page.get_by_role("radio", name=routing["link_text"]).click()
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text(routing["next_page_heading"])).to_be_visible()
