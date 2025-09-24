from app.main.update_office.forms import PaymentMethodForm
from app.main.update_office.views import PaymentMethodFormView
from app.utils import register_form_view


def register_views(bp):
    register_form_view(
        form_class=PaymentMethodForm,
        view_class=PaymentMethodFormView,
        blueprint=bp,
        endpoint="payment_method_form",
    )
