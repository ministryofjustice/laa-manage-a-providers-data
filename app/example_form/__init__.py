from flask import Blueprint

from app.utils import register_form_view

from .forms import ExampleForm
from .views import ExampleFormView

bp = Blueprint("example_form", __name__)

register_form_view(form_class=ExampleForm, view_class=ExampleFormView, blueprint=bp)
from .routes import *  # noqa: E402,F401,F403
