from app.utils import register_form_view

from .forms import (
    AddAdvocateCheckForm,
    AddAdvocateDetailsForm,
    AddAdvocateLiaisonManagerForm,
    AddBarristerCheckForm,
    AddBarristerDetailsForm,
    AddBarristerLiaisonManagerForm,
    AddProviderForm,
    AdvocateDetailsForm,
    AssignContractManagerForm,
    BankAccountForm,
    HeadOfficeContactDetailsForm,
    LiaisonManagerForm,
    LspDetailsForm,
    VATRegistrationForm,
)
from .views import (
    AddAdvocateBarristersCheckFormView,
    AddAdvocateBarristersLiaisonManagerFormView,
    AddAdvocateDetailsFormView,
    AddBarristerDetailsFormView,
    AddProviderFormView,
    AdvocateDetailsFormView,
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

    register_form_view(
        form_class=HeadOfficeContactDetailsForm, view_class=HeadOfficeContactDetailsFormView, blueprint=bp
    )

    register_form_view(form_class=VATRegistrationForm, view_class=VATRegistrationFormView, blueprint=bp)

    register_form_view(form_class=BankAccountForm, view_class=BankAccountFormView, blueprint=bp)

    register_form_view(form_class=LiaisonManagerForm, view_class=LiaisonManagerFormView, blueprint=bp)

    register_form_view(form_class=AssignContractManagerForm, view_class=AssignContractManagerFormView, blueprint=bp)

    register_form_view(
        form_class=AddBarristerDetailsForm,
        view_class=AddBarristerDetailsFormView,
        blueprint=bp,
        endpoint="add_barrister_details_form",
    )
    register_form_view(
        form_class=AddBarristerCheckForm,
        view_class=AddAdvocateBarristersCheckFormView,
        blueprint=bp,
        endpoint="add_barrister_check_form",
        model_type="barrister",
    )
    register_form_view(
        form_class=AddBarristerLiaisonManagerForm,
        view_class=AddAdvocateBarristersLiaisonManagerFormView,
        blueprint=bp,
        endpoint="add_barrister_liaison_manager_form",
        model_type="barrister",
    )
    register_form_view(
        form_class=AddAdvocateDetailsForm,
        view_class=AddAdvocateDetailsFormView,
        blueprint=bp,
        endpoint="add_advocate_details_form",
    )
    register_form_view(
        form_class=AddAdvocateCheckForm,
        view_class=AddAdvocateBarristersCheckFormView,
        blueprint=bp,
        endpoint="add_advocate_check_form",
        model_type="advocate",
    )
    register_form_view(
        form_class=AddAdvocateLiaisonManagerForm,
        view_class=AddAdvocateBarristersLiaisonManagerFormView,
        blueprint=bp,
        endpoint="add_advocate_liaison_manager_form",
        model_type="advocate",
    )
