import datetime
import logging
from typing import Any

from flask import Response, abort, current_app, flash, redirect, render_template, request, url_for

from app.forms import BaseForm
from app.main.modify_provider import AssignChambersForm, ReassignHeadOfficeForm
from app.main.update_office import ChangeOfficeContactDetailsFormView
from app.main.utils import assign_firm_to_a_new_chambers, change_liaison_manager, reassign_head_office
from app.main.views import AdvocateBarristerOfficeMixin, get_main_table
from app.models import Contact, Firm, Office
from app.pda.errors import ProviderDataApiError
from app.views import BaseFormView, FullWidthBaseFormView

logger = logging.getLogger(__name__)


class ChangeLiaisonManagerFormView(FullWidthBaseFormView):
    templates = {
        "Legal Services Provider": "modify_provider/change-liaison-manager-legal-services-provider.html",
        "Chambers": "modify_provider/change-liaison-manager-chambers.html",
        "Advocate": "modify_provider/change-liaison-manager-advocate.html",
        "Barrister": "modify_provider/change-liaison-manager-barrister.html",
        "Office": "modify_provider/change-liaison-manager-legal-services-provider-office.html",
    }

    def get_success_url(self, firm, office: Office | None = None):
        if office:
            return url_for("main.view_office", firm=firm, office=office)
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

        # If the office is not specified, we change liaison manager at the firm level...
        office = None
        if hasattr(form, "office"):
            # ...but if we have a specific office, only change the office liaison manager.
            office = form.office
        change_liaison_manager(new_contact, form.firm.firm_id, office=office)

        return redirect(self.get_success_url(form.firm, office=office))

    def get(self, firm, context, **kwargs):
        form = self.get_form_class()(firm=firm)
        context = self.get_context_data(form, **kwargs)

        # Get the current liaison manager from the head office so we can display a more specific message
        pda = current_app.extensions["pda"]
        try:
            head_office = pda.get_head_office(firm_id=firm.firm_id)
            for contact in pda.get_office_contacts(firm_id=firm.firm_id, office_code=head_office.firm_office_code):
                if contact.job_title == "Liaison manager" and contact.primary == "Y":
                    context.update({"current_liaison_manager_name": f"{contact.first_name} {contact.last_name}"})
                    break
        except ProviderDataApiError as e:
            logger.error(f"Error {e.__class__.__name__} whilst getting liaison manager for {firm.firm_id} {e}")
            context.update({"current_liaison_manager_name": "the current liaison manager"})

        # Different levels of description for the different firm types
        template = self.templates.get(firm.firm_type, self.template)
        if hasattr(form, "office"):
            template = self.templates.get("Office", self.template)

        return render_template(template, **context)

    def post(self, firm, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm, *args, **kwargs)

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

        if form.firm.is_legal_services_provider or form.firm.is_chambers:
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

    def get_form_instance(self, firm: Firm, **kwargs) -> BaseForm:
        status = "inactive" if firm.inactive_date else "active"
        form = self.get_form_class()(status=status, firm=firm)
        return form

    def form_valid(self, form):
        status = form.data.get("status")
        inactive_date = None
        if status == "inactive":
            inactive_date = datetime.date.today().strftime("%Y-%m-%d")
        data = {Firm.model_fields["inactive_date"].alias: inactive_date}

        pda = current_app.extensions["pda"]
        firm = pda.patch_provider_firm(form.firm.firm_id, data)
        if firm:
            flash(f"<b>{form.firm.firm_name} marked as {status}</b>", "success")
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

    def get_form_instance(self, firm: Firm, **kwargs) -> BaseForm:
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(firm=firm, search_term=search_term, page=page)
        if request.method.upper() == "GET" and search_term:
            form.search.validate(form)
        return form

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


class ReassignHeadOfficeFormView(BaseFormView):
    form_class = ReassignHeadOfficeForm

    def get_success_url(self, form: BaseForm | None = None) -> str:
        return url_for("main.view_provider_offices", firm=form.firm)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update({"cancel_url": self.get_success_url(form)})
        return context

    def get_form_instance(self, firm: Firm, **kwargs) -> BaseForm:
        head_office = self.get_api().get_head_office(firm.firm_id)
        default_office = head_office.firm_office_code if head_office else None
        form = self.get_form_class()(firm=firm, office=default_office)

        return form

    def form_valid(self, form: BaseForm):
        new_head_office_code = form.data.get("office")

        if not form.has_changed():
            flash(f"No change made because {new_head_office_code} is already the head office")
            return redirect(self.get_success_url(form))

        try:
            reassign_head_office(form.firm, new_head_office_code)
            flash(f"<b>{form.firm.firm_name} head office reassigned to {new_head_office_code}</b>", category="success")
        except (ValueError, RuntimeError, ProviderDataApiError) as e:
            logger.error(f"{e.__class__.__name__} whilst reassigning head office: {e}")
            flash(
                f"Unable to reassign head office for {form.firm.firm_name} to {new_head_office_code}", category="error"
            )

        return redirect(self.get_success_url(form))


