import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_add_barrister_form_loads_from_chambers(page: Page) -> None:
    # Navigate to a chambers provider and then to add barrister form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()  # This is a chambers
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    # Check form loads correctly
    expect(page.get_by_role("heading", name="Barrister details")).to_be_visible()
    expect(page.get_by_text("Barrister name")).to_be_visible()
    expect(page.get_by_text("Barrister level")).to_be_visible()
    expect(page.get_by_text("Bar Council roll number")).to_be_visible()
    expect(page.get_by_role("button", name="Submit")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_barrister_form_not_accessible_for_non_chambers(page: Page) -> None:
    # Navigate to the add barrister page for a legal services provider
    page.goto(url_for("main.add_barrister_form", firm=1, _external=True))

    # Should get 404 error
    assert page.title() == "404 Not Found"


@pytest.mark.usefixtures("live_server")
def test_add_barrister_validation_errors(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    # Submit without filling form
    page.get_by_role("button", name="Submit").click()

    # Check validation error messages
    expect(page.locator("#main-content")).to_contain_text("Enter barrister name")
    expect(page.locator("#main-content")).to_contain_text("Select barrister level")
    expect(page.locator("#main-content")).to_contain_text("Enter Bar Council roll number")


@pytest.mark.usefixtures("live_server")
def test_add_barrister_successful_submission(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    chambers_url = page.url
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    # Fill out the form
    page.get_by_label("Barrister name").fill("John Smith")
    page.get_by_role("radio", name="Junior counsel").click()
    page.get_by_label("Bar Council roll number").fill("12345")

    page.get_by_role("button", name="Submit").click()

    # Should redirect back to chambers provider page
    expect(page).to_have_url(chambers_url)
    # Check for success flash message
    expect(page.locator("#main-content")).to_contain_text("New barrister successfully created")


@pytest.mark.usefixtures("live_server")
def test_add_advocate_form_loads_from_chambers(page: Page) -> None:
    # Navigate to a chambers provider and then to add advocate form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()  # This is a chambers
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Check form loads correctly
    expect(page.get_by_role("heading", name="Advocate details")).to_be_visible()
    expect(page.get_by_label("Advocate name")).to_be_visible()
    expect(page.get_by_label("Advocate level")).to_be_visible()
    expect(page.get_by_label("SRA roll number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_advocate_form_not_accessible_for_non_chambers(page: Page) -> None:
    # Navigate to an LSP provider
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS").click()  # This is an LSP

    # Get the firm ID from URL and try to access add advocate form
    firm_id = page.url.split("/provider/")[1]
    page.goto(f"/provider/{firm_id}/add-advocate")

    # Should get 404 error
    assert page.title() == "404 Not Found"


@pytest.mark.usefixtures("live_server")
def test_add_advocate_validation_errors(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Submit without filling form
    page.get_by_role("button", name="Submit").click()

    # Check validation error messages
    expect(page.locator("#main-content")).to_contain_text("Enter advocate name")
    expect(page.locator("#main-content")).to_contain_text("Select advocate level")
    expect(page.locator("#main-content")).to_contain_text("Enter SRA roll number")


@pytest.mark.usefixtures("live_server")
def test_add_advocate_successful_submission(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    chambers_url = page.url
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Fill out the form
    page.get_by_label("Advocate name").fill("Jane Doe")
    page.get_by_role("radio", name="Senior counsel").click()
    page.get_by_label("SRA roll number").fill("67890")

    page.get_by_role("button", name="Submit").click()

    # Should redirect back to chambers provider page
    expect(page).to_have_url(chambers_url)
    # Check for success flash message
    expect(page.locator("#main-content")).to_contain_text("New advocate successfully created")


@pytest.mark.usefixtures("live_server")
def test_add_barrister_field_validation_lengths(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    # Test maximum length validation
    long_name = "a" * 256  # Over 255 character limit
    long_roll_number = "1" * 16  # Over 15 character limit

    page.get_by_label("Barrister name").fill(long_name)
    page.get_by_label("Bar Council roll number").fill(long_roll_number)
    page.get_by_role("radio", name="Junior counsel").click()

    page.get_by_role("button", name="Submit").click()

    expect(page.locator("#main-content")).to_contain_text("Barrister name must be 255 characters or less")
    expect(page.locator("#main-content")).to_contain_text("Bar Council roll number must be 15 characters or less")


@pytest.mark.usefixtures("live_server")
def test_add_advocate_field_validation_lengths(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Test maximum length validation
    long_name = "a" * 256  # Over 255 character limit
    long_roll_number = "1" * 16  # Over 15 character limit

    page.get_by_label("Advocate name").fill(long_name)
    page.get_by_label("SRA roll number").fill(long_roll_number)
    page.get_by_role("radio", name="Junior counsel").click()

    page.get_by_role("button", name="Submit").click()

    expect(page.locator("#main-content")).to_contain_text("Advocate name must be 255 characters or less")
    expect(page.locator("#main-content")).to_contain_text("SRA roll number must be 15 characters or less")


@pytest.mark.usefixtures("live_server")
def test_add_barrister_button_links_correctly(page: Page) -> None:
    # Navigate to chambers barristers and advocates page
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()

    # Check that "Add a barrister" button links to correct URL pattern
    add_barrister_button = page.get_by_role("button", name="Add a barrister")
    expect(add_barrister_button).to_be_visible()

    add_barrister_button.click()
    expect(page.url).to_match(r".*/provider/\d+/add-barrister$")


@pytest.mark.usefixtures("live_server")
def test_add_advocate_button_links_correctly(page: Page) -> None:
    # Navigate to chambers barristers and advocates page
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()

    # Check that "Add an advocate" button links to correct URL pattern
    add_advocate_button = page.get_by_role("button", name="Add an advocate")
    expect(add_advocate_button).to_be_visible()

    add_advocate_button.click()
    expect(page.url).to_match(r".*/provider/\d+/add-advocate$")


@pytest.mark.usefixtures("live_server")
def test_barrister_office_and_contacts_copied_from_chambers(page: Page) -> None:
    # Navigate to chambers and get its address details
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    # Capture chambers address from the main page
    chambers_address = page.locator(".govuk-summary-list__value").filter(has_text="1 Skyscraper").text_content()
    chambers_phone = page.locator(".govuk-summary-list__value").filter(has_text="555101").text_content()

    # Go to contacts tab to see contact details
    page.get_by_role("link", name="Contact").click()
    chambers_contact_name = page.locator(".govuk-summary-list__value").filter(has_text="Alice Johnson").text_content()
    chambers_contact_email = (
        page.locator(".govuk-summary-list__value").filter(has_text="office1@provider1.uk").text_content()
    )

    # Navigate to add barrister form and create one
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    page.get_by_label("Barrister name").fill("Test Barrister")
    page.get_by_role("radio", name="Junior counsel").click()
    page.get_by_label("Bar Council roll number").fill("TEST123")
    page.get_by_role("button", name="Submit").click()

    # Find the newly created barrister and navigate to their page
    page.get_by_role("button", name="Search").click()
    page.get_by_role("textbox", name="Search").fill("Test Barrister")
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Test Barrister").click()

    # Verify the barrister has the same address as the chambers
    expect(page.locator(".govuk-summary-list__value")).to_contain_text(chambers_address)
    expect(page.locator(".govuk-summary-list__value")).to_contain_text(chambers_phone)

    # Check contacts were copied
    page.get_by_role("link", name="Contact").click()
    expect(page.locator(".govuk-summary-list__value")).to_contain_text(chambers_contact_name)
    expect(page.locator(".govuk-summary-list__value")).to_contain_text(chambers_contact_email)


@pytest.mark.usefixtures("live_server")
def test_advocate_office_and_contacts_copied_from_chambers(page: Page) -> None:
    # Navigate to chambers and get its address details
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    # Capture chambers address from the main page
    chambers_postcode = page.locator(".govuk-summary-list__value").filter(has_text="LE1 1AA").text_content()
    chambers_city = page.locator(".govuk-summary-list__value").filter(has_text="Leicester").text_content()

    # Go to contacts tab to see contact details
    page.get_by_role("link", name="Contact").click()
    chambers_contact_phone = page.locator(".govuk-summary-list__value").filter(has_text="01162555101").text_content()

    # Navigate to add advocate form and create one
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    page.get_by_label("Advocate name").fill("Test Advocate")
    page.get_by_role("radio", name="Senior counsel").click()
    page.get_by_label("SRA roll number").fill("TEST456")
    page.get_by_role("button", name="Submit").click()

    # Find the newly created advocate and navigate to their page
    page.get_by_role("button", name="Search").click()
    page.get_by_role("textbox", name="Search").fill("Test Advocate")
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Test Advocate").click()

    # Verify the advocate has the same address details as the chambers
    expect(page.locator(".govuk-summary-list__value")).to_contain_text(chambers_postcode)
    expect(page.locator(".govuk-summary-list__value")).to_contain_text(chambers_city)

    # Check contacts were copied
    page.get_by_role("link", name="Contact").click()
    expect(page.locator(".govuk-summary-list__value")).to_contain_text(chambers_contact_phone)


@pytest.mark.usefixtures("live_server")
def test_barrister_has_separate_office_ids_from_chambers(page: Page) -> None:
    # Navigate to chambers
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()

    # Get chambers office code
    chambers_office_code = page.locator(".govuk-summary-list__value").filter(has_text="5A001L").text_content()

    # Create a barrister
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    page.get_by_label("Barrister name").fill("Separate Office Test")
    page.get_by_role("radio", name="Junior counsel").click()
    page.get_by_label("Bar Council roll number").fill("SEP123")
    page.get_by_role("button", name="Submit").click()

    # Navigate to the barrister
    page.get_by_role("button", name="Search").click()
    page.get_by_role("textbox", name="Search").fill("Separate Office Test")
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="Separate Office Test").click()

    # Verify barrister has different office code (should not match chambers)
    expect(page.locator(".govuk-summary-list__value")).not_to_contain_text(chambers_office_code)


@pytest.mark.usefixtures("live_server")
def test_barrister_form_displays_chambers_name_as_caption(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    # Check that the chambers name appears as a caption in the form
    expect(page.locator(".govuk-caption-xl")).to_contain_text("JOHNSON LEGAL SERVICES")


@pytest.mark.usefixtures("live_server")
def test_advocate_form_displays_chambers_name_as_caption(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Check that the chambers name appears as a caption in the form
    expect(page.locator(".govuk-caption-xl")).to_contain_text("JOHNSON LEGAL SERVICES")
