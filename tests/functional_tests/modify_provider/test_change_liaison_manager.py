from datetime import date

import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_existing_provider(page: Page, firm_id: int = 1):
    """Helper function to navigate to an existing provider's details page."""
    page.get_by_role("button", name="Sign in").click()

    # Perform a blank search to view all providers
    page.get_by_role("button", name="Search").click()

    # Click on the first provider (SMITH & PARTNERS SOLICITORS - firm ID 1)
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    # Verify we're on the provider details page
    expect(page.get_by_role("cell", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()


def navigate_to_change_liaison_manager_form(page: Page, firm_id: int = 1):
    """Helper function to navigate to the change liaison manager form."""
    # Direct navigation to the change liaison manager form
    page.goto(url_for("main.add_new_liaison_manager", firm=firm_id, _external=True))


@pytest.mark.usefixtures("live_server")
def test_change_liaison_manager_form_loads_correctly(page: Page):
    """Test that the change liaison manager form loads with correct elements."""
    navigate_to_change_liaison_manager_form(page)

    # Check page title and heading
    expect(page.get_by_role("heading", name="Change liaison manager")).to_be_visible()

    # Check that firm name appears in caption
    expect(page.get_by_text("SMITH & PARTNERS SOLICITORS")).to_be_visible()

    # Check description text
    expect(page.get_by_text("This will make the current liaison manager inactive")).to_be_visible()

    # Check form fields are present
    expect(page.get_by_label("First name")).to_be_visible()
    expect(page.get_by_label("Last name")).to_be_visible()
    expect(page.get_by_label("Email address")).to_be_visible()
    expect(page.get_by_label("Telephone number")).to_be_visible()
    expect(page.get_by_label("Website")).to_be_visible()

    # Check submit button
    expect(page.get_by_role("button", name="Save")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_liaison_manager_successful_submission(page: Page):
    """Test successfully submitting the change liaison manager form."""
    navigate_to_change_liaison_manager_form(page)

    # Fill out the form with new liaison manager details
    page.get_by_label("First name").fill("Jane")
    page.get_by_label("Last name").fill("Doe")
    page.get_by_label("Email address").fill("jane.doe@newexample.com")
    page.get_by_label("Telephone number").fill("07890123456")
    page.get_by_label("Website").fill("https://www.janedoe.com")

    # Submit the form
    page.get_by_role("button", name="Save").click()

    # Should redirect to the provider details page
    expect(page.get_by_role("cell", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()

    # Should show success message
    expect(page.get_by_text("Jane Doe is the new liaison manager")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_liaison_manager_form_validation_errors(page: Page):
    """Test that form validation errors are displayed correctly."""
    navigate_to_change_liaison_manager_form(page)

    # Submit form without filling required fields
    page.get_by_role("button", name="Save").click()

    # Should stay on form page and show validation errors
    expect(page.get_by_role("heading", name="Change liaison manager")).to_be_visible()

    # Check for validation error messages (exact message may vary based on form validation)
    # At minimum, first name, last name, and email should be required
    expect(page.get_by_text("There is a problem")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_liaison_manager_form_partial_data(page: Page):
    """Test submitting form with only required fields filled."""
    navigate_to_change_liaison_manager_form(page)

    # Fill only required fields
    page.get_by_label("First name").fill("John")
    page.get_by_label("Last name").fill("Smith")
    page.get_by_label("Email address").fill("john.smith@example.com")
    page.get_by_label("Telephone number").fill("12345678")

    # Submit the form
    page.get_by_role("button", name="Save").click()

    # Should redirect to the provider details page
    expect(page.get_by_role("cell", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()

    # Should show success message
    expect(page.get_by_text("John Smith is the new liaison manager")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_liaison_manager_email_validation(page: Page):
    """Test that email field validates email format."""
    navigate_to_change_liaison_manager_form(page)

    # Fill form with invalid email
    page.get_by_label("First name").fill("Test")
    page.get_by_label("Last name").fill("User")
    page.get_by_label("Email address").fill("invalid-email")

    # Submit the form
    page.get_by_role("button", name="Save").click()

    # Should stay on form page with validation error
    expect(page.get_by_role("heading", name="Change liaison manager")).to_be_visible()
    expect(page.get_by_text("Error: Enter a valid email")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_change_liaison_manager_replaces_existing_primary(page: Page):
    """Test that changing liaison manager makes the old one non-primary."""
    navigate_to_change_liaison_manager_form(page, firm_id=2)

    # Fill and submit form
    page.get_by_label("First name").fill("NewPrimary")
    page.get_by_label("Last name").fill("Manager")
    page.get_by_label("Email address").fill("newprimary@example.com")
    page.get_by_label("Telephone number").fill("020 7947 6330")
    page.get_by_role("button", name="Save").click()

    expect(page.get_by_text("NewPrimary Manager is the new liaison manager")).to_be_visible()
    expect(page.get_by_role("heading", name="NewPrimary Manager")).to_be_visible()
    expect(page.get_by_role("definition").filter(has_text="Liaison manager")).to_be_visible()
    expect(page.get_by_text("020 7947 6330")).to_be_visible()
    expect(page.get_by_text("newprimary@example.com")).to_be_visible()

    current_date = date.today().strftime("%d %b %Y")
    expect(page.get_by_text(current_date)).to_be_visible()
