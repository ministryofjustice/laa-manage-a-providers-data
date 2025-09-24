from flask import Response, abort, flash, redirect, render_template, session, url_for, current_app

from app.models import Firm, Office
from app.views import BaseFormView


class PaymentMethodFormView(BaseFormView):
    """Form view for the payment method form"""

    def get_success_url(self, form, firm, office=None):
        if office:
            return url_for("main.view_office", firm=firm, office=office)
        return url_for("main.view_office", firm=firm)

    def form_valid(self, form):
        if not hasattr(form, "firm") or not hasattr(form, "office"):
            abort(400)

        # Update the office with payment method
        pda = current_app.extensions["pda"]
        updated_office = pda.update_office_payment_method(
            firm_id=form.firm.firm_id,
            office_code=form.office.firm_office_code,
            payment_method=form.data.get("payment_method"),
        )
        if not updated_office:
            flash("Failed to update payment method", "error")
            return self.form_invalid(form)

        # Save the selection to the session to use later
        session["payment_method"] = form.data.get("payment_method")

        flash("Payment method updated successfully", "success")
        return redirect(self.get_success_url(form, form.firm, updated_office))

    def get(self, context, firm: Firm, office: Office = None, **kwargs):
        if not office:
            abort(404)

        form = self.get_form_class()(firm=firm, office=office)
        # Pre-populate radio with currently saved value when landing on the change page
        if getattr(office, "payment_method", None):
            form.payment_method.data = office.payment_method
        context = self.get_context_data(form, **kwargs)

        # Build office address string expected by reusable template
        address_parts = [
            office.address_line_1,
            office.address_line_2,
            office.address_line_3,
            office.address_line_4,
            office.city,
            office.county,
            office.postcode,
        ]
        office_address = ", ".join(part for part in address_parts if part)
        context.update({"office_address": office_address})

        return render_template(self.template, **context)

    def post(self, firm: Firm, office: Office = None, *args, **kwargs) -> Response | str:
        if not office:
            abort(404)

        form = self.get_form_class()(firm=firm, office=office)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
