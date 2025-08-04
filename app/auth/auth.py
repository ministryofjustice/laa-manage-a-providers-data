from functools import wraps

from flask import session, url_for
from identity.flask import Auth as BaseAuth

from app.config.authentication import AuthenticationConfig


class Auth(BaseAuth):
    def __init__(self, *args, **kwargs):
        self.skip_auth = False
        super(Auth, self).__init__(*args, **kwargs)

    def init_app(self, app):
        self.skip_auth = app.config.get("SKIP_AUTH", False)
        super(Auth, self).init_app(app)

    def login_required(self, function=None, *args, **kwargs):
        if self.skip_auth:

            @wraps(function)
            def wrapper(*args, **kwargs):
                return function(*args, context={"user": AuthenticationConfig.TEST_USER}, **kwargs)

            return wrapper
        else:
            return super().login_required(function, *args, **kwargs)

    def logout(self):
        session.clear()
        url = url_for("main.index", _external=True)
        return self.__class__._redirect(self._auth.log_out(url))
