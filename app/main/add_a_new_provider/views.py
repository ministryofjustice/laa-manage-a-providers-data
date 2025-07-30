from flask import session

from app.views import BaseFormView


class AddProviderFormView(BaseFormView):
    """Form view for the add provider"""

    def form_valid(self, form):
        session["provider_name"] = form.data.get("provider_name")
        session["provider_type"] = form.data.get("provider_type")

        # Call parent method for redirect
        return super().form_valid(form)
    
class LspDetailsFormView(BaseFormView):
    """Form view for the Legal services provider details"""

    def form_valid(self, form):

        # Call parent method for redirect
        return super().form_valid(form)
    
class ChambersDetailsFormView(BaseFormView):
    """Form view for the Chambers details"""

    def form_valid(self, form):

        # Call parent method for redirect
        return super().form_valid(form)
    
class ParentProviderFormView(BaseFormView):
    """Form view for the Assign to parent provider"""

    def form_valid(self, form):

        # Call parent method for redirect
        return super().form_valid(form)