from flask import redirect, render_template, session, url_for

from app.views import BaseFormView

from .forms import AddProviderForm


class AddProviderFormView(BaseFormView):
    """Form view for the add provider"""

    template = "templates/form.html"

    def form_valid(self, form):
        session["provider_name"] = form.data.get("provider_name")
        session["provider_type"] = form.data.get("provider_type")

        # Call parent method for redirect
        return super().form_valid(form)

    def dispatch_request(self, context):
        form = AddProviderForm()
        if form.validate_on_submit():
            provider_type = form.data.get("provider_type")
            next_page = form.next_step_mapping.get(provider_type)
            return redirect(url_for(next_page))
        return render_template(self.template, form=form)


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
