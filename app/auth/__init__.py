from app.auth.auth import Auth
from app.config.authentication import AuthenticationConfig

authentication = Auth(
    app=None,
    authority=AuthenticationConfig.AUTHORITY,
    client_id=AuthenticationConfig.CLIENT_ID,
    client_credential=AuthenticationConfig.CLIENT_SECRET,
    redirect_uri=AuthenticationConfig.REDIRECT_URI,
)
