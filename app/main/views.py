from flask import session

from app.views import BaseFormView


class AddProviderFormView(BaseFormView):
    """Form view for the add provider"""

    def form_valid(self, form):
        session["provider_name"] = form.data.get("provider_name")
        session["provider_type"] = form.data.get("provider_type")

        # Call parent method for redirect
        return super().form_valid(form)

