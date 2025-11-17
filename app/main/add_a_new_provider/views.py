from typing import Any

from flask import Response, abort, current_app, redirect, render_template, request, session, url_for

from app.constants import DEFAULT_CONTRACT_MANAGER_NAME, PARENT_FIRM_TYPE_CHOICES
from app.forms import BaseForm
from app.main.utils import change_liaison_manager, create_advocate_from_form_data, create_barrister_from_form_data
from app.models import Contact, Firm
from app.views import BaseFormView, FullWidthBaseFormView


class AddProviderFormView(BaseFormView):
    """Form view for the add provider"""

    template = "templates/form.html"

    # Only 'parent' firm choices
    next_step_mapping = {
        "Chambers": "main.add_contact_details",
        "Legal Services Provider": "main.additional_details_legal_services_provider",
    }

    def form_valid(self, form):
        session["new_provider"] = {}
        session["new_provider"].update(
            {
                "firm_name": form.data.get("provider_name"),
                "firm_type": form.data.get("provider_type"),
            }
        )

        # Call parent method for redirect
        return super().form_valid(form)

    def get_success_url(self, form):
        provider_type = form.data.get("provider_type")
        next_page = self.next_step_mapping.get(provider_type)
        return url_for(next_page)


class LspDetailsFormView(BaseFormView):
    """Form view for the Legal services provider details"""

    success_endpoint = "main.add_contact_details"

    def form_valid(self, form):
        session["new_provider"].update(
            {
                "constitutional_status": form.data.get("constitutional_status"),
                "company_house_number": form.data.get("companies_house_number"),
            }
        )

        indemnity_date = form.data.get("indemnity_received_date")
        if indemnity_date:
            session["new_provider"].update({"indemnity_received_date": indemnity_date.isoformat()})

        return super().form_valid(form)


class AdvocateDetailsFormView(BaseFormView):
    success_endpoint = "main.create_provider"

    def form_valid(self, form):
        session["new_provider"].update(
            {
                "solicitor_advocate": form.data.get("solicitor_advocate"),
                "advocate_level": form.data.get("advocate_level"),
                "bar_council_roll": form.data.get("bar_council_roll_number"),
            }
        )
        return super().form_valid(form)


