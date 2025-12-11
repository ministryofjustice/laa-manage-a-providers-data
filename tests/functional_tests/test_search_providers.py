import pytest
from playwright.sync_api import expect


@pytest.mark.usefixtures("live_server")
def test_search_providers_page_ui_loads(page):
    page.get_by_role("button", name="Sign in").click()
    expect(page.get_by_role("heading", name="Provider records")).to_be_visible()
    expect(page.get_by_text("Find a provider")).to_be_visible()
    expect(page.get_by_text("You can search by name,")).to_be_visible()
    expect(page.get_by_role("textbox", name="Find a provider")).to_be_visible()
    expect(page.get_by_role("button", name="Search")).to_be_visible()
    expect(page.get_by_role("button", name="Add a new parent provider")).to_be_visible()

    # Check table is not visible
    expect(page.get_by_role("columnheader", name="Provider name")).not_to_be_visible()
    expect(page.get_by_role("columnheader", name="Provider type")).not_to_be_visible()
    expect(page.get_by_role("columnheader", name="Account number")).not_to_be_visible()
    expect(page.get_by_role("columnheader", name="Status")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_empty_search_shows_all_providers(page):
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_role("columnheader", name="Provider name")).to_be_visible()
    expect(page.get_by_role("columnheader", name="Provider type")).to_be_visible()
    expect(page.get_by_role("columnheader", name="Account number")).to_be_visible()
    expect(page.get_by_role("columnheader", name="Status")).to_be_visible()
    expect(page.get_by_text("Showing 1 to 14 of 14 results")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_search_shows_correct__providers(page):
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("textbox", name="Find a provider").fill("Metro")
    page.get_by_role("button", name="Search").click()
    expect(page.get_by_role("heading", name="search result for ‘Metro’")).to_be_visible()
    expect(page.get_by_role("cell", name="Metropolitan Law Centre")).to_be_visible()
    expect(page.get_by_role("cell", name="Legal Services Provider")).to_be_visible()
    expect(page.get_by_role("cell", name="3")).to_be_visible()
    expect(page.get_by_role("cell", name="No statuses")).to_be_visible()
    expect(page.get_by_text("Showing 1 to 1 of 1 results")).to_be_visible()
