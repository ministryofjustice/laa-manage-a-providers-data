from flask import Flask, session
from flask_session import Session
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from govuk_frontend_wtf.main import WTFormsHelpers
from jinja2 import ChoiceLoader, PackageLoader, PrefixLoader
import sentry_sdk
from app.config import Config
from identity.flask import Auth as BaseAuth
from app.config.authentication import AuthenticationConfig


from typing import List, Optional  # Needed in Python 3.7 & 3.8
from flask import Flask, render_template, url_for


class Auth(BaseAuth):
    def login(
        self,
        *,
        next_link: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None,
    ) -> str:
        config_error = self._get_configuration_error()
        if config_error:
            return self._render_auth_error(
                error="configuration_error", error_description=config_error)
        assert self._auth, "_auth should have been initialized"  # And mypy needs this
        log_in_result: dict = self._auth.log_in(
            scopes=scopes,  # Have user consent to scopes (if any) during log-in
            redirect_uri=self._redirect_uri,
            prompt="select_account",  # Optional. More values defined in  https://openid.net/specs/openid-connect-core-1_0.html#AuthRequest
            next_link=next_link,
            state=state,
            )
        if "error" in log_in_result:
            return self._render_auth_error(
                error=log_in_result["error"],
                error_description=log_in_result.get("error_description"),
                )
        return render_template("identity/login.html", **dict(
            log_in_result,
            reset_password_url=self._get_reset_password_url(),
            auth_response_url=url_for(f"{self._endpoint_prefix}.auth_response"),
            ))

    def auth_response(self):
        result = self._auth.complete_log_in(request.args)
        if "error" in result:
            return self._render_auth_error(
                error=result["error"],
                error_description=result.get("error_description"),
                )
        return redirect(result.get("next_link") or "/")
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
    Session(app)

    #talisman.init_app(
    #    app,
    #    content_security_policy=csp if not Config.TESTING else None,
    #    permissions_policy=permissions_policy,
    #    content_security_policy_nonce_in=["script-src", "style-src"],
    #    force_https=True,
    #)

    # Initialize auth with the Flask app
    auth.init_app(app)

    # Store auth instance for access in decorators
    app.extensions["auth"] = auth

    WTFormsHelpers(app)

    # Register custom template filters
    from app.filters import register_template_filters

    register_template_filters(app)

    # Register blueprints
    from app.main import bp as main_bp
    from app.example_form import bp as example_form_bp
    from app.auth_routes import bp as auth_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(example_form_bp)
    app.register_blueprint(auth_bp)

    return app
