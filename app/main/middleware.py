import sentry_sdk
from flask import request, session

from app.main import bp


@bp.after_app_request
def add_noindex_header(response):
    """Add a noindex header to all responses, to disallow search engines from indexing the page."""
    response.headers["X-Robots-Tag"] = "noindex"
    return response


@bp.after_app_request
def add_no_cache_headers(response):
    """Prevents the webbrowser from caching webpages"""
    if not request.path.startswith("/assets"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    else:
        response.headers["Cache-Control"] = "public, max-age=1800"  # Max age of 30 minutes
        response.headers["Pragma"] = "cache"

    return response


@bp.app_context_processor
def user_context_processor():
    if current_user := session.get("_logged_in_user"):
        current_user = {
            "name": current_user["name"],
            "email": current_user["preferred_username"],
        }
    return dict(current_user=current_user)


@bp.before_app_request
def set_sentry_user():
    if current_user := session.get("_logged_in_user"):
        sentry_sdk.set_user(
            {
                "name": current_user["name"],
                "email": current_user.get("preferred_username"),
            }
        )
    else:
        sentry_sdk.set_user(None)
