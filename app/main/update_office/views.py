from typing import Any

from flask import Response, abort, current_app, flash, redirect, render_template, request, session, url_for

from app.forms import BaseForm
from app.main.update_office.forms import NoBankAccountsError
from app.models import BankAccount, Firm, Office
from app.utils.formatting import format_office_address_one_line
from app.views import BaseFormView, FullWidthBaseFormView


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


class SearchBankAccountFormView(BaseFormView):
    """Form view for to search for bank accounts"""

    template = "update_office/search-bank-account.html"
    success_endpoint = "main.view_office_bank_payment_details"

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update(
            {
                "office_address": format_office_address_one_line(form.office),
                "add_new_bank_account_url": url_for("main.add_office_bank_account", firm=form.firm, office=form.office),
            }
        )
        return context

    def get_success_url(self, form: BaseForm | None = None) -> str:
        return url_for(self.success_endpoint, firm=form.firm, office=form.office)

    def form_valid(self, form: BaseForm, **kwargs) -> str:
        pda = current_app.extensions["pda"]
        pda.assign_bank_account_to_office(form.firm.firm_id, form.office.firm_office_code, form.bank_account.data)
        return super().form_valid(form, **kwargs)

    def get(self, firm, office: Office, context, **kwargs):
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))

        try:
            form = self.get_form_class()(firm, office, search_term=search_term, page=page)
        except NoBankAccountsError:
            # This firm does not have any bank accounts, so redirect the user to a form to add new bank account details
            url = url_for("main.add_office_bank_account", firm=firm, office=office)
            return redirect(url)

        if search_term:
            form.search.validate(form)

        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def post(self, firm, office: Office, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm, office)
        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class AddBankAccountFormView(BaseFormView):
    def get_success_url(self, form):
        return url_for("main.view_office_bank_payment_details", firm=form.firm, office=form.office)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form)
        context.update({"office_address": format_office_address_one_line(form.office)})
        return context

    def form_valid(self, form):
        bank_account = BankAccount(
            **{
                "sortCode": form.sort_code.data,
                "accountNumber": form.account_number.data,
                "bankAccountName": form.bank_account_name.data,
                "vendorSiteId": form.office.firm_office_id,
            }
        )
        pda = current_app.extensions["pda"]
        pda.add_bank_account_to_office(form.firm.firm_id, form.office.firm_office_code, bank_account)
        return super().form_valid(form)

    def get(self, firm, office, *args, **kwargs):
        form = self.get_form_class()(firm=firm, office=office)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm: Firm, office: Office, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm, office=office)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
