from flask import current_app
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, ValidationError

from ..forms import BaseForm
from ..widgets import GovPasswordInput


def check_known_password(_, field):
    expected_password = current_app.config.get("PASSWORD")

    if field.data != expected_password:
        raise ValidationError("Incorrect password")


class AuthenticationForm(BaseForm):
    title = "Authenticate"
    url = "authenticate"

    full_name = StringField(
        "To access this page you need a password",
        widget=GovPasswordInput(hint="Ask for the password in #laa-manage-a-providers-data"),
        validators=[
            InputRequired(message="Enter your name"),
            check_known_password,
        ],
    )
