from flask import session, url_for

from app.views import BaseFormView


class AddProviderFormView(BaseFormView):
    """Form view for the add provider"""

    template = "templates/form.html"

    next_step_mapping = {
        "barrister": "main.add_provider/assign_parent_provider",
        "advocate": "main.add_provider/assign_parent_provider",
        "chambers": "main.add_provider/chambers_details",
        "lsp": "main.additional_details_legal_services_provider",
    }

    def form_valid(self, form):
        session["provider_name"] = form.data.get("provider_name")
        session["provider_type"] = form.data.get("provider_type")

        # Call parent method for redirect
        return super().form_valid(form)

    def get_success_url(self, form):
        provider_type = form.data.get("provider_type")
        next_page = self.next_step_mapping.get(provider_type)
        return url_for(next_page)


class LspDetailsFormView(BaseFormView):
    """Form view for the Legal services provider details"""

    def form_valid(self, form):
        session["constitutional_status"] = form.data.get("constitutional_status")
        session["non_profit_organisation"] = form.data.get("non_profit_organisation")
        session["high_risk_supplier"] = form.data.get("high_risk_supplier")
        session["companies_house_number"] = form.data.get("companies_house_number")

        indemnity_date = form.data.get("indemnity_received_date")
        if indemnity_date:
            session["indemnity_received_date"] = indemnity_date.isoformat()

        return super().form_valid(form)


class ChambersDetailsFormView(BaseFormView):
    """Form view for the Chambers details"""

    pass


class ParentProviderFormView(BaseFormView):
    """Form view for the Assign to parent provider"""

    pass
