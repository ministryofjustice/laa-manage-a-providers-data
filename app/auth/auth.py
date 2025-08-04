from functools import wraps

from flask import current_app, session, url_for
from identity.flask import Auth as BaseAuth

from app.config.authentication import AuthenticationConfig


class Auth(BaseAuth):
    def login_required(self, function=None, *args, **kwargs):
        if AuthenticationConfig.SKIP_AUTH:

            @wraps(function)
            def wrapper(*args, **kwargs):
                return function(*args, context={"user": AuthenticationConfig.TEST_USER}, **kwargs)

            return wrapper
        else:
            return super().login_required(function, *args, **kwargs)

    def logout(self):
        session.clear()
        scheme = "http" if current_app.config["ENVIRONMENT"] == "local" else "https"
        url = url_for("main.index", _external=True, _scheme=scheme)
        return self.__class__._redirect(self._auth.log_out(url))
