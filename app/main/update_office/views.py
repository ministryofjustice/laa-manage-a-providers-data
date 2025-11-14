import datetime
import logging
from typing import Any

from flask import Response, abort, current_app, flash, redirect, render_template, request, session, url_for

from app.constants import DEFAULT_CONTRACT_MANAGER_NAME, STATUS_CONTRACT_MANAGER_NAMES
from app.forms import BaseForm
from app.main.forms import NoBankAccountsError
from app.main.utils import firm_office_url_for
from app.main.views import AdvocateBarristerOfficeMixin
from app.models import BankAccount, Firm, Office
from app.pda.errors import ProviderDataApiError
from app.utils.formatting import format_office_address_one_line
from app.views import BaseFormView, FullWidthBaseFormView

logger = logging.getLogger(__name__)


class UpdateVATRegistrationNumberFormView(AdvocateBarristerOfficeMixin, FullWidthBaseFormView):
    template = "update_office/form.html"
    provider_success_url = "main.view_provider_bank_accounts_payment"
    office_success_url = "main.view_office_bank_payment_details"

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update({"office_address": format_office_address_one_line(form.office)})
        return context

    def form_valid(self, form):
        pda = current_app.extensions["pda"]
        data = {"vatRegistrationNumber": form.data.get("vat_registration_number")}
        try:
            pda.patch_office(form.firm.firm_id, form.office.firm_office_code, data)
        except ProviderDataApiError as e:
            logger.error(f"Error {e.__class__.__name__} whilst updating office VAT registration number {e}")
            flash("<b>Failed to update VAT registration number</b>", "error")
            return self.form_invalid(form)
        flash("<b>Updated VAT registration number</b>", "success")
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
            return url_for("main.view_office_bank_payment_details", firm=firm, office=office)
        return url_for("main.view_office_bank_payment_details", firm=firm, office=form.office)

    def form_valid(self, form):
        if not hasattr(form, "firm") or not hasattr(form, "office"):
            abort(400)

        # Update the office with payment method
        pda = current_app.extensions["pda"]
        try:
            updated_office = pda.update_office_payment_method(
                firm_id=form.firm.firm_id,
                office_code=form.office.firm_office_code,
                payment_method=form.data.get("payment_method"),
            )
        except (ValueError, ProviderDataApiError) as e:
            logger.error(f"Error {e.__class__.__name__} whilst updating office payment method {e}")
            flash("<b>Failed to update payment method</b>", "error")
            return self.form_invalid(form)

        session["payment_method"] = form.data.get("payment_method")

        flash("<b>Payment method updated successfully</b>", "success")
        return redirect(self.get_success_url(form, form.firm, updated_office))

    def get(self, context, firm: Firm, office: Office = None, **kwargs):
        if not office:
            abort(404)

        form = self.get_form_class()(firm=firm, office=office)

        # Pre-populate radio with currently saved value when landing on the change page
        if getattr(office, "payment_method", None):
            form.payment_method.data = office.payment_method

        context = self.get_context_data(form, **kwargs)
        context.update({"office_address": format_office_address_one_line(office)})

        return render_template(self.template, **context)

    def post(self, firm: Firm, office: Office = None, *args, **kwargs) -> Response | str:
        if not office:
            abort(404)

        form = self.get_form_class()(firm=firm, office=office)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class OfficeActiveStatusFormView(BaseFormView):
    """Form view for the office active status form"""

    def get_success_url(self, form, firm, office):
        return url_for("main.view_office", firm=firm, office=office)

    def form_valid(self, form):
        if not hasattr(form, "firm") or not hasattr(form, "office"):
            abort(400)

        office_active_status = form.data.get("active_status")
        office = form.office
        current_status = "inactive" if office.inactive_date else "active"
        if office_active_status == current_status:
            flash("<b>Office active status unchanged</b>", "message")
            return redirect(self.get_success_url(form, form.firm, form.office))

        inactive_date = None
        hold_payments = None
        hold_reason = None
        if office_active_status == "inactive":
            inactive_date = datetime.date.today().strftime("%Y-%m-%d")
            hold_payments = "Y"
            hold_reason = "Office made inactive"
        data = {
            Office.model_fields["inactive_date"].alias: inactive_date,
            Office.model_fields["hold_all_payments_flag"].alias: hold_payments,
            Office.model_fields["hold_reason"].alias: hold_reason,
        }

        pda = current_app.extensions["pda"]
        try:
            pda.patch_office(firm_id=form.firm.firm_id, office_code=form.office.firm_office_code, fields_to_update=data)
        except ProviderDataApiError as e:
            logger.error(f"Error {e.__class__.__name__} whilst updating office active status {e}")
            flash("<b>Failed to update office active status</b>", "error")
            return self.form_invalid(form)

        flash(f"<b>Office marked as {office_active_status}</b>", "success")
        return redirect(self.get_success_url(form, form.firm, form.office))

    def get(self, context, firm: Firm, office: Office, **kwargs):
        active_status = "active"
        if getattr(office, "inactive_date", None):
            active_status = "inactive"

        form = self.get_form_class()(firm=firm, office=office, active_status=active_status)

        context = self.get_context_data(form, **kwargs)
        context.update({"office_address": format_office_address_one_line(office)})
        context.update({"cancel_url": url_for("main.view_office", firm=firm, office=office)})

        return render_template(self.template, **context)

    def post(self, firm: Firm, office: Office, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm, office=office)
        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class SearchBankAccountFormView(AdvocateBarristerOfficeMixin, BaseFormView):
    """Form view for to search for bank accounts"""

    template = "update_office/search-bank-account.html"
    provider_success_url = "main.view_provider_bank_accounts_payment"
    office_success_url = "main.view_office_bank_payment_details"

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        add_new_bank_account_url = firm_office_url_for(
            "main.add_office_bank_account", firm=form.firm, office=form.office
        )
        context.update(
            {
                "office_address": format_office_address_one_line(form.office),
                "add_new_bank_account_url": add_new_bank_account_url,
            }
        )
        return context

    def form_valid(self, form: BaseForm, **kwargs) -> str:
        pda = current_app.extensions["pda"]
        pda.assign_bank_account_to_office(form.firm.firm_id, form.office.firm_office_code, form.bank_account.data)
        return super().form_valid(form, **kwargs)

    def get(self, firm, office: Office, context, **kwargs):
        # Display all bank accounts by default
        default_search_term = ""
        if firm.is_advocate or firm.is_barrister:
            # Display no results by default for advocates and barristers
            default_search_term = None
        search_term = request.args.get("search", default_search_term)
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


