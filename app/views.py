from typing import Any

from flask import Response, current_app, redirect, render_template, url_for
from flask.views import MethodView
from pydantic import BaseModel

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

    def get_form_instance(self, *args, **kwargs) -> BaseForm:
        return self.get_form_class()()

    def get(self, *args, **kwargs) -> str:
        form = self.get_form_instance(*args, **kwargs)
        return render_template(self.get_template(), **self.get_context_data(form, **kwargs))

    def post(self, *args, **kwargs) -> Response | str:
        form = self.get_form_instance(**kwargs)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)

    def get_api(self) -> ProviderDataApi:
        return current_app.extensions["pda"]

    def form_data_to_model_data(self, form: BaseForm, model_class: type[BaseModel]) -> dict:
        """
        Transform a form's submitted data into a dictionary compatible with a Pydantic model.

        This function iterates over `form.data` and keeps only the fields that exist on the
        target Pydantic model. If a model field defines an alias, the alias is used as the
        output key; otherwise, the original field name is used.

        Args:
            form (BaseForm): The form instance containing user-submitted data.
            model_class (type[BaseModel]): The Pydantic model class whose fields (and aliases)
                determine which form fields should be included and how they should be named.

        Returns:
            dict: A dictionary mapping model field aliases (or names) to the corresponding
                values from the form. Fields that do not exist on the model are omitted.
        """

        data = {}
        for field_name, field_value in form.data.items():
            model_field = model_class.model_fields.get(field_name)
            if model_field:
                alias = model_field.alias if model_field.alias else field_name
                data[alias] = field_value
        return data


class FullWidthBaseFormView(BaseFormView):
    """Used to render full width form pages by setting the grid_column_class to 'govuk-grid-column-full'"""

    def get_context_data(self, form: BaseForm, context=None, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(form=form, context=context, **kwargs)
        context.update({"grid_column_class": "govuk-grid-column-full"})
        return context
