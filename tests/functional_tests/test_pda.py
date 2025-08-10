import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_providers(page: Page):
    page.goto(url_for("main.providers", _external=True))
    expect(page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS")).to_be_visible()
    expect(page.get_by_role("link", name="JOHNSON LEGAL SERVICES")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_offices(page: Page):
    test_providers(page)
    test_firm_1 = page.get_by_role("link", name="SMITH & PARTNERS SOLICITORS")
    test_firm_1.click()
    expect(page.get_by_role("link", name="1A001L", exact=True)).to_be_visible()
    expect(page.get_by_role("cell", name="1A001L,1 Skyscraper")).to_be_visible()
    expect(page.get_by_role("link", name="1A002L", exact=True)).to_be_visible()
    expect(page.get_by_role("cell", name="1A002L,2 High Street")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_contracts(page: Page):
    test_offices(page)
    page.get_by_role("link", name="1A001L").click()
    expect(page.get_by_text("1A001L", exact=True)).to_be_visible()
    expect(page.get_by_role("heading", name="1A001L,1 Skyscraper")).to_be_visible()
    expect(page.get_by_role("cell", name="MAT")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_schedules(page: Page):
    test_contracts(page)
    page.get_by_role("link", name="Schedules").click()
    expect(page.get_by_role("cell", name="2024 Standard Civil Contract")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_bank_details(page: Page):
    test_contracts(page)
    page.get_by_role("link", name="Bank Details").click()
    expect(
        page.get_by_text(
            "Warning We do not currently have permission to read provider's bank details, the below is just example data."
        )
    ).to_be_visible()
    expect(page.get_by_role("cell", name="Example Bank")).to_be_visible()
    expect(page.get_by_role("cell", name="-34-56")).to_be_visible()
    expect(page.get_by_role("cell", name="12345678")).to_be_visible()
