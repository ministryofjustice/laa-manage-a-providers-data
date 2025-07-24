import uuid

from flask import Blueprint, session, url_for
from app import auth

bp = Blueprint("auth", __name__)


@bp.app_context_processor
def user_context_processor():
    if current_user := session.get("_logged_in_user"):
        current_user = {
            "name": current_user["name"],
            "email": current_user["preferred_username"],
        }
    return dict(current_user=current_user)


@bp.route("/login")
def login():
    """Initiate login process."""
    # Set session as permanent BEFORE starting OAuth
    session.permanent = True
    return auth.login()

