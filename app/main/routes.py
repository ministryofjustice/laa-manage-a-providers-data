from flask import render_template, session

from app.main import bp


@bp.app_context_processor
def user_context_processor():
    if current_user := session.get("_logged_in_user"):
        current_user = {
            "name": current_user["name"],
            "email": current_user["preferred_username"],
        }
    return dict(current_user=current_user)


@bp.get("/")
def index():
    """Directs the user to the start page of the service
    This is the endpoint directed to from the header text, clicking this link will reset the users' session.
    """
    return render_template("index.html")


@bp.route("/status", methods=["GET"])
def status():
    return "OK"
