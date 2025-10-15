import datetime
from typing import Any

from flask import Response, abort, current_app, flash, redirect, render_template, request, url_for

from app.forms import BaseForm
from app.main.modify_provider import AssignChambersForm
from app.main.utils import assign_firm_to_a_new_chambers, change_liaison_manager
from app.main.views import get_main_table
from app.models import Contact, Firm, Office
from app.views import BaseFormView, FullWidthBaseFormView


class ChangeLiaisonManagerFormView(FullWidthBaseFormView):
    def get_success_url(self, firm):
        return url_for("main.view_provider", firm=firm)

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
        context.update({"cancel_url": self.get_success_url(form)})

        pda = current_app.extensions["pda"]
        if form.firm.firm_id:
            # Get head office for account number
            head_office: Office = pda.get_head_office(form.firm.firm_id)
            context.update({"head_office": head_office})

        if form.firm.parent_firm_id:
            # Get parent provider
            parent_provider: Firm = pda.get_provider_firm(form.firm.parent_firm_id)
            context.update({"parent_provider": parent_provider})

        if form.firm.is_legal_service_provider or form.firm.is_chambers:
            context.update(
                {
                    "main_table": get_main_table(
                        form.firm, head_office=context.get("head_office"), parent_firm=context.get("parent_provider")
                    ),
                }
            )
        else:
            context.update({"caption": form.firm.firm_name})

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
        firm = pda.patch_provider_firm(form.firm.firm_id, data)
        if firm:
            flash(f"{form.firm.firm_name} marked as {status}", "success")
        return super().form_valid(form)


class AssignChambersFormView(BaseFormView):
    """Form view for the assign to a chambers form"""

    template = "add_provider/assign-chambers.html"
    success_endpoint = "main.create_provider"
    form_class: AssignChambersForm

    def get_success_url(self, form):
        return url_for("main.view_provider", firm=form.firm)

    def form_valid(self, form):
        new_chambers_id = int(form.data.get("provider"))
        assign_firm_to_a_new_chambers(form.firm, new_chambers_id)
        return redirect(self.get_success_url(form))

    @staticmethod
    def get_valid_firm_or_abort(firm):
        if not firm:
            abort(400)

        if firm.firm_type not in ["Barrister", "Advocate"]:
            abort(400)

    def get(self, firm, context):
        self.get_valid_firm_or_abort(firm)
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(firm=firm, search_term=search_term, page=page)

        if search_term:
            form.search.validate(form)

        return render_template(self.get_template(), **self.get_context_data(form, context))

    def post(self, firm, context) -> Response | str:
        self.get_valid_firm_or_abort(firm)
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(firm=firm, search_term=search_term, page=page)
        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
