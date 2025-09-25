import sentry_sdk
from flask import render_template, request

from app.main import bp


@bp.app_errorhandler(404)
def not_found_error(error):
    sentry_sdk.capture_message(f"404 not found - {request.path}")
    return render_template("errors/404.html"), 404


@bp.app_errorhandler(500)
def internal_error(error):
    return render_template("errors/500.html"), 500
