from flask import render_template, session

from app.main import bp


@bp.get("/")
def index():
    """Directs the user to the start page of the service
    This is the endpoint directed to from the header text, clicking this link will reset the users' session.
    """
    return render_template("index.html")


@bp.route("/status", methods=["GET"])
def status():
    return "OK"
