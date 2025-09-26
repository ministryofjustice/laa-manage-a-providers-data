from app.utils import register_form_view

from .forms import UpdateVATRegistrationNumberForm, PaymentMethodForm
from .views import UpdateVATRegistrationNumberFormView, PaymentMethodFormView


def register_views(bp):
    register_form_view(
        form_class=UpdateVATRegistrationNumberForm,
        view_class=UpdateVATRegistrationNumberFormView,
        blueprint=bp,
        endpoint="add_office_vat_number",
    )
    register_form_view(
        form_class=PaymentMethodForm,
        view_class=PaymentMethodFormView,
        blueprint=bp,
        endpoint="payment_method_form",
    )
