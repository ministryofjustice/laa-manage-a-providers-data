from app.main import bp
from app.utils import register_form_view

from .forms import ChangeLiaisonManagerForm
from .views import ChangeLiaisonManagerFormView


def register_views():
    register_form_view(
        form_class=ChangeLiaisonManagerForm,
        view_class=ChangeLiaisonManagerFormView,
        blueprint=bp,
        endpoint="add_new_liaison_manager",
    )


register_views()
