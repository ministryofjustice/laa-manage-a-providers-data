from flask import Response, redirect, render_template, request, session, url_for

from app.views import BaseFormView


class AddProviderFormView(BaseFormView):
    """Form view for the add provider"""

    template = "templates/form.html"

    next_step_mapping = {
        "barrister": "main.assign_parent_provider",
        "advocate": "main.assign_parent_provider",
        "chambers": "main.add_provider/chambers_details",
        "lsp": "main.add_provider/lsp_details",
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
        # Call parent method for redirect
        return super().form_valid(form)


class ChambersDetailsFormView(BaseFormView):
    """Form view for the Chambers details"""

    def form_valid(self, form):
        # Call parent method for redirect
        return super().form_valid(form)


class ParentProviderFormView(BaseFormView):
    """Form view for the Assign to parent provider"""

    template = "add_provider/assign-parent-provider.html"
    success_url = "main.view_provider"

    def form_valid(self, form):
        session["parent_provider_id"] = form.data.get("provider")
        return redirect(url_for(self.success_url))

    def get(self):
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(search_term=search_term, page=page)
        return render_template(self.get_template(), **self.get_context_data(form))

    def post(self) -> Response | str:
        search_term = request.args.get("search", "").strip()
        page = int(request.args.get("page", 1))
        form = self.get_form_class()(search_term=search_term, page=page)
        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
