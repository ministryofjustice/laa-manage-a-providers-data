from unittest.mock import MagicMock, patch

from app import auth
from tests.conftest import TestConfig

config = TestConfig


def test_skip_auth(app):
    app.config["SKIP_AUTH"] = True

    mock_view = MagicMock()
    with patch.object(auth.__class__.__base__, "login_required", autospec=True) as super_login_required:
        super_login_required.return_value = lambda *args, **kwargs: mock_view(*args, **kwargs)
        with app.app_context():
            decorated = auth.login_required(mock_view)
            decorated()
            super_login_required.assert_not_called()
            # The original view should be called with test user context when skipping auth
            mock_view.assert_called_once_with(
                context={"user": {"name": "Test User", "email": "test.user@justice.gov.uk"}}
            )


def test_not_skipping_auth(app):
    app.config["SKIP_AUTH"] = False

    mock_view = MagicMock()
    with patch.object(auth.__class__.__base__, "login_required", autospec=True) as super_login_required:
        super_login_required.return_value = lambda *args, **kwargs: mock_view(*args, **kwargs)

        with app.app_context():
            decorated = auth.login_required(mock_view)
            decorated()
            super_login_required.assert_called()
