from flask import Blueprint

from app.main.forms import ProviderListForm
from app.main.views import ProviderList, ViewOffice, ViewProvider
from app.utils import register_form_view

bp = Blueprint("main", __name__, template_folder="templates")

# Import modules after blueprint creation to avoid circular imports
from app.main import middleware  # noqa: E402,F401
from app.main import routes  # noqa: E402,F401
from app.main import add_a_new_office, add_a_new_provider  # noqa: E402,F401

register_form_view(form_class=ProviderListForm, view_class=ProviderList, blueprint=bp)

bp.add_url_rule("/view-provider", defaults={"firm": None}, view_func=ViewProvider.as_view("view_provider"))
bp.add_url_rule("/view-provider/<firm:firm>", view_func=ViewProvider.as_view("view_provider_with_id"))

bp.add_url_rule("/provider/<firm:firm>/view-office/<office:office>", view_func=ViewOffice.as_view("view_office"))
