from typing import Any

from flask import Response, redirect, render_template, url_for
from flask.views import MethodView
from flask_wtf import FlaskForm

from app.forms import BaseForm


class BaseFormView(MethodView):
    """Base view class for handling forms with GET and POST methods."""

    form_class: type[FlaskForm] = BaseForm
    template: str = "form.html"
    success_endpoint: str = "main.index"

    def __init__(
        self,
        form_class: type[FlaskForm] | None = None,
        template: str | None = None,
        success_endpoint: str | None = None,
    ) -> None:
        if form_class is not None:
            self.form_class = form_class
        if template is not None:
            self.template = template
        if success_endpoint is not None:
            self.success_endpoint = success_endpoint

    def get_form_class(self) -> type[FlaskForm]:
        return self.form_class

    def get_template(self) -> str:
        return self.template

    def get_success_url(self, form: BaseForm | None = None) -> str:
        if self.success_endpoint:
            return url_for(self.success_endpoint)
        return url_for("main.index")

    def get_context_data(self, form: FlaskForm) -> dict[str, Any]:
        context = {"form": form, "title": getattr(self.get_form_class(), "title", "Form")}
        return context

    def form_valid(self, form: FlaskForm) -> Response:
        return redirect(self.get_success_url(form))

    def form_invalid(self, form: FlaskForm) -> str:
        return render_template(self.get_template(), **self.get_context_data(form))

    def get(self) -> str:
        form = self.get_form_class()()
        return render_template(self.get_template(), **self.get_context_data(form))

    def post(self) -> Response | str:
        form = self.get_form_class()()

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
