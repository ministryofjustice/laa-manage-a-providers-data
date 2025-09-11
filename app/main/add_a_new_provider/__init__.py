from app.main import bp
from app.utils import register_form_view

from .forms import (
    AddProviderForm,
    AdvocateDetailsForm,
    AssignChambersForm,
    BankAccountForm,
    HeadOfficeContactDetailsForm,
    LiaisonManagerForm,
    LspDetailsForm,
    VATRegistrationForm,
)
from .views import (
    AddProviderFormView,
    AdvocateDetailsFormView,
    AssignChambersFormView,
    BankAccountFormView,
    HeadOfficeContactDetailsFormView,
    LiaisonManagerFormView,
    LspDetailsFormView,
    VATRegistrationFormView,
)


def register_views():
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


register_views()
