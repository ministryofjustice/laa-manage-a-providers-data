import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_assign_chambers_form(page: Page, firm_id: int):
    """Helper function to navigate to the assign chambers form."""
    page.goto(url_for("main.assign_chambers", firm=firm_id, _external=True))


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_form_loads_correctly_for_advocate(page: Page):
    """Test that the assign chambers form loads with correct elements for an advocate."""
    # Use firm_id 4 which is an Advocate
    navigate_to_assign_chambers_form(page, 4)

    # Check page title and heading
    expect(page.get_by_role("heading", name="Assign chambers for Alan Davies")).to_be_visible()

    # Check search field is present
    expect(page.get_by_label("Search for a chambers")).to_be_visible()
    expect(page.get_by_text("You can search by name or account number")).to_be_visible()

    # Check search button
    expect(page.get_by_role("button", name="Search")).to_be_visible()

    # Check submit button
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_search_functionality(page: Page):
    """Test that searching for chambers returns appropriate results."""
    navigate_to_assign_chambers_form(page, 4)

    # Search for "JOHNSON" which should find Johnson Legal Services (Chambers)
    page.get_by_label("Search for a chambers").fill("JOHNSON")
    page.get_by_role("button", name="Search").click()

    # Should show search results
    expect(page.get_by_text("Johnson Legal Services")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_search_by_account_number(page: Page):
    """Test searching for chambers by account number."""
    navigate_to_assign_chambers_form(page, 4)

    # Search by firm number/ID
    page.get_by_label("Search for a chambers").fill("2")
    page.get_by_role("button", name="Search").click()

    # Should find Johnson Legal Services (firm_id 2)
    expect(page.get_by_text("Johnson Legal Services")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_validation_error_no_selection(page: Page):
    """Test that validation error appears when no chambers is selected."""
    navigate_to_assign_chambers_form(page, 4)

    # Search for chambers first
    page.get_by_label("Search for a chambers").fill("JOHNSON")
    page.get_by_role("button", name="Search").click()

    # Submit without selecting a chambers
    page.get_by_role("button", name="Submit").click()

    # Should show validation error with dynamic message including firm type
    expect(page.get_by_text("There is a problem")).to_be_visible()
    expect(page.get_by_text("Error: Select a chambers to assign the advocate to")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_successful_submission(page: Page):
    """Test successfully assigning an advocate to chambers."""
    navigate_to_assign_chambers_form(page, 4)

    # Search for chambers
    page.get_by_label("Search for a chambers").fill("NORTHERN")
    page.get_by_role("button", name="Search").click()

    # Select the first chambers result
    page.get_by_role("radio").first.click()

    # Submit the form
    page.get_by_role("button", name="Submit").click()

    # Should redirect to providers list with success message
    expect(page.get_by_text("Alan Davies assigned to Northern Legal Chambers")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_search_validation_too_long(page: Page):
    """Test that search term validation works for terms that are too long."""
    navigate_to_assign_chambers_form(page, 4)

    # Enter a search term longer than 100 characters
    long_search_term = "a" * 101
    page.get_by_label("Search for a chambers").fill(long_search_term)
    page.get_by_role("button", name="Search").click()

    # Should show validation error
    expect(page.get_by_text("Error: Search term must be 100 characters or less")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_no_search_results(page: Page):
    """Test behavior when search returns no results."""
    navigate_to_assign_chambers_form(page, 4)

    # Search for something that won't exist
    page.get_by_label("Search for a chambers").fill("NONEXISTENT")
    page.get_by_role("button", name="Search").click()

    expect(page.get_by_role("heading", name="0 search results for ‘NONEXISTENT’")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_case_insensitive_search(page: Page):
    """Test that search is case-insensitive."""
    navigate_to_assign_chambers_form(page, 4)

    # Search with different cases
    page.get_by_label("Search for a chambers").fill("johnson")
    page.get_by_role("button", name="Search").click()

    # Should still find Johnson Legal Services
    expect(page.get_by_text("Johnson Legal Services")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_chambers_form_preserves_search_term(page: Page):
    """Test that the search term is preserved after searching."""
    navigate_to_assign_chambers_form(page, 4)

    search_term = "JOHNSON"
    page.get_by_label("Search for a chambers").fill(search_term)
    page.get_by_role("button", name="Search").click()

    # The search field should still contain the search term
    expect(page.get_by_label("Search for a chambers")).to_have_value(search_term)
