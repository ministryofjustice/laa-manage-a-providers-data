from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired
from ..forms import BaseForm
from ..widgets import PageHeadingInput


class ExampleForm(BaseForm):
    title = "Form Title"
    url = "example-form"

    full_name = StringField(
        "Your full name",
        widget=PageHeadingInput(hint="This should include any middle names."),
        validators=[
            InputRequired(message="Enter your name"),
        ],
    )