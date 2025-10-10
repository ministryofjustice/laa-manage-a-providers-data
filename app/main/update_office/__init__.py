from app.utils import register_form_view

from .forms import (
    BankAccountSearchForm,
    ChangeOfficeActiveStatusForm,
    PaymentMethodForm,
    UpdateVATRegistrationNumberForm,
)
from .views import (
    OfficeActiveStatusFormView,
    PaymentMethodFormView,
    SearchBankAccountFormView,
    UpdateVATRegistrationNumberFormView,
)


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
    register_form_view(
        form_class=ChangeOfficeActiveStatusForm,
        view_class=OfficeActiveStatusFormView,
        blueprint=bp,
        endpoint="office_active_status_form",
    )
    register_form_view(
        form_class=BankAccountSearchForm,
        view_class=SearchBankAccountFormView,
        blueprint=bp,
        endpoint="search_bank_account",
    )
