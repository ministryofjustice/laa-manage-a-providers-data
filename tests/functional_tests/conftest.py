import pytest
from flask import url_for


@pytest.fixture(scope="function", autouse=True)
def startup(app, page):
    page.goto(url_for("main.index", _external=True))
