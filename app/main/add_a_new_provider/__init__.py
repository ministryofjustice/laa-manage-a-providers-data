from app.utils import register_form_view

from .forms import (
    AddAdvocateForm,
    AddBarristerForm,
    AddProviderForm,
    AdvocateDetailsForm,
    AssignChambersForm,
    AssignContractManagerForm,
    BankAccountForm,
    HeadOfficeContactDetailsForm,
    LiaisonManagerForm,
    LspDetailsForm,
    VATRegistrationForm,
)
from .views import (
    AddAdvocateFormView,
    AddBarristerFormView,
    AddProviderFormView,
    AdvocateDetailsFormView,
    AssignChambersFormView,
    AssignContractManagerFormView,
    BankAccountFormView,
    HeadOfficeContactDetailsFormView,
    LiaisonManagerFormView,
    LspDetailsFormView,
    VATRegistrationFormView,
)


def register_views(bp):
    register_form_view(form_class=AddProviderForm, view_class=AddProviderFormView, blueprint=bp)

    register_form_view(form_class=LspDetailsForm, view_class=LspDetailsFormView, blueprint=bp)

    register_form_view(form_class=AdvocateDetailsForm, view_class=AdvocateDetailsFormView, blueprint=bp)

    register_form_view(form_class=AssignChambersForm, view_class=AssignChambersFormView, blueprint=bp)

    register_form_view(
        form_class=HeadOfficeContactDetailsForm, view_class=HeadOfficeContactDetailsFormView, blueprint=bp
    )

    register_form_view(form_class=VATRegistrationForm, view_class=VATRegistrationFormView, blueprint=bp)

    register_form_view(form_class=BankAccountForm, view_class=BankAccountFormView, blueprint=bp)

    register_form_view(form_class=LiaisonManagerForm, view_class=LiaisonManagerFormView, blueprint=bp)

    register_form_view(form_class=AssignContractManagerForm, view_class=AssignContractManagerFormView, blueprint=bp)

    register_form_view(
        form_class=AddBarristerForm, view_class=AddBarristerFormView, blueprint=bp, endpoint="add_barrister_form"
    )

    register_form_view(
        form_class=AddAdvocateForm, view_class=AddAdvocateFormView, blueprint=bp, endpoint="add_advocate_form"
    )
