from app.utils import register_form_view

from .forms import UpdateVATRegistrationNumberForm
from .views import UpdateVATRegistrationNumberFormView


def register_views(bp):
    register_form_view(
        form_class=UpdateVATRegistrationNumberForm,
        view_class=UpdateVATRegistrationNumberFormView,
        blueprint=bp,
        endpoint="add_office_vat_number",
    )
