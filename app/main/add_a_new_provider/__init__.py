from app.utils import register_form_view
from .forms import AddProviderForm, LspDetailsForm, ChambersDetailsForm, ParentProviderForm
from .views import AddProviderFormView, LspDetailsFormView, ChambersDetailsFormView, ParentProviderFormView
from app.main import bp


def register_views():
    register_form_view(form_class=AddProviderForm, view_class=AddProviderFormView, blueprint=bp)

    register_form_view(form_class=LspDetailsForm, view_class=LspDetailsFormView, blueprint=bp)

    register_form_view(form_class=ChambersDetailsForm, view_class=ChambersDetailsFormView, blueprint=bp)

    register_form_view(form_class=ParentProviderForm, view_class=ParentProviderFormView, blueprint=bp)


register_views()
