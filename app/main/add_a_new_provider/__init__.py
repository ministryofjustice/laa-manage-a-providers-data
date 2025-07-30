from app.utils import register_form_view
from .forms import AddProviderForm
from .views import AddProviderFormView
from app.main import bp

def register_views():
  register_form_view(form_class=AddProviderForm, view_class=AddProviderFormView, blueprint=bp)

register_views()