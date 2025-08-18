from datetime import datetime, timezone
from functools import wraps

import structlog
from flask import current_app, request, session, url_for
from identity.flask import Auth as BaseAuth

from app.config.authentication import AuthenticationConfig


class Auth(BaseAuth):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = structlog.get_logger("auth")

    def login_required(self, function=None, *args, **kwargs):
        @wraps(function)
        def wrapper(*func_args, **func_kwargs):
            if current_app.config.get("SKIP_AUTH", False):
                return function(*func_args, context={"user": AuthenticationConfig.TEST_USER}, **func_kwargs)
            else:
                base_decorated = super(Auth, self).login_required(function, *args, **kwargs)
                return base_decorated(*func_args, **func_kwargs)

        return wrapper

    def auth_response(self):
        """Log successful login"""
        redirect = super().auth_response()

        user_data = session.get("_logged_in_user")
        if user_data and user_data.get("oid"):
            session["login_timestamp"] = datetime.now(timezone.utc).isoformat()

            self.logger.info(
                "User logged in",
                user_id=user_data.get("oid"),
                ip_address=request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr),
                user_agent=request.headers.get("User-Agent", "Unknown")[:200],
            )

        return redirect

    def logout(self):
        """Log logout with session duration"""
        user_data = session.get("_logged_in_user")
        login_time_str = session.get("login_timestamp")

        if user_data and user_data.get("oid"):
            extra = {
                "user_id": user_data.get("oid"),
                "ip_address": request.environ.get("HTTP_X_FORWARDED_FOR", request.remote_addr),
                "user_agent": request.headers.get("User-Agent", "Unknown")[:200],
            }

            if login_time_str:
                try:
                    login_time = datetime.fromisoformat(login_time_str.replace("Z", "+00:00"))
                    duration_seconds = (datetime.now(timezone.utc) - login_time).total_seconds()
                    extra["session_duration_seconds"] = duration_seconds
                except (ValueError, TypeError):
                    pass

            self.logger.info("User logged out", **extra)

        session.clear()
        url_scheme = current_app.config.get("PREFERRED_URL_SCHEME", "https")
        url = url_for("main.index", _external=True, _scheme=url_scheme)
        return self.__class__._redirect(self._auth.log_out(url))
