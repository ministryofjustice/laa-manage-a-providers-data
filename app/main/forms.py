from wtforms.fields.simple import StringField
from wtforms.validators import Length

from app.forms import BaseForm
from app.widgets import GovTextInput


class ProviderListForm(BaseForm):
    title = "Provider records"
    url = "providers"
    template = "providers.html"

    class Meta:
        csrf = False  # CSRF is disabled as this form only accepts GET requests with search data in a query string.

    search = StringField(
        "Find a provider",
        widget=GovTextInput(
            form_group_classes="govuk-!-width-two-thirds",
            heading_class="govuk-fieldset__legend--s",
            classes="provider-search",
            hint="You can search by name, office or account number",
        ),
        validators=[Length(max=100, message="Search term must be 100 characters or less")],
    )
