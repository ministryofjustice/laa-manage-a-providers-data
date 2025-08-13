import os


class AuthenticationConfig:
    """Configuration class for Entra ID authentication settings."""

    # Used when SKIP_AUTH is True
    TEST_USER = {
        "name": "Test User",
        "email": "test.user@justice.gov.uk",
    }
    CLIENT_ID = os.getenv("ENTRA_ID_CLIENT_ID")
    CLIENT_SECRET_THUMBPRINT = os.environ.get("ENTRA_ID_CLIENT_SECRET_THUMBPRINT")
    if CLIENT_SECRET_THUMBPRINT:
        CLIENT_SECRET = {
            "private_key": os.getenv("ENTRA_ID_CLIENT_SECRET"),
            "thumbprint": CLIENT_SECRET_THUMBPRINT,
        }
    else:
        CLIENT_SECRET = os.environ.get("ENTRA_ID_CLIENT_SECRET")
    AUTHORITY = os.getenv("ENTRA_ID_AUTHORITY")
    REDIRECT_URI = os.getenv("ENTRA_ID_REDIRECT_URI")
