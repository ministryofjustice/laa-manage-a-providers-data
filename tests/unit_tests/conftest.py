import pytest
from app.config import Config
from app import create_app


class TestConfig(Config):
    TESTING = True
    DEBUG = True
    SERVER_NAME = "localhost"
    SECRET_KEY = "TEST_KEY"
    WTF_CSRF_ENABLED = False


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
