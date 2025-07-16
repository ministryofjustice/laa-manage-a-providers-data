import pytest
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_header(page: Page):
    header = page.get_by_role("banner")

    expect(header).to_be_visible()
    expect(header).to_have_class("moj-header")
    expect(header).to_have_css("background-color", "rgb(11, 12, 12)")

    organisation_name = header.get_by_text("Legal Aid Agency")
    expect(organisation_name).to_have_attribute("href", "https://www.gov.uk/government/organisations/legal-aid-agency")

    moj_crest = header.locator("svg.moj-header__logotype-crest")
    expect(moj_crest).to_be_visible()

@pytest.mark.usefixtures("live_server")
def test_service_navigation(page: Page):
    service_navigation = page.get_by_role("region", name="Service information")

    expect(service_navigation).to_be_visible()

    service_name = service_navigation.get_by_text("Manage a provider's data")
    expect(service_name).to_have_attribute("href", "/")
