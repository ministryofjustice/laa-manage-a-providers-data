from app.main import bp
from app.utils import register_form_view

from .forms import AddProviderForm, AdvocateDetailsForm, ChambersDetailsForm, LspDetailsForm, ParentProviderForm
from .views import (
    AddProviderFormView,
    AdvocateDetailsFormView,
    ChambersDetailsFormView,
    LspDetailsFormView,
    ParentProviderFormView,
)


def register_views():
    register_form_view(form_class=AddProviderForm, view_class=AddProviderFormView, blueprint=bp)

    register_form_view(form_class=LspDetailsForm, view_class=LspDetailsFormView, blueprint=bp)

    register_form_view(form_class=AdvocateDetailsForm, view_class=AdvocateDetailsFormView, blueprint=bp)

    register_form_view(form_class=ChambersDetailsForm, view_class=ChambersDetailsFormView, blueprint=bp)

    register_form_view(form_class=AssignChambersForm, view_class=AssignChambersFormView, blueprint=bp)


register_views()
