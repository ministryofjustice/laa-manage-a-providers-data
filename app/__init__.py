import sentry_sdk
from flask import Flask
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader

from app.config import Config
from app.pda.api import ProviderDataApi

csrf = CSRFProtect()
talisman = Talisman()
provider_data_api = ProviderDataApi()

if Config.SENTRY_DSN:
    sentry_sdk.init(
        dsn=Config.SENTRY_DSN,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=0.01,
        # Set profiles_sample_rate to 1.0 to profile 100%
        # of sampled transactions.
        # We recommend adjusting this value in production.
        profiles_sample_rate=0.2,
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

    app.logger.level = app.config["LOGGING_LEVEL"]

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
        session_cookie_secure=True,
        session_cookie_http_only=Config.SESSION_COOKIE_HTTP_ONLY,
        session_cookie_samesite="Strict",
    )

    provider_data_api.init_app(app, base_url=app.config["PDA_URL"], api_key=app.config["PDA_API_KEY"])

    WTFormsHelpers(app)

    # Register custom template filters
    from app.filters import register_template_filters

    register_template_filters(app)

    # Register blueprints
    from app.auth import bp as auth_bp
    from app.example_form import bp as example_form_bp
    from app.main import bp as main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(example_form_bp)
    app.register_blueprint(auth_bp)

    return app
