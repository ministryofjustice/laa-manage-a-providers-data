import pytest

from app import Config, create_app
from tests.fixture.pda import mock_provider_data_api


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"
    PDA_URL = "http://mock-api.test"
    PDA_API_KEY = "test-key"
    # Ensure these are not set to avoid conflicts
    SERVER_NAME = "localhost"

 
def app(config=TestConfig):
    app = create_app(config, mock_provider_data_api
                    
    # Replace the real API instance with our mock after app creation
    app.extensions["pda"] = mock_pda

    return app
