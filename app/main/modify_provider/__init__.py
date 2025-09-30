from flask import Blueprint

from app.utils import register_form_view

from .forms import AssignChambersForm, ChangeLiaisonManagerForm, ChangeProviderActiveStatusForm
from .views import AssignChambersFormView, ChangeLiaisonManagerFormView, ChangeProviderActiveStatusFormView


def register_views(bp: Blueprint):
    register_form_view(
        form_class=ChangeLiaisonManagerForm,
        view_class=ChangeLiaisonManagerFormView,
        blueprint=bp,
        endpoint="add_new_liaison_manager",
    )
    register_form_view(
        form_class=ChangeProviderActiveStatusForm,
        view_class=ChangeProviderActiveStatusFormView,
        blueprint=bp,
        endpoint="change_provider_active_status",
    )
    register_form_view(
        form_class=AssignChambersForm,
        view_class=AssignChambersFormView,
        blueprint=bp,
        endpoint="assign_chambers",
