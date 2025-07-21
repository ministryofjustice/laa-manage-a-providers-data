import pytest

from app import Config

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"
    # Provide valid config to avoid API initialization errors
    PDA_BASE_URL = "http://mock-api.test"
    PDA_API_KEY = "test-key"
    # Ensure these are not set to avoid conflicts
    SERVER_NAME = None


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="function", autouse=True)
def startup(live_server, page):
    """Navigate to the live server's index page"""
    # Debug the live server
    print(f"Live server: {live_server}")
    print(f"Live server type: {type(live_server)}")

    # Get the URL - try different approaches
    if hasattr(live_server, "url") and callable(live_server.url):
        url = live_server.url()
    elif hasattr(live_server, "url") and not callable(live_server.url):
        url = live_server.url
    else:
        url = f"http://localhost:{getattr(live_server, 'port', 5000)}"

    print(f"Attempting to navigate to: {url}")

    if url and url != "None":
        page.goto(url)
    else:
        raise ValueError(f"Invalid live server URL: {url}")
