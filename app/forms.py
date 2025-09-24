from flask_wtf import FlaskForm


class BaseForm(FlaskForm):
    template: str = "form.html"
    title: str = "Form Title"  # Supports line breaks with "\n"
    url: str = "example-form"
