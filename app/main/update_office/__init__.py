from app.utils import register_form_view

from .forms import (
    BankAccountForm,
    BankAccountSearchForm,
    ChangeOfficeActiveStatusForm,
    ChangeOfficeContactDetailsForm,
    ChangeOfficeContractManagerForm,
    ChangeOfficeFalseBalanceForm,
    PaymentMethodForm,
    UpdateVATRegistrationNumberForm,
)
from .views import (
    AddBankAccountFormView,
    ChangeContractManagerFormView,
    ChangeOfficeContactDetailsFormView,
    ChangeOfficeFalseBalanceFormView,
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
    register_form_view(
        form_class=ChangeOfficeContactDetailsForm,
        view_class=ChangeOfficeContactDetailsFormView,
        blueprint=bp,
        endpoint="change_office_contact_details_form",
    )
    register_form_view(
        form_class=BankAccountForm,
        view_class=AddBankAccountFormView,
        blueprint=bp,
        endpoint="add_office_bank_account",
    )
    register_form_view(
        form_class=ChangeOfficeContractManagerForm,
        view_class=ChangeContractManagerFormView,
        blueprint=bp,
        endpoint="change_office_contract_manager",
    )
    register_form_view(
        form_class=ChangeOfficeFalseBalanceForm,
        view_class=ChangeOfficeFalseBalanceFormView,
        blueprint=bp,
        endpoint="change_office_false_balance",
    )
