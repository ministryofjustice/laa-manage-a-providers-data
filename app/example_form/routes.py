from flask import render_template, session

from . import bp
from app import auth


@bp.get("/success")
@auth.login_required
def success(*, context):
    name = session.get("full_name")
    return render_template("success.html", name=name, user=context["user"])
