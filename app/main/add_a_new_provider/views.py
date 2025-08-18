from flask import Response, redirect, render_template, request, session, url_for

from app.main.add_a_new_provider import AssignChambersForm
from app.views import BaseFormView


class AddProviderFormView(BaseFormView):
    """Form view for the add provider"""

    template = "templates/form.html"

    next_step_mapping = {
        "Barrister": "main.assign_chambers",
        "Advocate": "main.assign_chambers",
        "Chambers": "main.chambers_details",
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

    success_endpoint = "main.view_provider"

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
    success_endpoint = "main.view_provider"

    def form_valid(self, form):
        session["new_provider"].update(
            {
                "solicitor_advocate": form.data.get("solicitor_advocate"),
                "advocate_level": form.data.get("advocate_level"),
                "bar_council_roll": form.data.get("bar_council_roll_number"),
            }
        )
        return super().form_valid(form)


class ChambersDetailsFormView(BaseFormView):
    """Form view for the Chambers details"""

    success_endpoint = "main.view_provider"

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
    success_endpoint = "main.view_provider"

    next_step_mapping = {
        "Barrister": "main.view_provider",
        "Advocate": "main.advocate_details",
    }

    def get_success_url(self, form):
        provider_type = session.get("new_provider", {}).get("firm_type")
        next_page = self.next_step_mapping.get(provider_type, "main.view_provider")
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
