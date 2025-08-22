from flask import Response, abort, render_template, session, url_for

from app.forms import BaseForm
from app.models import Firm
from app.views import BaseFormView


class AddOfficeFormView(BaseFormView):
    """Form view for the Add a new office page"""

    def get_success_url(self, form: BaseForm | None = None) -> str:
        if not form or not hasattr(form, "firm"):
            abort(404)

        return url_for("main.view_provider_with_id", firm=form.firm)

    def form_valid(self, form):
        session["new_office"] = {
            "office_name": form.data.get("office_name"),
            "is_head_office": form.data.get("is_head_office"),
        }

        return super().form_valid(form)

    def get(self, context, firm: Firm, **kwargs):
        form = self.get_form_class()(firm=firm)

        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm: Firm, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
