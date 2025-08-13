import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_add_parent_provider_page_loads(page: Page):
    """Test that the Add Parent Provider page loads correctly"""
    page.goto(url_for("main.add_parent_provider", _external=True))
    
    # Check page title/heading
    expect(page.get_by_text("Add a new parent provider")).to_be_visible()
    
    # Check search field is present
    expect(page.get_by_role("textbox", name="Search for parent provider")).to_be_visible()
    
    # Check search button is present
    expect(page.get_by_role("button", name="Search")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_parent_provider_search_validation(page: Page):
    """Test that search validation works correctly"""
    page.goto(url_for("main.add_parent_provider", _external=True))
    
    # Click search button without entering search term
    page.get_by_role("button", name="Search").click()
    
    # Check validation error appears
    expect(page.get_by_text("Enter a search term for the parent provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_parent_provider_search_functionality(page: Page):
    """Test that search functionality works"""
    page.goto(url_for("main.add_parent_provider", _external=True))
    
    # Enter search term
    search_term = "Test Provider"
    page.get_by_role("textbox", name="Search for parent provider").fill(search_term)
    
    # Click search button
    page.get_by_role("button", name="Search").click()
    
    # Check that the page still shows the form (since we're using mock results)
    expect(page.get_by_text("Add a new parent provider")).to_be_visible()
    expect(page.get_by_role("textbox", name="Search for parent provider")).to_have_value(search_term)


@pytest.mark.usefixtures("live_server")
def test_add_parent_provider_routing_from_add_provider(page: Page):
    """Test routing from Add Provider page to Add Parent Provider page"""
    # Start at Add Provider page
    page.goto(url_for("main.add_provider", _external=True))
    
    # Fill in provider name
    page.get_by_role("textbox", name="Provider name").fill("Test Provider")
    
    # Select Chambers (should route to Add Parent Provider)
    page.get_by_role("radio", name="Chambers").click()
    
    # Click Continue
    page.get_by_role("button", name="Continue").click()
    
    # Should be on Add Parent Provider page
    expect(page.get_by_text("Add a new parent provider")).to_be_visible()
    expect(page.get_by_role("textbox", name="Search for parent provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
@pytest.mark.parametrize("provider_type", ["Barrister", "Advocate", "Chambers"])
def test_add_parent_provider_routing_for_all_types(page: Page, provider_type: str):
    """Test that Barrister, Advocate, and Chambers all route to Add Parent Provider"""
    # Start at Add Provider page
    page.goto(url_for("main.add_provider", _external=True))
    
    # Fill in provider name
    page.get_by_role("textbox", name="Provider name").fill("Test Provider")
    
    # Select provider type
    page.get_by_role("radio", name=provider_type).click()
    
    # Click Continue
    page.get_by_role("button", name="Continue").click()
    
    # Should be on Add Parent Provider page
    expect(page.get_by_text("Add a new parent provider")).to_be_visible()
    expect(page.get_by_role("textbox", name="Search for parent provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_lsp_still_routes_to_lsp_details(page: Page):
    """Test that Legal Services Provider still routes to LSP details page"""
    # Start at Add Provider page
    page.goto(url_for("main.add_provider", _external=True))
    
    # Fill in provider name
    page.get_by_role("textbox", name="Provider name").fill("Test Provider")
    
    # Select Legal services provider
    page.get_by_role("radio", name="Legal services provider").click()
    
    # Click Continue
    page.get_by_role("button", name="Continue").click()
    
    # Should be on LSP details page, NOT Add Parent Provider page
    expect(page.get_by_text("Legal services provider details")).to_be_visible()
    expect(page.get_by_text("Add a new parent provider")).not_to_be_visible()
