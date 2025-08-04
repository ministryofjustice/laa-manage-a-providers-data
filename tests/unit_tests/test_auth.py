from unittest.mock import MagicMock, patch

from app.auth import Auth
from app.config.authentication import AuthenticationConfig


def test_skip_auth(monkeypatch):
    monkeypatch.setattr("app.config.authentication.AuthenticationConfig.SKIP_AUTH", True)
    auth = Auth(app=None, client_id=None)

    mock_view = MagicMock()
    with patch.object(Auth.__base__, "login_required", autospec=True) as super_login_required:
        decorated = auth.login_required(mock_view)
        decorated()
        super_login_required.assert_not_called()
        mock_view.assert_called_with(context={"user": AuthenticationConfig.TEST_USER})


def test_not_skipping_auth(monkeypatch):
    monkeypatch.setattr("app.config.authentication.AuthenticationConfig.SKIP_AUTH", False)
    auth = Auth(app=None, client_id=None)

    mock_view = MagicMock()
    with patch.object(Auth.__base__, "login_required", autospec=True) as super_login_required:
        decorated = auth.login_required(mock_view)
        decorated()
        super_login_required.assert_called()
