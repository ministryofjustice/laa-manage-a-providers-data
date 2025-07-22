from unittest.mock import MagicMock

import pytest

from app import Config, create_app


@pytest.fixture(scope="session")
def mock_provider_data_api():
    """Create a mock ProviderDataApi with predefined responses"""
    mock_api = MagicMock()

    # All your mock setup here...
    mock_api.get_provider_firm.return_value = {"id": 1, "name": "Test Firm", "status": "active"}

    mock_api.get_all_provider_firms.return_value = {
        "firms": [{"id": 1, "name": "Test Firm 1"}, {"id": 2, "name": "Test Firm 2"}]
    }

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


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"
    # Provide valid config to avoid API initialization errors
    PDA_BASE_URL = "http://mock-api.test"
    PDA_API_KEY = "test-key"
    # Ensure these are not set to avoid conflicts
    SERVER_NAME = "localhost"


@pytest.fixture(scope="session")
def app(mock_provider_data_api, config=TestConfig):
    app = create_app(config)

    # Replace the real API instance with our mock after app creation
    app.extensions["pda"] = mock_provider_data_api

    return app
