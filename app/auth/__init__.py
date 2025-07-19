from flask import Blueprint

from app.auth.forms import AuthenticationForm
from app.auth.utils import requires_authentication as requires_authentication
from app.auth.views import AuthenticationFormView
from app.utils import register_form_view

bp = Blueprint("authentication", __name__)

register_form_view(form_class=AuthenticationForm, view_class=AuthenticationFormView, blueprint=bp)
