from flask import Blueprint

bp = Blueprint("main", __name__, template_folder="templates")

from app.main import middleware  # noqa: E402,F401
from app.main import routes  # noqa: E402,F401

# Form views
from app.utils import register_form_view
from app.main.forms import AddProviderForm
from app.main.views import AddProviderFormView

register_form_view(form_class=AddProviderForm, view_class=AddProviderFormView, blueprint=bp)