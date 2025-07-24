import pytest
from flask import url_for

from app import create_app
from tests.config import TestConfig


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": {
            "width": 1920,
            "height": 1080,
        },
    }


@pytest.fixture(scope="session")
def app():
    from app.config.authentication import AuthenticationConfig
    AuthenticationConfig.SKIP_AUTH = True
    app = create_app(TestConfig)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture(scope="function", autouse=True)
def startup(app, page):
    page.goto(url_for("main.index", _external=True))