class HeadOfficeContactDetailsFormView(BaseFormView):
    """Form view for the Head office contact details page"""

    next_step_mapping = {
        "Chambers": "main.add_liaison_manager",
        "Legal Services Provider": "main.add_vat_number",
    }

    def get_success_url(self, form):
        return url_for(self.next_step_mapping.get(form.firm.firm_type, "main.create_provider"))

    def form_valid(self, form):
        session["new_head_office"] = {
            "is_head_office": True,
            "head_office": "N/A",
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
            "payment_method": "Electronic",
        }

        return super().form_valid(form)

    @staticmethod
    def get_valid_firm_or_abort():
        if not session.get("new_provider"):
            abort(400)

        valid_parent_types = [choice[0] for choice in PARENT_FIRM_TYPE_CHOICES]
        if session.get("new_provider").get("firm_type") not in valid_parent_types:
            abort(400)

    def get(self, context, **kwargs):
        self.get_valid_firm_or_abort()

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, *args, **kwargs) -> Response | str:
        self.get_valid_firm_or_abort()

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class VATRegistrationFormView(FullWidthBaseFormView):
    success_endpoint = "main.add_bank_account"

    def form_valid(self, form):
        session["new_head_office"].update(
            {
                "vat_registration_number": form.data.get("vat_registration_number"),
            }
        )

        return super().form_valid(form)

    @staticmethod
    def get_valid_firm_or_abort():
        if not session.get("new_provider"):
            abort(400)

        if session.get("new_provider").get("firm_type") != "Legal Services Provider":
            abort(400)

    def get(self, context, **kwargs):
        self.get_valid_firm_or_abort()

        # Check if the new head office data exists in the session
        if not session.get("new_head_office"):
            abort(400)

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, *args, **kwargs) -> Response | str:
        self.get_valid_firm_or_abort()

        # Check if the new head office data exists in the session
        if not session.get("new_head_office"):
            abort(400)

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class BankAccountFormView(FullWidthBaseFormView):
    success_endpoint = "main.add_liaison_manager"

    def form_valid(self, form):
        # Set payment method for the main submit button flow
        session["new_head_office"]["payment_method"] = "Electronic"
        session["new_head_office_bank_account"] = {
            "bank_account_name": form.data.get("bank_account_name"),
            "sort_code": form.data.get("sort_code"),
            "account_number": form.data.get("account_number"),
        }

        return super().form_valid(form)

    @staticmethod
    def get_valid_firm_or_abort():
        if not session.get("new_provider"):
            abort(400)

        if session.get("new_provider").get("firm_type") != "Legal Services Provider":
            abort(400)

    def get(self, context, **kwargs):
        self.get_valid_firm_or_abort()

        # Check if the new head office data exists in the session
        if not session.get("new_head_office"):
            abort(400)

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, *args, **kwargs) -> Response | str:
        self.get_valid_firm_or_abort()

        # Check if the new head office data exists in the session
        if not session.get("new_head_office"):
            abort(400)

        # Check if skip button was clicked (before validation)
        if request.form.get("skip_button"):
            # Skip storing bank account data set payment-method to "Cheque" and go to next step
            session["new_head_office"]["payment_method"] = "Cheque"
            return redirect(url_for(self.success_endpoint))

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class LiaisonManagerFormView(FullWidthBaseFormView):
    next_step_mapping = {
        "Chambers": "main.create_provider",
        "Legal Services Provider": "main.assign_contract_manager",
    }

    def get_success_url(self, form):
        provider_type = session.get("new_provider", {}).get("firm_type")
        return url_for(self.next_step_mapping.get(provider_type, "main.create_provider"))

    def form_valid(self, form):
        session["new_liaison_manager"] = {
            "first_name": form.data.get("first_name"),
            "last_name": form.data.get("last_name"),
            "email_address": form.data.get("email_address"),
            "telephone_number": form.data.get("telephone_number"),
            "website": form.data.get("website"),
            "job_title": "Liaison manager",  # All contacts are liaison managers in MAPD
            "primary": "Y",  # We are adding a new head office so this will be the primary contact
        }

        return super().form_valid(form)

    @staticmethod
    def get_valid_firm_or_abort():
        if not session.get("new_provider"):
            abort(400)

        valid_parent_types = [choice[0] for choice in PARENT_FIRM_TYPE_CHOICES]
        if session.get("new_provider").get("firm_type") not in valid_parent_types:
            abort(400)

    def get(self, context, **kwargs):
        self.get_valid_firm_or_abort()

        # Check if the new head office data exists in the session
        if not session.get("new_head_office"):
            abort(400)

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, *args, **kwargs) -> Response | str:
        self.get_valid_firm_or_abort()

        # Check if the new head office data exists in the session
        if not session.get("new_head_office"):
            abort(400)

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class AssignContractManagerFormView(BaseFormView):
    """Form view for the assign contract manager form"""

    template = "add_provider/assign-contract-manager.html"
    success_endpoint = "main.create_provider"

    def form_valid(self, form):
        session.get("new_head_office").update({"contract_manager": form.data.get("contract_manager")})
        return super().form_valid(form)

    def skip_form(self, form):
        session.get("new_head_office").update({"contract_manager": DEFAULT_CONTRACT_MANAGER_NAME})
        return super().form_valid(form)

    @staticmethod
    def get_valid_firm_or_abort():
        if not session.get("new_provider"):
            abort(400)

        if session.get("new_provider").get("firm_type") != "Legal Services Provider":
            abort(400)

    def get(self, context, **kwargs):
        self.get_valid_firm_or_abort()

        # Check if the new head office data exists in the session
        if not session.get("new_head_office"):
            abort(400)

        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(search_term=search_term, page=page)

        if search_term:
            form.search.validate(form)

        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def post(self, context, **kwargs) -> Response | str:
        self.get_valid_firm_or_abort()

        # Check if the new head office data exists in the session
        if not session.get("new_head_office"):
            abort(400)

        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(search_term=search_term, page=page)

        if form.skip.data:
            return self.skip_form(form)
        elif form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class AddBarristerDetailsFormView(BaseFormView):
    """Form view for the add barrister form"""

    def get_success_url(self, form, firm):
        return url_for("main.add_barrister_check_form", firm=firm)

    def get_chambers_or_abort(self, firm):
        if not firm or firm.firm_type != "Chambers":
            abort(404)

    def form_valid(self, form, firm):
        session["new_barrister"] = dict(
            barrister_name=form.data.get("barrister_name"),
            barrister_level=form.data.get("barrister_level"),
            bar_council_roll_number=form.data.get("bar_council_roll_number"),
            parent_firm_id=firm.firm_id,
        )
        return redirect(self.get_success_url(form, firm))

    def get(self, context, firm, **kwargs):
        self.get_chambers_or_abort(firm)
        form = self.get_form_class()(firm=firm)
        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def post(self, context, firm, **kwargs) -> Response | str:
        self.get_chambers_or_abort(firm)
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form, firm)
        else:
            return self.form_invalid(form, **kwargs)


