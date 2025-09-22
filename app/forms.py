from flask_wtf import FlaskForm


class BaseForm(FlaskForm):
    template: str = "form.html"
    title: str = "Form Title"  # Supports line breaks with "\n"
    url: str = "example-form"
    caption: str | None = None  # Optional caption text that will render above the form title
    description: str | None = None  # Optional description text that will render under the form title
    submit_button_text: str = "Continue"  # Should be "Submit" on final page before creating a new entity.