class ChangeLegalServicesProviderNameFormView(BaseFormView):
    success_url = "main.view_provider"

    def get_success_url(self, form):
        return url_for(self.success_url, firm=form.firm)

    def get_form_instance(self, firm: Firm, **kwargs):
        return self.get_form_class()(firm=firm, provider_name=firm.firm_name)

    def form_valid(self, form):
        self.get_api().update_provider_firm_name(form.firm.firm_id, form.provider_name.data)
        flash(f"<b>{form.firm.firm_type.lower().capitalize()} name successfully updated</b>", category="success")
        return super().form_valid(form)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update({"cancel_url": self.get_success_url(form)})
        return context


class ChangeLspDetailsFormView(BaseFormView):
    """Form view for the Legal services provider details"""

    success_endpoint = "main.view_provider"

    def get_success_url(self, form: BaseForm) -> str:
        return url_for("main.view_provider", firm=form.firm)

    def form_valid(self, form):
        data = dict(
            constitutionalStatus=form.data.get("constitutional_status"),
            indemnityReceivedDate=form.data.get("indemnity_received_date"),
            companyHouseNumber=form.data.get("companies_house_number"),
        )
        if data["indemnityReceivedDate"]:
            data["indemnityReceivedDate"] = data["indemnityReceivedDate"].isoformat()

        self.get_api().update_legal_service_provider_details(form.firm.firm_id, data)
        flash("<b>Legal services provider overview successfully updated<b>", category="success")
        return super().form_valid(form)

    def get_form_instance(self, firm: Firm, **kwargs) -> BaseForm:
        indemnity_received_date = firm.indemnity_received_date
        if indemnity_received_date:
            indemnity_received_date = datetime.datetime.strptime(indemnity_received_date, "%Y-%m-%d").date()
        data = dict(
            constitutional_status=firm.constitutional_status,
            indemnity_received_date=indemnity_received_date,
            companies_house_number=firm.company_house_number,
        )
        return self.get_form_class()(firm=firm, **data)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update({"cancel_url": self.get_success_url(form)})
        return context


class BarristerChangeDetailsView(AdvocateBarristerOfficeMixin, BaseFormView):
    provider_success_url = "main.view_provider"

    def form_valid(self, form):
        barrister_details = {
            "firmName": form.data["barrister_name"],
            "advocateLevel": form.data["barrister_level"],
            "barCouncilRoll": form.data["bar_council_roll_number"],
        }
        self.get_api().update_barrister_details(firm_id=form.firm.firm_id, barrister_details=barrister_details)
        flash("Barrister overview updated successfully", category="success")

        return super().form_valid(form)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update({"cancel_url": self.get_success_url(form)})
        return context

    def get_form_instance(self, firm: Firm, office: Office, **kwargs) -> BaseForm:
        return self.get_form_class()(
            firm=firm,
            office=office,
            **{
                "barrister_name": firm.firm_name,
                "barrister_level": firm.advocate_level,
                "bar_council_roll_number": firm.bar_council_roll,
            },
        )


class ChangeChambersDetailsFormView(ChangeOfficeContactDetailsFormView):
    success_message = "Chambers contact details successfully updated"
    error_message = "We couldn’t update the Chambers contact details. Try again later."

    def get_success_url(self, form) -> str:
        return url_for("main.view_provider", firm=form.firm)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context)
        context.update({"cancel_url": self.get_success_url(form)})
        return context

    def dispatch_request(self, firm: Firm, context=None, **kwargs):
        office = self.get_api().get_head_office(firm.firm_id)
        return super().dispatch_request(firm=firm, office=office, context=context, **kwargs)


class ChangeAdvocateDetailsFormView(BaseFormView):
    def get_success_url(self, form):
        return url_for("main.view_provider", firm=form.firm)

    def form_valid(self, form: BaseForm) -> Response:
        data = dict(
            firmName=form.data.get("advocate_name"),
            advocateLevel=form.data.get("advocate_level"),
            barCouncilRoll=form.data.get("sra_roll_number"),
        )
        self.get_api().update_advocate_details(form.firm.firm_id, data)
        flash("Advocate overview successfully updated", category="success")
        return super().form_valid(form)

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, context, **kwargs)
        context.update({"cancel_url": self.get_success_url(form)})
        return context

    def get_form_instance(self, firm: Firm) -> BaseForm:
        details = dict(
            advocate_name=firm.firm_name,
            advocate_level=firm.advocate_level,
            sra_roll_number=firm.bar_council_roll,
        )
        return self.get_form_class()(firm=firm, **details)

    def get(self, firm: Firm, context=None, **kwargs):
        form = self.get_form_instance(firm)
        return render_template(self.get_template(), **self.get_context_data(form, context))

    def post(self, firm: Firm, context) -> Response | str:
        form = self.get_form_instance(firm)
        if form.validate_on_submit():
            return self.form_valid(form)
        return self.form_invalid(form)
