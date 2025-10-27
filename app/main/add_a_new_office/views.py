from flask import Response, redirect, render_template, session, url_for

from app.main.utils import add_new_office
from app.models import Firm, Office
from app.views import BaseFormView


class OfficeContactDetailsFormView(BaseFormView):
    """Form view for the Office Contact Details page"""

    def get_success_url(self, new_office: Office, firm: Firm) -> str:
        return url_for("main.view_office", firm=firm, office=new_office)

    def form_valid(self, form):
        head_office = self.get_api().get_head_office(form.firm.firm_id)
        # Add contact details to the existing office dict
        session["new_office"].update(
            {
                "office_name": form.firm.firm_name,
                "is_head_office": not head_office,
                "address_line_1": form.data.get("address_line_1"),
                "address_line_2": form.data.get("address_line_2"),
                "address_line_3": form.data.get("address_line_3"),
                "address_line_4": form.data.get("address_line_4"),
                "city": form.data.get("city"),
                "county": form.data.get("county"),
                "postcode": form.data.get("postcode"),
                "telephone_number": form.data.get("telephone_number"),
                "email_address": form.data.get("email_address"),
                "dx_number": form.data.get("dx_number"),
                "dx_centre": form.data.get("dx_centre"),
            }
        )

        # the new office must be set to Electronic payment method so we do it here before the offcie is created
        session["new_office"]["payment_method"] = "Electronic"

        # Create the office
        office = Office(**session.get("new_office"))
        new_office = add_new_office(office, firm_id=form.firm.firm_id)

        return redirect(self.get_success_url(new_office, form.firm))

    def get(self, context, firm: Firm, **kwargs):
        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm: Firm, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
