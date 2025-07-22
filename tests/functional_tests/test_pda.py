import pytest
from flask import url_for
from playwright.sync_api import Page, expect


@pytest.mark.usefixtures("live_server")
def test_providers(page: Page):
    page.goto(url_for("main.providers", _external=True))
    expect(page.get_by_role("link", name="Test Firm 1")).to_be_visible()
    expect(page.get_by_role("link", name="Test Firm 2")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_offices(page: Page):
    test_providers(page)
    test_firm_1 = page.get_by_role("link", name="Test Firm 1")
    test_firm_1.click()
    expect(page.get_by_role("link", name="TEST001")).to_be_visible()
    expect(page.get_by_role("cell", name="Test Office 1")).to_be_visible()
    expect(page.get_by_role("link", name="TEST002")).to_be_visible()
    expect(page.get_by_role("cell", name="Test Office 2")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_contracts(page: Page):
    test_offices(page)
    page.get_by_role("link", name="TEST001").click()
    expect(page.get_by_text("TEST001")).to_be_visible()
    expect(page.get_by_role("heading", name="Test Office 1")).to_be_visible()
    expect(page.get_by_role("cell", name="Family")).to_be_visible()


@pytest.mark.usefixtures("live_server")
def test_schedules(page: Page):
    test_contracts(page)
    page.get_by_role("link", name="Schedules").click()
    expect(page.get_by_role("cell", name="2022 Civil Contract")).to_be_visible()


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
