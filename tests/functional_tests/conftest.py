import pytest
from flask import url_for

from app import create_app
from app.config import Config


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
    SERVER_NAME = "localhost"
    RATELIMIT_ENABLED = False
    SECRET_KEY = "TEST_KEY"


@pytest.fixture(scope="session")
def app(config=TestConfig):
    return create_app(config)


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="function", autouse=True)
def startup(app, page):
    page.goto(url_for("main.index", _external=True))
