import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_assign_parent_provider(page: Page):
    """Helper function to navigate to assign parent provider page via UI flow."""
    page.goto(url_for("main.add_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test Barrister")
    page.get_by_role("radio", name="Barrister").click()
    page.get_by_role("button", name="Continue").click()
    # Should now be on the assign parent provider page
    expect(page.get_by_role("heading", name="Assign to parent provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_parent_provider_page_loads_via_ui(page: Page):
    """Test that the assign parent provider page loads correctly via UI navigation."""
    navigate_to_assign_parent_provider(page)
    expect(page.get_by_role("textbox", name="Search for a parent provider")).to_be_visible()
    expect(page.get_by_role("button", name="Search")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_search_functionality_shows_results(page: Page):
    """Test that searching for a provider shows results."""
    navigate_to_assign_parent_provider(page)

    # Search for "Johnson" which should match "JOHNSON LEGAL SERVICES"
    page.get_by_role("textbox", name="Search for a parent provider").fill("Johnson")
    page.get_by_role("button", name="Search").click()

    # Should show the results table and continue button
    expect(page.locator("text=JOHNSON LEGAL SERVICES")).to_be_visible()
    expect(page.get_by_role("button", name="Continue")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_search_functionality_shows_no_results_error(page: Page):
    """Test that searching for non-existent provider shows error."""
    navigate_to_assign_parent_provider(page)

    # Search for something that doesn't exist
    page.get_by_role("textbox", name="Search for a parent provider").fill("NonExistentProvider")
    page.get_by_role("button", name="Search").click()

    # Should show error message and no results table
    expect(
        page.locator(
            ".govuk-error-message", has_text="No providers found. Check the spelling and search for something else."
        )
    ).to_be_visible()
    expect(page.get_by_role("button", name="Continue")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_search_field_validation_max_length(page: Page):
    """Test that search field validates maximum length."""
    navigate_to_assign_parent_provider(page)

    # Try to enter more than 100 characters
    long_search = "a" * 101
    page.get_by_role("textbox", name="Search for a parent provider").fill(long_search)
    page.get_by_role("button", name="Search").click()

    # Should show length validation error
    expect(page.locator(".govuk-error-message", has_text="Search term must be 100 characters or less")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_search_filters_only_chambers(page: Page):
    """Test that search only shows Chambers providers."""
    navigate_to_assign_parent_provider(page)

    # Search for something that matches both Chambers and LSP
    page.get_by_role("textbox", name="Search for a parent provider").fill("LEGAL")
    page.get_by_role("button", name="Search").click()

    # Should only show Chambers providers, not Legal Services Providers
    expect(page.locator("text=NORTHERN LEGAL CHAMBERS")).to_be_visible()
    expect(page.locator("text=METROPOLITAN LAW CENTRE")).not_to_be_visible()  # This is LSP


@pytest.mark.usefixtures("live_server")
def test_search_by_firm_name(page: Page):
    """Test that search works by firm name."""
    navigate_to_assign_parent_provider(page)

    # Search by partial firm name
    page.get_by_role("textbox", name="Search for a parent provider").fill("Westminster")
    page.get_by_role("button", name="Search").click()

    # Should find WESTMINSTER SOLICITORS LLP
    expect(page.locator("text=WESTMINSTER SOLICITORS LLP")).to_be_visible()
    expect(page.locator("text=Chambers")).to_be_visible()  # Should show firm type


@pytest.mark.usefixtures("live_server")
def test_search_by_firm_id(page: Page):
    """Test that search works by firm ID/number."""
    navigate_to_assign_parent_provider(page)

    # Search by firm ID (should match firmId: 2)
    page.get_by_role("textbox", name="Search for a parent provider").fill("2")
    page.get_by_role("button", name="Search").click()

    # Should find the firm with firmId 2 (JOHNSON LEGAL SERVICES)
    expect(page.locator("text=JOHNSON LEGAL SERVICES")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_case_insensitive_search(page: Page):
    """Test that search is case insensitive."""
    navigate_to_assign_parent_provider(page)

    # Search with different case
    page.get_by_role("textbox", name="Search for a parent provider").fill("johnson")
    page.get_by_role("button", name="Search").click()

    # Should still find JOHNSON LEGAL SERVICES
    expect(page.locator("text=JOHNSON LEGAL SERVICES")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_search_preserves_search_term(page: Page):
    """Test that search term is preserved after search."""
    navigate_to_assign_parent_provider(page)

    search_term = "Johnson"
    page.get_by_role("textbox", name="Search for a parent provider").fill(search_term)
    page.get_by_role("button", name="Search").click()

    # Search field should still contain the search term
    expect(page.get_by_role("textbox", name="Search for a parent provider")).to_have_value(search_term)


@pytest.mark.usefixtures("live_server")
def test_select_parent_provider_requires_selection(page: Page):
    """Test that submitting without selecting a provider shows validation error."""
    navigate_to_assign_parent_provider(page)

    # Search to show results
    page.get_by_role("textbox", name="Search for a parent provider").fill("Johnson")
    page.get_by_role("button", name="Search").click()

    # Try to continue without selecting a provider
    page.get_by_role("button", name="Continue").click()

    # Should show validation error
    expect(page.locator(".govuk-error-message", has_text="Select a parent provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_select_parent_provider_success(page: Page):
    """Test successful parent provider selection."""
    navigate_to_assign_parent_provider(page)

    # Search to show results
    page.get_by_role("textbox", name="Search for a parent provider").fill("Johnson")
    page.get_by_role("button", name="Search").click()

    # Select a provider (assuming radio buttons are rendered for the table)
    page.locator("input[type='radio'][value='2']").click()
    page.get_by_role("button", name="Continue").click()

    # Should redirect to success page - check that we're no longer on assign parent provider page
    page.wait_for_function("() => !document.title.includes('Assign to parent provider')", timeout=10000)
    # Verify we've navigated away from the assign parent provider page
    expect(page.get_by_role("heading", name="Assign to parent provider")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_advocate_also_navigates_to_assign_parent_provider(page: Page):
    """Test that selecting Advocate also leads to assign parent provider page."""
    page.goto(url_for("main.add_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test Advocate")
    page.get_by_role("radio", name="Advocate").click()
    page.get_by_role("button", name="Continue").click()

    # Should also be on the assign parent provider page
    expect(page.get_by_role("heading", name="Assign to parent provider")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_pagination_with_search(page: Page):
    """Test pagination works with search results."""
    navigate_to_assign_parent_provider(page)

    # Search for "chambers" to get multiple results
    page.get_by_role("textbox", name="Search for a parent provider").fill("chambers")
    page.get_by_role("button", name="Search").click()

    # If there are multiple results, pagination should be visible
    # This test assumes we have more than 7 chambers (the limit per page)
    # If pagination is shown, test it maintains search term
    if page.locator("text=Next").is_visible():
        page.locator("text=Next").click()
        # Search term should still be preserved in URL and field
        expect(page.get_by_role("textbox", name="Search for a parent provider")).to_have_value("chambers")
