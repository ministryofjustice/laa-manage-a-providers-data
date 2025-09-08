from app.main import bp
from app.utils import register_form_view

from .forms import (
    AddProviderForm,
    AdvocateDetailsForm,
    AssignChambersForm,
    ChambersDetailsForm,
    HeadOfficeContactDetailsForm,
    LspDetailsForm,
)
from .views import (
    AddProviderFormView,
    AdvocateDetailsFormView,
    AssignChambersFormView,
    ChambersDetailsFormView,
    HeadOfficeContactDetailsFormView,
    LspDetailsFormView,
)


def register_views():
    register_form_view(form_class=AddProviderForm, view_class=AddProviderFormView, blueprint=bp)

    register_form_view(form_class=LspDetailsForm, view_class=LspDetailsFormView, blueprint=bp)

    register_form_view(form_class=AdvocateDetailsForm, view_class=AdvocateDetailsFormView, blueprint=bp)

    register_form_view(form_class=ChambersDetailsForm, view_class=ChambersDetailsFormView, blueprint=bp)

    register_form_view(form_class=AssignChambersForm, view_class=AssignChambersFormView, blueprint=bp)

    register_form_view(
        form_class=HeadOfficeContactDetailsForm, view_class=HeadOfficeContactDetailsFormView, blueprint=bp
    )


register_views()
