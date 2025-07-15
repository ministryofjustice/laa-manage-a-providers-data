import uuid

from flask import Blueprint, session
from app import auth

bp = Blueprint("auth", __name__)


@bp.route("/login")
def login():
    """Initiate login process."""
    # Set session as permanent BEFORE starting OAuth
    session.permanent = True
    state = str(uuid.uuid4())
    return auth.login(state="I AM A TEST STATE", next_link=)


@bp.route("/logout")
def logout():
    """Log out the current user."""
    session.clear()
    return auth.logout()
