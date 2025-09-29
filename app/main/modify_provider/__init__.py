from flask import Blueprint

from app.utils import register_form_view

from .forms import AssignChambersForm, ChangeLiaisonManagerForm
from .views import AssignChambersFormView, ChangeLiaisonManagerFormView


def register_views(bp: Blueprint):
    register_form_view(
        form_class=ChangeLiaisonManagerForm,
        view_class=ChangeLiaisonManagerFormView,
        blueprint=bp,
        endpoint="add_new_liaison_manager",
    )
    register_form_view(
        form_class=AssignChambersForm,
        view_class=AssignChambersFormView,
        blueprint=bp,
        endpoint="assign_chambers",
    )