class ChangeOfficeContactDetailsFormView(BaseFormView):
    def get_success_url(self, form) -> str:
        return url_for("main.view_office_contact", firm=form.firm, office=form.office)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update({"office_address": format_office_address_one_line(form.office)})
        return context

    def get(self, context, firm: Firm, office: Office, **kwargs):
        form = self.get_form_class()(firm=firm, office=office, **office.to_internal_dict())
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def form_valid(self, form, **kwargs):
        pda = current_app.extensions["pda"]
        data = {}
        for field_name, field_value in form.data.items():
            model_field = Office.model_fields.get(field_name)
            if model_field:
                alias = model_field.alias if model_field.alias else field_name
                data[alias] = field_value

        try:
            pda.update_office_contact_details(form.firm.firm_id, form.office.firm_office_code, data)
        except ProviderDataApiError as e:
            logger.error(
                f"Error {e.__class__.__name__} whilst updating office contact details for Firm id: {form.firm.firm_id}, Office code: {form.office.firm_office_code} {e}"
            )
            form.form_errors = getattr(form, "form_errors", [])
            form.form_errors.append("We couldn’t update the office contact details. Try again later.")
            return self.form_invalid(form)

        flash("Office contact details successfully updated", category="success")
        return super().form_valid(form, **kwargs)

    def post(self, firm: Firm, office: Office, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm, office=office)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class AddBankAccountFormView(AdvocateBarristerOfficeMixin, BaseFormView):
    provider_success_url = "main.view_provider_bank_accounts_payment"
    office_success_url = "main.view_office_bank_payment_details"

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form)
        context.update(
            {
                "office_address": format_office_address_one_line(form.office),
                "grid_column_class": "govuk-grid-column-full",
            }
        )
        return context

    def form_valid(self, form):
        bank_account = BankAccount(
            **{
                "sortCode": form.sort_code.data,
                "accountNumber": form.account_number.data,
                "bankAccountName": form.bank_account_name.data,
                "vendorSiteId": form.office.firm_office_id,
                "startDate": datetime.date.today(),
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


class ChangeContractManagerFormView(BaseFormView):
    """Form view to change contract manager on an Office"""

    template = "add_provider/assign-contract-manager.html"
    success_endpoint = "main.create_provider"

    def get_success_url(self, firm, office: Office) -> str:
        return url_for("main.view_office", firm=firm.firm_id, office=office.firm_office_code)

    def change_contract_manager(self, contract_manager: str, firm, office=None):
        pda = current_app.extensions.get("pda")
        if not pda:
            raise RuntimeError("Provider Data API not initialized")

        change_fields = {"contractManager": contract_manager}
        try:
            pda.patch_office(firm.firm_id, office.firm_office_code, change_fields)
        except ProviderDataApiError as e:
            logger.error(f"{e.__class__.__name__} whilst changing contract manager on firm {firm} office {office}: {e}")
            return False
        return True

    def form_valid(self, form) -> Response:
        contract_manager = form.data.get("contract_manager")
        if self.change_contract_manager(contract_manager, form.firm, form.office):
            # Flash success
            flash(
                f"<b>Contract manager for {form.office.firm_office_code} changed to {contract_manager}</b>",
                category="success",
            )
        else:
            flash("Unable to change contract manager", category="error")

        return redirect(self.get_success_url(form.firm, form.office))

    def skip_form(self, form) -> Response:
        # Set contract manager to be default
        contract_manager = DEFAULT_CONTRACT_MANAGER_NAME
        self.change_contract_manager(contract_manager, form.firm, form.office)
        return redirect(self.get_success_url(form.firm, form.office))

    @staticmethod
    def get_valid_firm_or_abort(firm):
        if not firm:
            abort(400)

    def get(self, firm, context, office: Office, **kwargs) -> str:
        self.get_valid_firm_or_abort(firm)

        # By default (new offices), pre-select the contract manager from the head office...
        pda = current_app.extensions.get("pda")
        if not pda:
            raise RuntimeError("Provider Data API not initialized")
        head_office = pda.get_head_office(firm.firm_id)
        head_contract_manager = head_office.contract_manager
        selected_contract_manager = head_contract_manager

        # ...but if we're changing an existing office contract manager, pre-select that instead.
        office_contract_manager = office.contract_manager
        if office_contract_manager not in STATUS_CONTRACT_MANAGER_NAMES:
            selected_contract_manager = office_contract_manager

        # If we have a status workaround manager, they will not be in the list to pre-select.
        if selected_contract_manager in STATUS_CONTRACT_MANAGER_NAMES:
            selected_contract_manager = None

        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(
            firm, office, search_term=search_term, page=page, selected_value=selected_contract_manager
        )

        if search_term:
            form.search.validate(form)

        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def post(self, firm, context, office: Office | None = None, **kwargs) -> Response | str:
        self.get_valid_firm_or_abort(firm)

        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(firm, office, search_term=search_term, page=page)

        if form.skip.data:
            return self.skip_form(form)
        if form.validate_on_submit():
            return self.form_valid(form)
        return self.form_invalid(form, **kwargs)
