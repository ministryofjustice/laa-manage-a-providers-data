import pytest

from app import Config, create_app
from tests.fixture.pda import mock_provider_data_api


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
    PDA_URL = "http://mock-api.test"
    PDA_API_KEY = "test-key"
    # Ensure these are not set to avoid conflicts
    SERVER_NAME = "localhost"
    PREFERRED_URL_SCHEME = "http"
    SKIP_AUTH = True


@pytest.fixture(scope="session")
def app(config=TestConfig):
    app = create_app(config, mock_provider_data_api)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
