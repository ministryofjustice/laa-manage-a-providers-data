from typing import Optional, Type

from flask import Blueprint

from ..forms import BaseForm
from ..views import BaseFormView


def register_form_view(
    form_class: Type[BaseForm], view_class: Optional[Type[BaseFormView]] = None, blueprint: Optional[Blueprint] = None
) -> None:
    """Register a view class for a form with GET and POST methods."""
    if blueprint is None:
        from app.main import bp

        blueprint = bp

    if view_class is None:
        view_class = BaseFormView

    if form_class is not None and hasattr(form_class, "template"):
        view_class.template = form_class.template

    route_name = form_class.url.lower().replace("-", "_")

    # Register the view with the blueprint
    blueprint.add_url_rule(
        f"/{form_class.url}",
        view_func=view_class.as_view(f"{route_name}", form_class=form_class),
        methods=["GET", "POST"],
    )
