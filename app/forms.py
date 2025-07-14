from flask_wtf import FlaskForm


class BaseForm(FlaskForm):
    template: str = "form.html"
    title: str = "Form Title"
    url: str = "example-form"
