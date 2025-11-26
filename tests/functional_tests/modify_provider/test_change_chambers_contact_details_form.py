import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import definition_list_to_dict, navigate_to_provider_page


@pytest.mark.usefixtures("live_server")
def test_change_chambers_contact_details_address(page: Page) -> None:
    navigate_to_provider_page(page, provider_name="JOHNSON LEGAL SERVICES")
    contact_details = definition_list_to_dict(page, dl_selector=".chambers-contact-details")
    assert contact_details["Address"] == "1 Skyscraper,\n1 Some Road,\nLeicester,\nLE1 1AA"
    page.get_by_role("link", name="Change address").click()

    # Make sure form is prepopulated
    expect(page.get_by_role("textbox", name="Address line 1")).to_have_value("1 Skyscraper")
    expect(page.get_by_role("textbox", name="Address line 2 (optional)")).to_have_value("1 Some Road")
    expect(page.get_by_role("textbox", name="Address line 3 (optional)")).to_have_value("")
    expect(page.get_by_role("textbox", name="Address line 4 (optional)")).to_have_value("")
    expect(page.get_by_role("textbox", name="Town or city")).to_have_value("Leicester")
    expect(page.get_by_role("textbox", name="County (optional)")).to_have_value("Leicestershire")
    expect(page.get_by_role("textbox", name="Postcode")).to_have_value("LE1 1AA")

    # Change the values
    page.get_by_role("textbox", name="Address line 1").fill("Flat 783")
    page.get_by_role("textbox", name="Address line 2 (optional)").fill("Somerset House")
    page.get_by_role("textbox", name="Address line 3 (optional)").fill("Some Road")
    page.get_by_role("textbox", name="Address line 4 (optional)").fill("Westminster")
    page.get_by_role("textbox", name="Town or city").fill("London")
    page.get_by_role("textbox", name="County (optional)").fill("")
    page.get_by_role("textbox", name="Postcode").fill("SW1 1AA")
    page.get_by_role("button", name="Submit").click()

    page.get_by_text("Chambers contact details successfully updated")
    contact_details = definition_list_to_dict(page, dl_selector=".chambers-contact-details")
    assert contact_details["Address"] == "Flat 783,\nSomerset House,\nSome Road,\nWestminster,\nLondon,\nSW1 1AA"


@pytest.mark.usefixtures("live_server")
def test_change_chambers_contact_details_email_address(page: Page) -> None:
    navigate_to_provider_page(page, provider_name="JOHNSON LEGAL SERVICES")
    contact_details = definition_list_to_dict(page, dl_selector=".chambers-contact-details")
    assert contact_details["Email address"] == "office1@provider2.uk"
    page.get_by_role("link", name="Change email address").click()

    # Make sure form is prepopulated
    expect(page.get_by_role("textbox", name="Office email address (optional)")).to_have_value("office1@provider2.uk")

    # Change the values
    page.get_by_role("textbox", name="Office email address (optional)").fill("functional.tester@provider2.uk")
    page.get_by_role("button", name="Submit").click()

    page.get_by_text("Chambers contact details successfully updated")
    contact_details = definition_list_to_dict(page, dl_selector=".chambers-contact-details")
    assert contact_details["Email address"] == "functional.tester@provider2.uk"


@pytest.mark.usefixtures("live_server")
def test_change_chambers_contact_details_telephone_number(page: Page) -> None:
    navigate_to_provider_page(page, provider_name="JOHNSON LEGAL SERVICES")
    contact_details = definition_list_to_dict(page, dl_selector=".chambers-contact-details")
    assert contact_details["Telephone number"] == "555201"
    page.get_by_role("link", name="Change telephone number").click()

    # Make sure form is prepopulated
    expect(page.get_by_role("textbox", name="Telephone number (optional)")).to_have_value("555201")

    # Change the values
    page.get_by_role("textbox", name="Telephone number (optional)").fill("0000 111 2222")
    page.get_by_role("button", name="Submit").click()

    page.get_by_text("Chambers contact details successfully updated")
    contact_details = definition_list_to_dict(page, dl_selector=".chambers-contact-details")
    assert contact_details["Telephone number"] == "0000 111 2222"


@pytest.mark.usefixtures("live_server")
def test_change_chambers_contact_details_dx_number(page: Page) -> None:
    navigate_to_provider_page(page, provider_name="JOHNSON LEGAL SERVICES")

    page.get_by_role("link", name="Enter DX number").click()

    # Make sure form is prepopulated
    expect(page.get_by_role("textbox", name="DX number (optional)")).to_have_value("")

    # Change the values
    page.get_by_role("textbox", name="DX number (optional)").fill("111222333444555")
    page.get_by_role("button", name="Submit").click()

    page.get_by_text("Chambers contact details successfully updated")
    contact_details = definition_list_to_dict(page, dl_selector=".chambers-contact-details")
    assert contact_details["DX number"] == "111222333444555"


@pytest.mark.usefixtures("live_server")
def test_change_chambers_contact_details_dx_centre(page: Page) -> None:
    navigate_to_provider_page(page, provider_name="JOHNSON LEGAL SERVICES")

    page.get_by_role("link", name="Enter DX centre").click()

    # Make sure form is prepopulated
    expect(page.get_by_role("textbox", name="DX centre (optional)")).to_have_value("")

    # Change the values
    page.get_by_role("textbox", name="DX centre (optional)").fill("London")
    page.get_by_role("button", name="Submit").click()

    expect(page.get_by_text("Chambers contact details successfully updated")).to_be_visible()
    contact_details = definition_list_to_dict(page, dl_selector=".chambers-contact-details")
    assert contact_details["DX centre"] == "London"


@pytest.mark.usefixtures("live_server")
def test_change_chambers_contact_details_no_changes(page: Page) -> None:
    navigate_to_provider_page(page, provider_name="JOHNSON LEGAL SERVICES")
    provider_view_url = page.url
    page.get_by_role("link", name="Change address").click()
    page.get_by_role("button", name="Submit").click()

    expect(
        page.get_by_text("You have not changed anything. Cancel if you do not want to make a change.")
    ).to_be_visible()
    assert provider_view_url != page.url


@pytest.mark.usefixtures("live_server")
def test_change_chambers_contact_details_cancel(page: Page) -> None:
    navigate_to_provider_page(page, provider_name="JOHNSON LEGAL SERVICES")
    provider_view_url = page.url
    page.get_by_role("link", name="Change address").click()
    page.get_by_role("link", name="Cancel").click()

    expect(page.get_by_text("Chambers contact details successfully updated")).not_to_be_visible()
    assert provider_view_url == page.url
