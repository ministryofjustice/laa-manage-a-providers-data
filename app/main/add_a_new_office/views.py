from flask import Response, abort, redirect, render_template, session, url_for

from app.forms import BaseForm
from app.main.utils import add_new_office
from app.models import Firm, Office
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

    def get_success_url(self, new_office: Office, firm: Firm) -> str:
        return url_for("main.view_office", firm=firm, office=new_office)

    def form_valid(self, form):
        # Check if office data exists in session
        if not session.get("new_office"):
            abort(500)

        # Add contact details to the existing office dict
        session["new_office"].update(
            {
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

        # Create the office
        office = Office(**session.get("new_office"))
        new_office = add_new_office(office, firm_id=form.firm.firm_id)

        return redirect(self.get_success_url(new_office, form.firm))

    def get(self, context, firm: Firm, **kwargs):
        # Check if office data exists in session
        if not session.get("new_office"):
            abort(400)

        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm: Firm, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

class PaymentMethodFormView(BaseFormView):
    """Form view for the payment method form""" 

    def get_success_url(self, form, firm, office=None):
        if office:
            return url_for("main.view_office", firm=firm.firm_id, office_id=office.office_id)
        return url_for("main.view_office", firm=firm.firm_id)
    
    def form_valid(self, form): 
        if not hasattr(form, 'firm') or not hasattr(form, 'office'):
            abort(400)

        # Update the office with payment method
        form.office.payment_method = form.data.get("payment_method")
        form.office.save()

        return redirect(self.get_success_url(form.firm, form.office))

    def get(self, context, firm: Firm, office: Office = None, **kwargs):
        if not office:
            abort(404)

        form = self.get_form_class()(firm=firm, office=office)
        context = self.get_context_data(form, **kwargs)
        
        # Add caption data to context if it's a dictionary
        caption_data = form.caption
        if isinstance(caption_data, dict):
            context.update(caption_data)
            
        return render_template(self.template, **context)

    def post(self, firm: Firm, office: Office = None, *args, **kwargs) -> Response | str:
        if not office:
            abort(404)
            
        form = self.get_form_class()(firm=firm, office=office)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
