from functools import wraps

import sentry_sdk
from flask import Flask, session, url_for
from flask_session import Session
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from govuk_frontend_wtf.main import WTFormsHelpers
from identity.flask import Auth as BaseAuth
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
from sentry_sdk.integrations.flask import FlaskIntegration

from app.config import Config
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
        scheme = "https" if Config.ENVIRONMENT.lower() != "local" else "http"
        url = url_for("main.index", _external=True, _scheme=scheme)
        return self.__class__._redirect(self._auth.log_out(url))


# Create auth instance that can be imported
auth = Auth(
    app=None,
    authority=AuthenticationConfig.AUTHORITY,
    client_id=AuthenticationConfig.CLIENT_ID,
    client_credential=AuthenticationConfig.CLIENT_SECRET,
    redirect_uri=AuthenticationConfig.REDIRECT_URI,
)


csrf = CSRFProtect()
talisman = Talisman()

if Config.SENTRY_DSN:
    sentry_sdk.init(
        integrations=[FlaskIntegration(transaction_style="url")],
        dsn=Config.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=Config.SENTRY_TRACES_SAMPLE_RATE,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=Config.SENTRY_PROFILES_SAMPLE_RATE,
        # This can either be dev, uat, staging, or production.
        # It is set by MAPD_ENVIRONMENT in the helm charts.
        environment=Config.ENVIRONMENT,
    )


def create_app(config_class=Config):
    app: Flask = Flask(__name__, static_url_path="/assets", static_folder="static/dist")
    app.url_map.strict_slashes = False  # This allows www.host.gov.uk/category to be routed to www.host.gov.uk/category/
    app.config.from_object(config_class)
    app.jinja_env.lstrip_blocks = True
    app.jinja_env.trim_blocks = True
    app.jinja_loader = ChoiceLoader(
        [
            PackageLoader("app"),
            PrefixLoader(
                {
                    "govuk_frontend_jinja": PackageLoader("govuk_frontend_jinja"),
                    "govuk_frontend_wtf": PackageLoader("govuk_frontend_wtf"),
                }
            ),
        ]
    )

    # Set content security policy
    csp = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
        ],
        "style-src": ["'self'"],
        "connect-src": [
            "'self'",
        ],
        "img-src": [
            "'self'",
            "www.gov.uk",
        ],
    }

    # Set permissions policy
    permissions_policy = {
        "accelerometer": "()",
        "autoplay": "()",
        "camera": "()",
        "cross-origin-isolated": "()",
        "display-capture": "()",
        "encrypted-media": "()",
        "fullscreen": "()",
        "geolocation": "()",
        "gyroscope": "()",
        "keyboard-map": "()",
        "magnetometer": "()",
        "microphone": "()",
        "midi": "()",
        "payment": "()",
        "picture-in-picture": "()",
        "publickey-credentials-get": "()",
        "screen-wake-lock": "()",
        "sync-xhr": "()",
        "usb": "()",
        "xr-spatial-tracking": "()",
        "clipboard-read": "()",
        "clipboard-write": "()",
        "gamepad": "()",
        "hid": "()",
        "idle-detection": "()",
        "unload": "()",
        "window-management": "()",
    }

    # Initialise app extensions
    csrf.init_app(app)

    talisman.init_app(
        app,
        content_security_policy=csp if not Config.TESTING else None,
        permissions_policy=permissions_policy,
        content_security_policy_nonce_in=["script-src", "style-src"],
        force_https=False,
        session_cookie_secure=Config.SESSION_COOKIE_SECURE,
        session_cookie_http_only=Config.SESSION_COOKIE_HTTP_ONLY,
        session_cookie_samesite=Config.SESSION_COOKIE_SAMESITE,
    )

    # Initialize auth with the Flask app
    auth.init_app(app)

    # Store auth instance for access
    app.extensions["auth"] = auth

    WTFormsHelpers(app)

    Session(app)

    # Register custom template filters
    from app.filters import register_template_filters

    register_template_filters(app)

    # Register blueprints
    from app.auth_routes import bp as auth_bp
    from app.example_form import bp as example_form_bp
    from app.main import bp as main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(example_form_bp)

    return app
