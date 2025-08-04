from unittest.mock import MagicMock, patch

from app import auth
from tests.conftest import TestConfig

config = TestConfig


def test_skip_auth(app):
    auth.skip_auth = True

    mock_view = MagicMock()
    with patch.object(auth.__class__.__base__, "login_required", autospec=True) as super_login_required:
        decorated = auth.login_required(mock_view)
        decorated()
        super_login_required.assert_not_called()


def test_not_skipping_auth(app):
    auth.skip_auth = False

    mock_view = MagicMock()
    with patch.object(auth.__class__.__base__, "login_required", autospec=True) as super_login_required:
        decorated = auth.login_required(mock_view)
        decorated()
        super_login_required.assert_called()
