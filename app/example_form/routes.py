from flask import render_template, session

from app import auth

from . import bp


@bp.get("/success")
@auth.login_required
def success(*, context):
    name = session.get("full_name")
    return render_template("success.html", name=name)
