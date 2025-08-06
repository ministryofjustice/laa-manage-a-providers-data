from functools import wraps

from flask import current_app, session, url_for
from identity.flask import Auth as BaseAuth

from app.config.authentication import AuthenticationConfig


class Auth(BaseAuth):
    def __init__(self, *args, **kwargs):
        self.skip_auth = False
        super(Auth, self).__init__(*args, **kwargs)

    def login_required(self, function=None, *args, **kwargs):
        @wraps(function)
        def wrapper(*func_args, **func_kwargs):
            if current_app.config.get("SKIP_AUTH", False):
                return function(*func_args, context={"user": AuthenticationConfig.TEST_USER}, **func_kwargs)
            else:
                base_decorated = super(Auth, self).login_required(function, *args, **kwargs)
                return base_decorated(*func_args, **func_kwargs)

        return wrapper

    def logout(self):
        session.clear()
        url = url_for("main.index", _external=True)
        return self.__class__._redirect(self._auth.log_out(url))
