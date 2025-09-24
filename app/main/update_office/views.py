from typing import Any

from flask import Response, current_app, render_template, url_for

from app.forms import BaseForm
from app.utils.formatting import format_office_address_one_line
from app.views import FullWidthBaseFormView


class UpdateVATRegistrationNumberFormView(FullWidthBaseFormView):
    success_endpoint = "main.view_office_bank_payment_details"
    template = "update_office/form.html"

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update({"office_address": format_office_address_one_line(form.office)})
        return context

    def get_success_url(self, form: BaseForm | None = None) -> str:
        return url_for(self.success_endpoint, firm=form.firm, office=form.office)

    def form_valid(self, form):
        pda = current_app.extensions["pda"]
        data = {"vatRegistrationNumber": form.data.get("vat_registration_number")}
        pda.patch_office(form.firm.firm_id, form.office.firm_office_code, data)
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
