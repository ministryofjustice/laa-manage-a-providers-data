import os


class AuthenticationConfig:
    """Configuration class for Entra ID authentication settings."""
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    AUTHORITY = os.getenv("AUTHORITY")
    REDIRECT_URI = os.getenv("REDIRECT_URI")
