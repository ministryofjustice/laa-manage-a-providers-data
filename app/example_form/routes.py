from flask import render_template, session
from . import bp


@bp.get("/success")
def success():
    name = session.get('full_name')
    return render_template("success.html", name=name)