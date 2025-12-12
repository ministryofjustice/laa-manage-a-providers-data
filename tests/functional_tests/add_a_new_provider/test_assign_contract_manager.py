import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_assign_contract_manager_via_lsp(page: Page):
    """Helper function to navigate to Assign Contract Manager form via the LSP flow."""
    # Start with add parent provider
    page.goto(url_for("main.add_parent_provider", _external=True))

    # Fill provider details form
    page.get_by_role("textbox", name="Provider name").fill("Test Legal Services Provider")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()

    # Fill LSP details form
    page.get_by_role("radio", name="Limited company").click()
    page.get_by_role("textbox", name="Day").fill("01")
    page.get_by_role("textbox", name="Month").fill("01")
    page.get_by_role("textbox", name="Year").fill("2020")
    page.get_by_role("textbox", name="Companies House number").fill("12345678")
    page.get_by_role("button", name="Continue").click()

    # Fill head office contact details form
    page.get_by_role("textbox", name="Address line 1").fill("123 Head Office Street")
    page.get_by_role("textbox", name="Town or city").fill("Head Office City")
    page.get_by_role("textbox", name="Postcode").fill("HO1 2CE")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("headoffice@testlsp.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Head Office Centre")
    page.get_by_role("button", name="Continue").click()

    # Fill VAT registration form (optional, skip by submitting empty)
    expect(page.get_by_role("heading", name="Head office: VAT Registration number (optional)")).to_be_visible()
    page.get_by_role("button", name="Continue").click()

    # Fill bank account form
    expect(page.get_by_role("heading", name="Head office: Bank account details")).to_be_visible()
    page.get_by_role("textbox", name="Account name").fill("Test Business Account")
    page.get_by_role("textbox", name="Sort code").fill("123456")
    page.get_by_role("textbox", name="Account number").fill("12345678")
    page.get_by_role("button", name="Continue").click()

    # Fill liaison manager form
    expect(page.get_by_role("heading", name="Add liaison manager")).to_be_visible()
    page.get_by_role("textbox", name="First name").fill("John")
    page.get_by_role("textbox", name="Last name").fill("Smith")
    page.get_by_role("textbox", name="Email address").fill("john.smith@testlsp.com")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("button", name="Continue").click()

    # Should now be on the Assign Contract Manager page
    expect(page.get_by_role("heading", name="Assign contract manager")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_form_loads_correctly(page: Page):
    """Test that the Assign Contract Manager form loads correctly via LSP flow."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Verify the page title
    expect(page.get_by_role("heading", name="Assign contract manager")).to_be_visible()

    # Verify the hint text
    expect(
        page.get_by_text("Contact mapd@justice.gov.uk if you cannot find the contract manager you want to assign.")
    ).to_be_visible()

    # Verify form elements are present
    expect(page.get_by_role("textbox", name="Search for a contract manager")).to_be_visible()
    expect(page.get_by_role("button", name="Search")).to_be_visible()

    # Verify that contract managers are visible by default (10 contract managers available)
    expect(page.get_by_role("radio")).to_have_count(10)
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_search_functionality(page: Page):
    """Test that the search functionality works correctly."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for a contract manager
    page.get_by_role("textbox", name="Search for a contract manager").fill("Alice")
    page.get_by_role("button", name="Search").click()

    # Should show search results
    expect(page.get_by_text("1 search result for 'Alice'")).to_be_visible()
    expect(page.get_by_role("radio", name="Select this row")).to_be_visible()
    expect(page.get_by_text("Alice Brown")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_search_multiple_results(page: Page):
    """Test search that returns multiple results."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for a common name
    page.get_by_role("textbox", name="Search for a contract manager").fill("Davies")
    page.get_by_role("button", name="Search").click()

    # Should show multiple search results
    expect(page.get_by_text("1 search result for 'Davies'")).to_be_visible()
    expect(page.get_by_text("Alan Davies")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_search_no_results(page: Page):
    """Test search that returns no results."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for non-existent name
    page.get_by_role("textbox", name="Search for a contract manager").fill("Nonexistent")
    page.get_by_role("button", name="Search").click()

    # Should show no search results
    expect(page.get_by_text("0 search results for 'Nonexistent'")).to_be_visible()
    expect(page.get_by_role("radio")).not_to_be_visible()
    expect(page.get_by_role("button", name="Submit")).not_to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_case_insensitive_search(page: Page):
    """Test that search is case insensitive."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search with lowercase
    page.get_by_role("textbox", name="Search for a contract manager").fill("alice")
    page.get_by_role("button", name="Search").click()

    # Should still find Alice Brown
    expect(page.get_by_text("1 search result for 'alice'")).to_be_visible()
    expect(page.get_by_text("Alice Brown")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_form_validation_no_selection(page: Page):
    """Test form validation when no contract manager is selected."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for a contract manager
    page.get_by_role("textbox", name="Search for a contract manager").fill("Alice")
    page.get_by_role("button", name="Search").click()

    # Submit without selecting a radio button
    page.get_by_role("button", name="Submit").click()

    # Should show validation error
    expect(
        page.get_by_text(
            "Error: Select a contract manager, search again or skip this step if you do not know the contract manager"
        )
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_form_skip(page: Page):
    """Test form validation when no contract manager is selected."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for a contract manager
    page.get_by_role("textbox", name="Search for a contract manager").fill("Alice")
    page.get_by_role("button", name="Search").click()

    # Submit without selecting a radio button
    page.get_by_role("button", name="Unknown: Skip this step").click()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_successful_submission(page: Page):
    """Test successful contract manager assignment."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for a contract manager
    page.get_by_role("textbox", name="Search for a contract manager").fill("Alice")
    page.get_by_role("button", name="Search").click()

    # Select the contract manager
    page.get_by_role("radio", name="Select this row").click()

    # Submit the form
    page.get_by_role("button", name="Submit").click()

    # Should complete the flow successfully and redirect away from assign contract manager
    current_url = page.url
    assert "assign-contract-manager" not in current_url


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_search_term_validation(page: Page):
    """Test search term length validation."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search with term that's too long (over 100 characters)
    long_search_term = "a" * 101
    page.get_by_role("textbox", name="Search for a contract manager").fill(long_search_term)
    page.get_by_role("button", name="Search").click()

    # Should show validation error for search term
    expect(page.get_by_text("Error: Search term must be 100 characters or less")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_maintains_search_term_after_submission_error(page: Page):
    """Test that search term is maintained after form submission with validation errors."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for a contract manager
    search_term = "Alice"
    page.get_by_role("textbox", name="Search for a contract manager").fill(search_term)
    page.get_by_role("button", name="Search").click()

    # Submit without selecting (causing validation error)
    page.get_by_role("button", name="Submit").click()

    # Search term should still be visible in the form
    expect(page.get_by_role("textbox", name="Search for a contract manager")).to_have_value(search_term)
    expect(page.get_by_text("1 search result for 'Alice'")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_empty_search_shows_all_results(page: Page):
    """Test that an empty search shows all contract managers."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Submit empty search
    page.get_by_role("textbox", name="Search for a contract manager").fill("")
    page.get_by_role("button", name="Search").click()

    # Should show all contract managers (10 total)
    expect(page.get_by_role("radio")).to_have_count(10)
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_without_head_office_session_gives_error(page: Page):
    """Test that accessing Assign Contract Manager form without head office session data gives 400 error."""
    # Start provider flow but don't complete head office details
    page.goto(url_for("main.add_parent_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test LSP")
    page.get_by_role("radio", name="Legal services provider").click()
    page.get_by_role("button", name="Continue").click()

    # Try to access Assign Contract Manager form directly without completing head office details
    page.goto(url_for("main.assign_contract_manager", _external=True))

    # Should get 400 error since head office session data doesn't exist
    assert page.title() == "400 Bad Request"


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_chambers_provider_gives_error(page: Page):
    """Test that accessing Assign Contract Manager form with Chambers provider gives 400 error."""
    # Start with Chambers provider
    page.goto(url_for("main.add_parent_provider", _external=True))
    page.get_by_role("textbox", name="Provider name").fill("Test Chambers")
    page.get_by_role("radio", name="Chambers").click()
    page.get_by_role("button", name="Continue").click()

    # Complete chambers flow
    page.get_by_role("textbox", name="Address line 1").fill("123 Chambers Street")
    page.get_by_role("textbox", name="Town or city").fill("Chambers City")
    page.get_by_role("textbox", name="Postcode").fill("CH1 2CE")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("chambers@testchambers.com")
    page.get_by_role("textbox", name="DX number").fill("DX123456")
    page.get_by_role("textbox", name="DX centre").fill("Chambers Centre")
    page.get_by_role("button", name="Continue").click()

    # Try to access Assign Contract Manager form (should not be accessible for Chambers)
    page.goto(url_for("main.assign_contract_manager", _external=True))

    # Should get 400 error since this is only for LSPs
    assert page.title() == "400 Bad Request"


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_table_displays_correctly(page: Page):
    """Test that the contract manager table displays correctly with proper structure."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for a contract manager
    page.get_by_role("textbox", name="Search for a contract manager").fill("Alice")
    page.get_by_role("button", name="Search").click()

    # Check table structure and content
    expect(page.get_by_role("table")).to_be_visible()
    expect(page.get_by_role("columnheader", name="Name")).to_be_visible()
    expect(page.get_by_role("cell", name="Alice Brown")).to_be_visible()
    expect(page.get_by_role("radio", name="Select this row")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_assign_contract_manager_partial_name_search(page: Page):
    """Test that partial name searches work correctly."""
    navigate_to_assign_contract_manager_via_lsp(page)

    # Search for partial name
    page.get_by_role("textbox", name="Search for a contract manager").fill("John")
    page.get_by_role("button", name="Search").click()

    # Should find managers with "John" in their name
    expect(page.get_by_text("1 search result for 'John'")).to_be_visible()
    expect(page.get_by_text("Sarah Johnson")).to_be_visible()
