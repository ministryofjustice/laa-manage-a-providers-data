from flask import Response, redirect, render_template, url_for

from app.main.utils import change_liaison_manager
from app.models import Contact
from app.views import FullWidthBaseFormView


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
