from app.main.add_a_new_office.forms import OfficeContactDetailsForm
from app.main.add_a_new_office.views import OfficeContactDetailsFormView
from app.utils import register_form_view


def register_views(bp):
    register_form_view(
        form_class=OfficeContactDetailsForm,
        view_class=OfficeContactDetailsFormView,
        blueprint=bp,
        endpoint="add_office_contact_details",
    )
