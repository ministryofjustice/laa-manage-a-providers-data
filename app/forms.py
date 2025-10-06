from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Length

from app.validators import ValidateAccountNumber, ValidateSortCode
from app.widgets import GovTextInput


class BaseForm(FlaskForm):
    template: str = "form.html"
    title: str = "Form Title"  # Supports line breaks with "\n"
    url: str = "example-form"
    caption: str | None = None  # Optional caption text that will render above the form title
    description: str | None = None  # Optional description text that will render under the form title
    submit_button_text: str = "Continue"  # Should be "Submit" on final page before creating a new entity.


class BaseBankAccountForm(BaseForm):
    bank_account_name = StringField(
        "Account name",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            classes="govuk-!-width-one-quarter",
        ),
        validators=[
            InputRequired(message="Enter the account name"),
            Length(max=100, message="Account name must be 100 characters or less"),
        ],
    )

    sort_code = StringField(
        "Sort code",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            classes="govuk-input--width-10",
            hint="Must be 6 digits long",
        ),
        validators=[
            InputRequired(message="Enter a sort code"),
            ValidateSortCode(),
        ],
    )

    account_number = StringField(
        "Account number",
        widget=GovTextInput(
            heading_class="govuk-fieldset__legend--m",
            classes="govuk-!-width-one-quarter",
            hint="Must be between 6 and 8 digits long",
        ),
        validators=[
            InputRequired(message="Enter an account number"),
            ValidateAccountNumber(),
        ],
    )
