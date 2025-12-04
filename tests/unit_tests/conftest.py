import pytest

from tests.conftest import MockProviderDataApi, TestConfig, create_app


# Use scope=function instead of scope=session as this ensures every tests get a fresh copy of the app
# This is slower than session scoped but gives predictability
@pytest.fixture(scope="function")
def app(config=TestConfig):
    print("tests/unit_tests/conftest", config, getattr(config, "PDA_FIXTURE_SET", "No fixture set specified"))
    app = create_app(config, MockProviderDataApi)
    with app.app_context():
        yield app
