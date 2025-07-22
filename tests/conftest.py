import pytest

from app import Config, create_app
from tests.fixture.pda import mock_provider_data_api


@pytest.fixture(scope="session", autouse=True)
def mock_pda():
    return mock_provider_data_api()


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
def app(mock_pda, config=TestConfig):
    app = create_app(config)

    # Replace the real API instance with our mock after app creation
    app.extensions["pda"] = mock_pda

    return app
