import pytest
from cachelib import SimpleCache

from app import Config, create_app
from app.pda.mock_api import MockProviderDataApi


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
    SECRET_KEY = "TEST_KEY"
    PDA_URL = "http://mock-api.test"
    PDA_API_KEY = "test-key"
    SERVER_NAME = "localhost"
    PREFERRED_URL_SCHEME = "http"
    SKIP_AUTH = True
    # Use in-memory cache for testing sessions
    SESSION_TYPE = "cachelib"
    SESSION_CACHELIB = SimpleCache()
    RATELIMIT_ENABLED = False
    # Use memory storage for rate limiting in tests
    RATELIMIT_STORAGE_URI = "memory://"
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope="session")
def app(config=TestConfig):
    app = create_app(config, MockProviderDataApi)
    with app.app_context():
        yield app
