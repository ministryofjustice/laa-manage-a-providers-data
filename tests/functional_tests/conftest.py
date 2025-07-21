from unittest.mock import MagicMock, patch

import pytest

from app import Config, create_app


@pytest.fixture(scope="session")
def mock_provider_data_api():
    """Create a mock ProviderDataApi with predefined responses"""
    mock_api = MagicMock()

    # All your mock setup here...
    mock_api.get_provider_firm.return_value = {"id": 1, "name": "Test Firm", "status": "active"}

    mock_api.get_all_provider_firms.return_value = [{"id": 1, "name": "Test Firm 1"}, {"id": 2, "name": "Test Firm 2"}]

    mock_api.get_provider_office.return_value = {"code": "TEST001", "name": "Test Office", "address": "123 Test St"}

    mock_api.get_provider_offices.return_value = [
        {"code": "TEST001", "name": "Test Office 1"},
        {"code": "TEST002", "name": "Test Office 2"},
    ]

    mock_api.get_provider_users.return_value = [{"id": 1, "name": "Test User", "email": "test@example.com"}]

    mock_api.get_office_contract_details.return_value = {"contract_id": "C123", "status": "active"}

    mock_api.get_office_schedule_details.return_value = {"schedule_id": "S123", "working_hours": "9-5"}

    mock_api.get_office_bank_details.return_value = {"account_number": "*****1234", "bank_name": "Test Bank"}

    # Mock the status and init_app methods
    mock_api.status.return_value = None
    mock_api.init_app.return_value = None
    mock_api.base_url = "http://mock-api.test"

    return mock_api


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


@pytest.fixture(scope="session")
def app(mock_provider_data_api, config=TestConfig):
    patch("app.,dlfldpd", side_effect=mock_provider_data_api, return_value=mock_provider_data_api)

    app = create_app(config, mock_provider_data_api)

    # Replace the real API instance with our mock after app creation
    app.extensions["pda"] = mock_provider_data_api

    return app


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
