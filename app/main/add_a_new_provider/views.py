from flask import Response, abort, redirect, render_template, request, session, url_for

from app.constants import PARENT_FIRM_TYPE_CHOICES
from app.main.add_a_new_provider import AssignChambersForm
from app.models import Firm
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


class AssignChambersFormView(BaseFormView):
    """Form view for the assign to a chambers form"""

    template = "add_provider/assign-chambers.html"
    success_endpoint = "main.create_provider"

    next_step_mapping = {
        "Barrister": "main.create_provider",
        "Advocate": "main.advocate_details",
    }

    def get_success_url(self, form):
        provider_type = session.get("new_provider", {}).get("firm_type")
        next_page = self.next_step_mapping.get(provider_type, "main.create_provider")
        return url_for(next_page)

    def form_valid(self, form):
        session.get("new_provider", {}).update({"parent_firm_id": form.data.get("provider")})
        return redirect(self.get_success_url(form))

    def get(self, context):
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form: AssignChambersForm = self.get_form_class()(search_term=search_term, page=page)

        if search_term:
            form.search.validate(form)

        return render_template(self.get_template(), **self.get_context_data(form, context))

    def post(self, context) -> Response | str:
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(search_term=search_term, page=page)
        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


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
            # Skip storing bank account data and go to next step
            return redirect(url_for(self.success_endpoint))

        firm = Firm(**session.get("new_provider"))
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)


class LiaisonManagerFormView(FullWidthBaseFormView):
    success_endpoint = "main.create_provider"

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
