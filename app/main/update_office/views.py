from flask import Response, current_app, render_template, url_for

from app.forms import BaseForm
from app.main.update_office.forms import UpdateVATRegistrationNumberForm
from app.views import FullWidthBaseFormView


class UpdateVATRegistrationNumberFormView(FullWidthBaseFormView):
    form_class = UpdateVATRegistrationNumberForm
    success_endpoint = "main.view_office_bank_payment_details"
    template = "update_office/form.html"

    def get_success_url(self, form: BaseForm | None = None) -> str:
        return url_for(self.success_endpoint, firm=form.firm, office=form.office)

    def form_valid(self, form):
        pda = current_app.extensions["pda"]
        pda.update_office_vat_registration_number(
            form.firm.firm_id, form.office.firm_office_code, form.data.get("vat_registration_number")
        )
        return super().form_valid(form)

    def get(self, firm, office, *args, **kwargs):
        form = self.get_form_class()(firm=firm, office=office, vat_registration_number=office.vat_registration_number)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm, office, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm, office=office)
        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
