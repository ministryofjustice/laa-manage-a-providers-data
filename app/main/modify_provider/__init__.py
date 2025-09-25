from flask import Blueprint

from app.utils import register_form_view

from .forms import ChangeLiaisonManagerForm, ChangeProviderActiveStatusForm
from .views import ChangeLiaisonManagerFormView, ChangeProviderActiveStatusFormView


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
