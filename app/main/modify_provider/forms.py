from wtforms.fields import RadioField

from app.forms import BaseForm
from app.main.add_a_new_provider.forms import LiaisonManagerForm
from app.models import Firm
from app.widgets import GovRadioInput


class ChangeForm:
    submit_button_text = "Save"


class ChangeLiaisonManagerForm(ChangeForm, LiaisonManagerForm):
    title = "Change liaison manager"
    url = "provider/<firm:firm>/add-liaison-manager"
    description = "This will make the current liaison manager inactive"

    def __init__(self, firm: Firm, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm

    @property
    def caption(self):
        if not self.firm or not isinstance(self.firm, Firm):
            return "Unknown"
        return self.firm.firm_name


class ChangeProviderActiveStatusForm(ChangeForm, BaseForm):
    def __init__(self, firm: Firm, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm

        choice_hints = {
            "active": "This will not make all the offices of this provider active. Any office can be made active after you make the provider active."
        }
        if self.status.data == "active":
            choice_hints = {"inactive": "This will also make all offices of this provider inactive."}
        self.status.widget.choice_hints = choice_hints

    title = "Change active status"
    url = "provider/<firm:firm>/confirm-provider-status"
    template = "modify_provider/form.html"
    status = RadioField(
        "",
        widget=GovRadioInput(
            heading_class="govuk-fieldset__legend--m",
        ),
        choices=[("active", "Active"), ("inactive", "Inactive")],
    )
