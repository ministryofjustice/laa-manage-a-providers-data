import datetime
from typing import Any

from flask import Response, current_app, flash, redirect, render_template, url_for

from app.forms import BaseForm
from app.main.utils import change_liaison_manager
from app.main.views import get_main_table
from app.models import Contact, Firm
from app.views import FullWidthBaseFormView


class ChangeLiaisonManagerFormView(FullWidthBaseFormView):
    def get_success_url(self, firm):
        return url_for("main.view_provider", firm=firm)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super(ChangeLiaisonManagerFormView, self).get_context_data(form, context, **kwargs)
        context.update({"cancel_url": self.get_success_url(form.firm)})
        return context

    def form_valid(self, form):
        # Create Contact instance from form data
        new_contact = Contact(
            first_name=form.data.get("first_name"),
            last_name=form.data.get("last_name"),
            email_address=form.data.get("email_address"),
            telephone_number=form.data.get("telephone_number"),
            website=form.data.get("website"),
        )

        # Change the liaison manager (defaults to head office if no office_code specified)
        change_liaison_manager(new_contact, form.firm.firm_id)

        return redirect(self.get_success_url(form.firm))

    def get(self, firm, context, **kwargs):
        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class ChangeProviderActiveStatusFormView(FullWidthBaseFormView):
    def get_success_url(self, form):
        return url_for("main.view_provider", firm=form.firm)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form=form, context=context, **kwargs)
        context.update({"main_table": get_main_table(form.firm, head_office=None, parent_firm=None)})
        return context

    def get(self, firm: Firm, context, **kwargs):
        status = "inactive" if firm.inactive_date else "active"
        form = self.get_form_class()(status=status, firm=firm)
        return render_template(self.template, **self.get_context_data(form))

    def post(self, firm, context, **kwargs):
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

    def form_valid(self, form):
        status = form.data.get("status")
        inactive_date = None
        if status == "inactive":
            inactive_date = datetime.date.today().strftime("%Y-%m-%d")
        data = {Firm.model_fields["inactive_date"].alias: inactive_date}

        pda = current_app.extensions["pda"]
        pda.patch_provider_firm(form.firm.firm_id, data)
        flash(f"{form.firm.firm_name} marked as {status}", "success")
        return super().form_valid(form)
