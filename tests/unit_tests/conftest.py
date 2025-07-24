import pytest

from app import create_app
from tests.config import TestConfig


@pytest.fixture(scope="session")
def app():
    app = create_app(TestConfig)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()
