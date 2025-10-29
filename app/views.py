from typing import Any

from flask import Response, current_app, redirect, render_template, url_for
from flask.views import MethodView

from app.forms import BaseForm
from app.pda.api import ProviderDataApi


class BaseFormView(MethodView):
    """Base view class for handling forms with GET and POST methods."""

    form_class: type[BaseForm] = BaseForm
    template: str = "form.html"
    success_endpoint: str = "main.index"

    def __init__(
        self,
        form_class: type[BaseForm] | None = None,
        template: str | None = None,
        success_endpoint: str | None = None,
    ) -> None:
        if form_class is not None:
            self.form_class = form_class
        if template is not None:
            self.template = template
        if success_endpoint is not None:
            self.success_endpoint = success_endpoint

    def get_form_class(self) -> type[BaseForm]:
        return self.form_class

    def get_template(self) -> str:
        return self.template

    def get_success_url(self, form: BaseForm | None = None) -> str:
        if self.success_endpoint:
            return url_for(self.success_endpoint)
        return url_for("main.index")

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        return {
            "form": form,
            "title": getattr(self.get_form_class(), "title", "Form"),
            **(context.get("context", {}) if context else {}),
            **kwargs,
        }

    def form_valid(self, form: BaseForm) -> Response:
        return redirect(self.get_success_url(form))

    def form_invalid(self, form: BaseForm, **kwargs) -> str:
        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def get(self, **kwargs) -> str:
        form = self.get_form_class()()
        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def post(self, *args, **kwargs) -> Response | str:
        form = self.get_form_class()()

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

    def get_api(self) -> ProviderDataApi:
        return current_app.extensions["pda"]


class FullWidthBaseFormView(BaseFormView):
    """Used to render full width form pages by setting the grid_column_class to 'govuk-grid-column-full'"""

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form=form, context=context, **kwargs)
        context.update({"grid_column_class": "govuk-grid-column-full"})
        return context
