from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from ..forms import BaseForm


class ExampleForm(BaseForm):
    template = "example-form.html"
    title = "Your full name"
    url = "example-form"

    full_name = StringField(
        title,
        widget=GovTextInput(),
        validators=[
            InputRequired(message="Enter your name"),
        ],
    )