class AddAdvocateDetailsFormView(BaseFormView):
    """Form view for the add advocate form"""

    def get_success_url(self, form, firm):
        return url_for("main.add_advocate_check_form", firm=firm)

    def get_chambers_or_abort(self, firm):
        if not firm or firm.firm_type != "Chambers":
            abort(404)

    def form_valid(self, form, firm):
        session["new_advocate"] = dict(
            advocate_name=form.data.get("advocate_name"),
            advocate_level=form.data.get("advocate_level"),
            sra_roll_number=form.data.get("sra_roll_number"),
            parent_firm_id=firm.firm_id,
        )
        return redirect(self.get_success_url(form, firm))

    def get(self, context, firm, **kwargs):
        self.get_chambers_or_abort(firm)
        form = self.get_form_class()(firm=firm)
        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def post(self, context, firm, **kwargs) -> Response | str:
        self.get_chambers_or_abort(firm)
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form, firm)
        else:
            return self.form_invalid(form, **kwargs)


class AddAdvocateBarristersCheckFormView(BaseFormView):
    def __init__(self, model_type: str, *args, **kwargs):
        self.model_type = model_type.lower()
        super().__init__(*args, **kwargs)

    def get_context_data(self, form: BaseForm, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form, **kwargs)
        from app.main.views import get_contact_tables

        pda = current_app.extensions["pda"]
        head_office = pda.get_head_office(form.firm.firm_id)
        context["contact_tables"] = get_contact_tables(
            firm=form.firm, head_office=head_office, include_change_link=False
        )

        return context

    def create_model(self):
        if self.model_type == "barrister":
            firm = create_barrister_from_form_data(**session["new_barrister"])
            del session["new_barrister"]
        else:
            firm = create_advocate_from_form_data(**session["new_advocate"])
            del session["new_advocate"]
        return firm

    def form_valid(self, form: BaseForm, firm: Firm):
        if form.same_liaison_manager_as_chambers.data.lower() == "yes":
            new_firm = self.create_model()
            return redirect(url_for("main.view_provider", firm=new_firm))

        return redirect(url_for(f"main.add_{self.model_type}_liaison_manager_form", firm=firm))

    def dispatch_request(self, **kwargs):
        key = "new_barrister" if self.model_type == "barrister" else "new_advocate"
        if not session.get(key):
            return redirect(url_for(f"main.add_{self.model_type}_details_form", firm=kwargs["firm"]))

        firm: Firm = kwargs.get("firm")
        if (not firm) or (not firm.is_chambers) or (firm.firm_id != session[key]["parent_firm_id"]):
            abort(404)

        return super().dispatch_request(**kwargs)

    def get(self, context, firm, **kwargs):
        form = self.get_form_class()(firm=firm, model_type=self.model_type)
        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def post(self, context, firm, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm, model_type=self.model_type)

        if form.validate_on_submit():
            return self.form_valid(form, firm)
        else:
            return self.form_invalid(form, **kwargs)


class AddAdvocateBarristersLiaisonManagerFormView(AddAdvocateBarristersCheckFormView):
    def get_success_url(self, firm):
        return url_for("main.view_provider", firm=firm)

    def form_valid(self, form, firm):
        new_firm = self.create_model()

        liaison_manager = Contact(
            firstName=form.data.get("first_name"),
            lastName=form.data.get("last_name"),
            emailAddress=form.data.get("email_address"),
            telephoneNumber=form.data.get("telephone_number"),
            website=form.data.get("website"),
            jobTitle="Liaison manager",  # All contacts are liaison managers in MAPD
            primary="Y",  # We are adding a new head office so this will be the primary contact
        )
        change_liaison_manager(contact=liaison_manager, firm_id=new_firm.firm_id)
        return redirect(self.get_success_url(new_firm))
