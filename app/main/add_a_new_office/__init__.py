from app.main import bp
from app.main.add_a_new_office.forms import AddOfficeForm, OfficeContactDetailsForm
from app.main.add_a_new_office.views import AddOfficeFormView, OfficeContactDetailsFormView
from app.utils import register_form_view


def register_views():
    register_form_view(form_class=AddOfficeForm, view_class=AddOfficeFormView, blueprint=bp, endpoint="add_office")
    register_form_view(
        form_class=OfficeContactDetailsForm,
        view_class=OfficeContactDetailsFormView,
        blueprint=bp,
        endpoint="add_office_contact_details",
    )


register_views()
