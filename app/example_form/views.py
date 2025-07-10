from flask import session

from app.views import BaseFormView


class ExampleFormView(BaseFormView):
    """Example of extending BaseFormView for custom form handling."""

    success_endpoint = "example_form.success"  # Override to customize redirect, defaults to "main.index".

    def form_valid(self, form):
        # Add your custom processing here
        # e.g. save to session, send email, etc.
        session["full_name"] = form.data.get("full_name")

        # Call parent method for redirect
        return super().form_valid(form)

    def get_context_data(self, form):
        # Add custom context data to be passed to the template.
        context = super().get_context_data(form)
        context['custom_data'] = 'Your custom data here'
        return context
