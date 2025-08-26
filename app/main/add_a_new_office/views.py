from flask import Response, abort, render_template, session, url_for

from app.forms import BaseForm
from app.models import Firm
from app.views import BaseFormView


class AddOfficeFormView(BaseFormView):
    """Form view for the Add a new office page"""

    def get_success_url(self, form: BaseForm | None = None) -> str:
        if not form or not hasattr(form, "firm"):
            abort(404)

        return url_for("main.add_office_contact_details", firm=form.firm)

    def form_valid(self, form):
        session["new_office"] = {
            "office_name": form.data.get("office_name"),
            "is_head_office": form.data.get("is_head_office"),
        }

        return super().form_valid(form)

    def get(self, context, firm: Firm, **kwargs):
        form = self.get_form_class()(firm=firm)

        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm: Firm, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class OfficeContactDetailsFormView(BaseFormView):
    """Form view for the Office Contact Details page"""

    def get_success_url(self, form: BaseForm | None = None) -> str:
        if not form or not hasattr(form, "firm"):
            abort(404)

        return url_for("main.view_provider_with_id", firm=form.firm)

    def form_valid(self, form):
        # Check if office data exists in session
        if not session.get("new_office"):
            abort(404)

        # Add contact details to the existing office dict
        session["new_office"].update(
            {
                "address_line_1": form.data.get("address_line_1"),
                "address_line_2": form.data.get("address_line_2"),
                "address_line_3": form.data.get("address_line_3"),
                "address_line_4": form.data.get("address_line_4"),
                "city": form.data.get("city"),
                "county": form.data.get("county"),
                "post_code": form.data.get("post_code"),
                "telephone_number": form.data.get("telephone_number"),
                "email_address": form.data.get("email_address"),
                "dx_number": form.data.get("dx_number"),
                "dx_centre": form.data.get("dx_centre"),
            }
        )

        return super().form_valid(form)

    def get(self, context, firm: Firm, **kwargs):
        # Check if office data exists in session
        if not session.get("new_office"):
            abort(404)

        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm: Firm, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
