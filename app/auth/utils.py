from functools import wraps

from flask import redirect, request, session, url_for


def requires_authentication(f):
    """
    Decorator that checks if user is logged in by checking their session.
    Redirects to login page if not authenticated.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "authenticated" not in session or not session["authenticated"]:
            session["next_url"] = request.url
            return redirect(url_for("authentication.authenticate"))
        return f(*args, **kwargs)

    return decorated_function
