from wtforms import Form


def has_page_heading(form: Form) -> bool:
    """
    Check if any field in the form has a widget configured as a page heading.

    Args:
        form: WTForms form instance

    Returns:
        True if any field uses PageHeadingMixin, False otherwise
    """
    for field in form:
        if field.type not in ["CSRFToken", "HiddenField"]:
            widget = field.widget
            # Check if widget has PageHeadingMixin by looking for heading_size attribute
            if hasattr(widget, "heading_size"):
                return True
    return False


def register_template_filters(app):
    """Register all custom template filters with the Flask app."""
    app.template_filter("has_page_heading")(has_page_heading)
