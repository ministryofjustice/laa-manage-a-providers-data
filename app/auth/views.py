"""Temporary auth logic, to be replaced by Entra ID"""

from flask import Response, session
from flask_wtf import FlaskForm

from app.views import BaseFormView


class AuthenticationFormView(BaseFormView):
    success_endpoint = "main.providers"

    def form_valid(self, form: FlaskForm) -> Response:
        session["authenticated"] = True
        return super().form_valid(form)
