import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_add_office_form(page: Page):
    """Helper function to navigate to the Add Office form via UI flow."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    # Click on the first provider (should be "SMITH & PARTNERS SOLICITORS" from fixtures)
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()

    # Click "Add an office" button
    page.get_by_role("button", name="Add an office").click()

    # Verify we're on the add office page
    expect(page.get_by_role("heading", name="Add a new office")).to_be_visible()
    expect(page.get_by_text("SMITH & PARTNERS SOLICITORS")).to_be_visible()  # Caption should show firm name


@pytest.mark.usefixtures("live_server")
def test_add_office_form_loads_via_ui(page: Page):
    """Test that the Add Office form loads correctly via UI navigation."""
    navigate_to_add_office_form(page)

    # Verify form elements are present
    expect(page.get_by_role("textbox", name="Office name")).to_be_visible()
    expect(page.get_by_role("radio", name="Yes")).to_be_visible()
    expect(page.get_by_role("radio", name="No")).to_be_visible()
    expect(page.get_by_role("button", name="Continue")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_name_validation_required(page: Page):
    """Test that office name is required."""
    navigate_to_add_office_form(page)

    # Try to submit without filling office name
    page.get_by_role("radio", name="Yes").click()
    page.get_by_role("button", name="Continue").click()

    # Should show validation error
    expect(page.get_by_text("Error: Enter the office name")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_name_validation_length(page: Page):
    """Test that office name validates maximum length."""
    navigate_to_add_office_form(page)

    # Fill with an office name that's too long (over 320 characters)
    long_name = "A" * 321  # 321 characters
    page.get_by_role("textbox", name="Office name").fill(long_name)
    page.get_by_role("radio", name="Yes").click()
    page.get_by_role("button", name="Continue").click()

    # Should show validation error
    expect(page.get_by_text("Error: Office name must be less than 320 characters")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_head_office_selection_required(page: Page):
    """Test that head office selection is required."""
    navigate_to_add_office_form(page)

    # Fill office name but don't select head office option
    page.get_by_role("textbox", name="Office name").fill("Test Office")
    page.get_by_role("button", name="Continue").click()

    # Should show validation error
    expect(page.get_by_text("Error: Select yes if this is the head office")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_valid_form_submission_head_office_yes(page: Page):
    """Test successful form submission when selecting 'Yes' for head office."""
    navigate_to_add_office_form(page)

    # Fill all required fields
    page.get_by_role("textbox", name="Office name").fill("Main Office")
    page.get_by_role("radio", name="Yes").click()
    page.get_by_role("button", name="Continue").click()

    # Should go to the office details form
    expect(page.get_by_role("heading", name="Office contact details")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_valid_form_submission_head_office_no(page: Page):
    """Test successful form submission when selecting 'No' for head office."""
    navigate_to_add_office_form(page)

    # Fill all required fields
    page.get_by_role("textbox", name="Office name").fill("Branch Office")
    page.get_by_role("radio", name="No").click()
    page.get_by_role("button", name="Continue").click()

    # Should go to the office details form
    expect(page.get_by_role("heading", name="Office contact details")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_office_name_accepts_valid_length(page: Page):
    """Test that office name accepts valid length (exactly 320 characters)."""
    navigate_to_add_office_form(page)

    # Fill with exactly 320 characters (should be valid)
    valid_name = "A" * 320
    page.get_by_role("textbox", name="Office name").fill(valid_name)
    page.get_by_role("radio", name="Yes").click()
    page.get_by_role("button", name="Continue").click()

    # Should not show validation error and should redirect
    expect(page.get_by_text("Error: Office name must be less than 320 characters")).not_to_be_visible()
    expect(page.get_by_role("heading", name="Office contact details")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_form_caption_shows_correct_firm_name(page: Page):
    """Test that the form caption shows the correct firm name."""
    navigate_to_add_office_form(page)

    # The caption should show the firm name from the URL parameter
    expect(page.get_by_text("SMITH & PARTNERS SOLICITORS")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_form_labels(page: Page):
    """Test that form elements have proper labels."""
    navigate_to_add_office_form(page)

    # Check that the office name field has proper labeling
    office_name_field = page.get_by_role("textbox", name="Office name")
    expect(office_name_field).to_be_visible()

    # Check that the radio group has proper labeling
    expect(page.get_by_text("Is this the head office?")).to_be_visible()

    # Check that continue button is properly labeled
    continue_button = page.get_by_role("button", name="Continue")
    expect(continue_button).to_be_visible()
