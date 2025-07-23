import os


class AuthenticationConfig:
    """Configuration class for Entra ID authentication settings."""
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET_THUMBPRINT = os.environ.get("CLIENT_SECRET_THUMBPRINT")
    if CLIENT_SECRET_THUMBPRINT:
        CLIENT_SECRET = {
            "private_key": os.getenv("CLIENT_SECRET"),
            "thumbprint": CLIENT_SECRET_THUMBPRINT,
        }
    else:
        CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    AUTHORITY = os.getenv("AUTHORITY")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
