import pytest
from playwright.sync_api import Page, expect


def test_debug_api_state(debug_live_server, app):
    """Debug test to check API state"""
    print(f"App extensions: {list(app.extensions.keys())}")

    if "pda" in app.extensions:
        api = app.extensions["pda"]
        print(f"API instance: {api}")
        print(f"API type: {type(api)}")
        print(f"API base_url: {getattr(api, 'base_url', 'MISSING')}")

        # Test a method call
        try:
            result = api.get_provider_firm(1)
            print(f"API method result: {result}")
        except Exception as e:
            print(f"API method error: {e}")
        assert False
    else:
        print("No 'pda' extension found!")


@pytest.mark.usefixtures("live_server")
def test_pda(page: Page):
    page.get_by_role("button", name="Start now").click()
    page.get_by_role("textbox", name="Your full name").fill("Alice")
    page.get_by_role("button", name="Continue").click()
    expect(page.get_by_text("Your name is Alice")).to_be_visible()
