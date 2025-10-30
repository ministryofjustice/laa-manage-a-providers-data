import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_add_advocate_form_loads_from_chambers(page: Page) -> None:
    # Navigate to a chambers provider and then to add advocate form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()  # This is a chambers
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Check form loads correctly...
    expect(page.get_by_role("heading", name="Advocate details")).to_be_visible()
    expect(page.get_by_text("Advocate name")).to_be_visible()
    expect(page.get_by_text("Advocate level")).to_be_visible()
    expect(page.get_by_text("Solicitors Regulation Authority roll number")).to_be_visible()
    # ...with the expected levels.
    expect(page.get_by_role("radio", name="Junior")).to_be_visible()
    expect(page.get_by_role("radio", name="King's Counsel (KC,")).to_be_visible()
    expect(page.get_by_role("radio", name="None of the above")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_advocate_validation_errors(page: Page) -> None:
    # Navigate to chambers and add advocate form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="Add another advocate").click()

    # Submit without filling form
    page.get_by_role("button", name="Continue").click()

    # Check validation error messages
    expect(page.locator("#main-content")).to_contain_text("Enter the advocate name")
    expect(page.locator("#main-content")).to_contain_text("Select the advocate level")
    expect(page.locator("#main-content")).to_contain_text("Enter the Solicitors Regulation Authority roll number")


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

    page.get_by_role("button", name="Continue").click()

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

    page.get_by_role("button", name="Continue").click()

    expect(page.locator("#main-content")).to_contain_text("Advocate name must be 255 characters or less")
    expect(page.locator("#main-content")).to_contain_text(
        "Solicitors Regulation Authority roll number must be 15 characters or less"
    )


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


def _test_add_advocate_steps(page: Page) -> None:
    # Navigate to chambers and add barrister form
    page.get_by_role("button", name="Sign in").click()
    page.get_by_role("button", name="Search").click()
    page.get_by_role("link", name="JOHNSON LEGAL SERVICES").click()
    page.get_by_role("link", name="Barristers and advocates").click()
    page.get_by_role("button", name="dd another advocate").click()

    # Fill out the form
    page.get_by_label("Advocate name").fill("Jane Doe")
    page.get_by_role("radio", name="King's Counsel").click()
    page.get_by_label("Solicitors Regulation Authority roll number").fill("67890")
    page.get_by_role("button", name="Continue").click()

    # Should be taken to the page that gives the user a choice whether to use the same liaison manager as the chambers
    check_url = url_for("main.add_advocate_check_form", firm=2, _external=True)
    expect(page).to_have_url(check_url)
    expect(page.get_by_text("Robert MacLeod")).to_be_visible()
    expect(page.get_by_text("0131 222 3344")).to_be_visible()
    expect(page.get_by_text("robert.macleod@scottishlegal.com")).to_be_visible()
    expect(
        page.locator("legend", has_text="Do you want to use the same liaison manager as the chambers?")
    ).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_advocate_same_liaison_manager(page: Page) -> None:
    _test_add_advocate_steps(page)

    # Keep the same liaison manager as the chambers
    expect(page.get_by_role("radio", name="Yes")).to_be_visible()
    page.get_by_role("radio", name="Yes").check()
    page.get_by_role("button", name="Continue").click()

    # New Advocate should be created with same liaison manager as the chambers
    expect(page.locator("#main-content")).to_contain_text("New advocate successfully created")
    expect(page.get_by_role("heading", name="Jane Doe")).to_be_visible()
    page.get_by_role("heading", name="Robert MacLeod").scroll_into_view_if_needed()
    expect(page.get_by_text("0131 222 3344")).to_be_visible()
    expect(page.get_by_text("robert.macleod@scottishlegal.com")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_add_advocate_different_liaison_manager(page: Page) -> None:
    _test_add_advocate_steps(page)
    # Change the liaison manager
    expect(page.get_by_role("radio", name="No")).to_be_visible()
    page.get_by_role("radio", name="No").check()
    page.get_by_role("button", name="Continue").click()

    # The add liaison manager form should be shown now
    expect(page).to_have_url(url_for("main.add_advocate_liaison_manager_form", firm=2, _external=True))
    expect(page.get_by_text("Jane Doe")).to_be_visible()
    expect(page.get_by_role("Heading", name="Add liaison manager")).to_be_visible()
    page.get_by_role("textbox", name="First name").fill("Functional")
    page.get_by_role("textbox", name="Last name").fill("Tester")
    page.get_by_role("textbox", name="Email address").fill("functional.tester@justice.gov.uk")
    page.get_by_role("textbox", name="Telephone number").fill("0203 123 4567")
    page.get_by_role("textbox", name="Website (optional)").fill("http://gov.uk/advocates/functional-tester")
    page.get_by_role("button", name="Continue").click()

    # New barrister should be created with same liaison manager as the chambers
    expect(page.locator("#main-content")).to_contain_text("New advocate successfully created")
    expect(page.locator("#main-content")).to_contain_text("Functional Tester is the new liaison manager")
    expect(page.get_by_role("heading", name="Jane Doe")).to_be_visible()
    page.get_by_role("heading", name="Functional Tester").scroll_into_view_if_needed()
    expect(page.get_by_text("0203 123 4567")).to_be_visible()
    expect(page.get_by_text("functional.tester@justice.gov.uk")).to_be_visible()
    expect(page.get_by_text("http://gov.uk/advocates/functional-tester")).to_be_visible()
