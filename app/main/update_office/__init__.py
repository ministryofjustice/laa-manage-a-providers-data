from app.utils import register_form_view

from .forms import (
    BankAccountSearchForm,
    ChangeOfficeContactDetailsForm,
    PaymentMethodForm,
    UpdateVATRegistrationNumberForm,
)
from .views import (
    ChangeOfficeContactDetailsFormView,
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
        form_class=BankAccountSearchForm,
        view_class=SearchBankAccountFormView,
        blueprint=bp,
        endpoint="search_bank_account",
    )
    register_form_view(
        form_class=ChangeOfficeContactDetailsForm,
        view_class=ChangeOfficeContactDetailsFormView,
        blueprint=bp,
        endpoint="change_office_contact_details_form",
    )
