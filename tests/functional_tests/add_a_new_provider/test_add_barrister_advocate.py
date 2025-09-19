import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_add_barrister_form_loads_from_chambers(page: Page) -> None:
    # Navigate to a chambers provider and then to add barrister form
    page.get_by_role("button", name="Sign in").click()
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
def test_add_advocate_form_not_accessible_for_non_chambers(page: Page) -> None:
    # Navigate to the add advocate page for a legal services provider
    page.goto(url_for("main.add_barrister_form", firm=1, _external=True))

    # Should get 404 error
    assert page.title() == "404 Not Found"


@pytest.mark.usefixtures("live_server")
def test_add_barrister_validation_errors(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    # Submit without filling form
    page.get_by_role("button", name="Submit").click()

    # Check validation error messages
    expect(page.locator("#main-content")).to_contain_text("Enter the barrister name")
    expect(page.locator("#main-content")).to_contain_text("Select the barrister level")
    expect(page.locator("#main-content")).to_contain_text("Enter the Bar Council roll number")


@pytest.mark.usefixtures("live_server")
def test_add_barrister_successful_submission(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    chambers_url = page.url
    page.get_by_role("button", name="Add another barrister").click()

    # Fill out the form
    page.get_by_label("Barrister name").fill("John Smith")
    page.get_by_role("radio", name="Junior").click()
    page.get_by_label("Bar Council roll number").fill("12345")

    page.get_by_role("button", name="Submit").click()

    # Should redirect back to chambers provider page
    expect(page).to_have_url(chambers_url)
    # Check for success flash message
    expect(page.locator("#main-content")).to_contain_text("New barrister successfully created")


@pytest.mark.usefixtures("live_server")
def test_add_advocate_form_loads_from_chambers(page: Page) -> None:
    # Navigate to a chambers provider and then to add advocate form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()  # This is a chambers
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Check form loads correctly
    expect(page.get_by_role("heading", name="Advocate details")).to_be_visible()
    expect(page.get_by_text("Advocate name")).to_be_visible()
    expect(page.get_by_text("Advocate level")).to_be_visible()
    expect(page.get_by_text("Solicitors Regulation Authority roll number")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_advocate_validation_errors(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Submit without filling form
    page.get_by_role("button", name="Submit").click()

    # Check validation error messages
    expect(page.locator("#main-content")).to_contain_text("Enter the advocate name")
    expect(page.locator("#main-content")).to_contain_text("Select the advocate level")
    expect(page.locator("#main-content")).to_contain_text("Enter the Solicitors Regulation Authority roll number")


@pytest.mark.usefixtures("live_server")
def test_add_advocate_successful_submission(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    chambers_url = page.url
    page.get_by_role("button", name="Add another advocate").click()

    # Fill out the form
    page.get_by_label("Advocate name").fill("Jane Doe")
    page.get_by_role("radio", name="King's Counsel").click()
    page.get_by_label("Solicitors Regulation Authority roll number").fill("67890")

    page.get_by_role("button", name="Submit").click()

    # Should redirect back to chambers provider page
    expect(page).to_have_url(chambers_url)
    # Check for success flash message
    expect(page.locator("#main-content")).to_contain_text("New advocate successfully created")


@pytest.mark.usefixtures("live_server")
def test_add_barrister_field_validation_lengths(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    # Test maximum length validation
    long_name = "a" * 256  # Over 255 character limit
    long_roll_number = "1" * 16  # Over 15 character limit

    page.get_by_label("Barrister name").fill(long_name)
    page.get_by_label("Bar Council roll number").fill(long_roll_number)
    page.get_by_role("radio", name="Junior").click()

    page.get_by_role("button", name="Submit").click()

    expect(page.locator("#main-content")).to_contain_text("Barrister name must be 255 characters or less")
    expect(page.locator("#main-content")).to_contain_text("Bar Council roll number must be 15 characters or less")


@pytest.mark.usefixtures("live_server")
def test_add_advocate_field_validation_lengths(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Test maximum length validation
    long_name = "a" * 256  # Over 255-character limit
    long_roll_number = "1" * 16  # Over 15-character limit

    page.get_by_label("Advocate name").fill(long_name)
    page.get_by_label("Solicitors Regulation Authority roll number").fill(long_roll_number)
    page.get_by_role("radio", name="Junior").click()

    page.get_by_role("button", name="Submit").click()

    expect(page.locator("#main-content")).to_contain_text("Advocate name must be 255 characters or less")
    expect(page.locator("#main-content")).to_contain_text(
        "Solicitors Regulation Authority roll number must be 15 characters or less"
    )


@pytest.mark.usefixtures("live_server")
def test_barrister_form_displays_chambers_name_as_caption(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another barrister").click()

    # Check that the chambers name appears as a caption in the form
    expect(page.locator(".govuk-caption-xl")).to_contain_text("JOHNSON LEGAL SERVICES")


@pytest.mark.usefixtures("live_server")
def test_advocate_form_displays_chambers_name_as_caption(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Check that the chambers name appears as a caption in the form
    expect(page.locator(".govuk-caption-xl")).to_contain_text("JOHNSON LEGAL SERVICES")
