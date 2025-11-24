from flask import Blueprint

from app.utils import register_form_view

from .forms import (
    AssignChambersForm,
    ChangeLegalServicesProviderNameForm,
    BarristerChangeDetailsForm,
    ChangeLiaisonManagerForm,
    ChangeLspDetailsForm,
    ChangeOfficeLiaisonManagerForm,
    ChangeProviderActiveStatusForm,
    ReassignHeadOfficeForm,
)
from .views import (
    AssignChambersFormView,
    ChangeLegalServicesProviderNameFormView,
    BarristerChangeDetailsView,
    ChangeLiaisonManagerFormView,
    ChangeLspDetailsFormView,
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
        form_class=ChangeLegalServicesProviderNameForm,
        view_class=ChangeLegalServicesProviderNameFormView,
        blueprint=bp,
        endpoint="change_legal_services_provider_name",
    )
    register_form_view(
        form_class=ChangeLspDetailsForm,
        view_class=ChangeLspDetailsFormView,
        blueprint=bp,
        endpoint="change_lsp_details",
    )
    register_form_view(
        form_class=BarristerChangeDetailsForm,
        view_class=BarristerChangeDetailsView,
        blueprint=bp,
        endpoint="barrister_change_details",
    )
