from flask import Blueprint

from app.utils import register_form_view

from .forms import (
    AssignChambersForm,
    ChangeContractManagerForm,
    ChangeLiaisonManagerForm,
    ChangeOfficeContractManagerForm,
    ChangeOfficeLiaisonManagerForm,
    ChangeProviderActiveStatusForm,
    ReassignHeadOfficeForm,
)
from .views import (
    AssignChambersFormView,
    ChangeContractManagerFormView,
    ChangeLiaisonManagerFormView,
    ChangeProviderActiveStatusFormView,
    ReassignHeadOfficeFormView,
)


def register_views(bp: Blueprint):
    register_form_view(
        form_class=ChangeLiaisonManagerForm,
        view_class=ChangeLiaisonManagerFormView,
        blueprint=bp,
        endpoint="add_new_liaison_manager",
    )
    register_form_view(
        form_class=ChangeOfficeLiaisonManagerForm,
        view_class=ChangeLiaisonManagerFormView,
        blueprint=bp,
        endpoint="add_new_office_liaison_manager",
    )
    register_form_view(
        form_class=ChangeProviderActiveStatusForm,
        view_class=ChangeProviderActiveStatusFormView,
        blueprint=bp,
        endpoint="change_provider_active_status",
    )
    register_form_view(
        form_class=AssignChambersForm, view_class=AssignChambersFormView, blueprint=bp, endpoint="assign_chambers"
    )
    register_form_view(
        form_class=ReassignHeadOfficeForm,
        view_class=ReassignHeadOfficeFormView,
        blueprint=bp,
        endpoint="reassign_head_office",
    )
    register_form_view(
        form_class=ChangeContractManagerForm,
        view_class=ChangeContractManagerFormView,
        blueprint=bp,
        endpoint="change_contract_manager",
    )
    register_form_view(
        form_class=ChangeOfficeContractManagerForm,
        view_class=ChangeContractManagerFormView,
        blueprint=bp,
        endpoint="change_office_contract_manager",
    )
