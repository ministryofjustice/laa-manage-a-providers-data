from app.utils import register_form_view

from .forms import AddProviderForm, ChambersDetailsForm, LspDetailsForm, ParentProviderForm, AddParentProviderForm
from .views import (
    AddProviderFormView,
    ChambersDetailsFormView,
    LspDetailsFormView,
    ParentProviderFormView,
    AddParentProviderFormView,
)
from app.main import bp


def register_views():
    register_form_view(form_class=AddProviderForm, view_class=AddProviderFormView, blueprint=bp)

    register_form_view(form_class=LspDetailsForm, view_class=LspDetailsFormView, blueprint=bp)

    register_form_view(form_class=ChambersDetailsForm, view_class=ChambersDetailsFormView, blueprint=bp)

    register_form_view(form_class=ParentProviderForm, view_class=ParentProviderFormView, blueprint=bp)

    register_form_view(form_class=AddParentProviderForm, view_class=AddParentProviderFormView, blueprint=bp)


register_views()
