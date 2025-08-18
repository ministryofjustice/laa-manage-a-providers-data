from flask import Blueprint

from app.main.forms import ProviderListForm
from app.main.views import ProviderList, ViewProvider
from app.utils import register_form_view

bp = Blueprint("main", __name__, template_folder="templates")

# Import modules after blueprint creation to avoid circular imports
from app.main import middleware  # noqa: E402,F401
from app.main import routes  # noqa: E402,F401
from app.main.add_a_new_provider import register_views  # noqa: E402,F401

register_form_view(form_class=ProviderListForm, view_class=ProviderList, blueprint=bp)

bp.add_url_rule("/view-provider", defaults={"firm_id": None}, view_func=ViewProvider.as_view("view_provider"))
bp.add_url_rule("/view-provider/<int:firm_id>", view_func=ViewProvider.as_view("view_provider_with_id"))
