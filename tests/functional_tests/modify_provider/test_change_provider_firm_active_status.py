import pytest
from flask import url_for
from playwright.sync_api import Page


@pytest.mark.usefixtures("live_server")
def test_change_provider_firm_active_status(page: Page):
    page.goto(url_for("main.change_provider_active_status", firm=1, _external=True))
    # Provider is already inactive and should default to inactive
    page.wait_for_selector(selector="//input[@name='status' and @value='inactive' and @checked]")

    page.locator("//input[@name='status' and @value='active']").click()
    page.get_by_role("button", name="Save").click()

    success_message_element = page.locator(".govuk-notification-banner--success .govuk-notification-banner__content")
    assert success_message_element.text_content().strip() == "SMITH & PARTNERS SOLICITORS marked as active"
