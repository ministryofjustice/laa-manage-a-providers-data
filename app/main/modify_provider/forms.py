from flask import current_app
from wtforms.fields import RadioField
from wtforms.fields.simple import StringField
from wtforms.validators import InputRequired, Length

from app.constants import PROVIDER_ACTIVE_STATUS_CHOICES
from app.fields import GovUKTableRadioField
from app.forms import BaseForm
from app.main.add_a_new_provider.forms import LiaisonManagerForm
from app.main.utils import get_firm_account_number
from app.models import Firm, Office
from app.utils.formatting import format_office_address_one_line
from app.validators import ValidateSearchResults
from app.widgets import GovRadioInput, GovTextInput


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


class ChangeOfficeLiaisonManagerForm(ChangeLiaisonManagerForm):
    url = "provider/<firm:firm>/office/<office:office>/add-liaison-manager"

    def __init__(self, firm: Firm, office: Office | None = None, *args, **kwargs):
        super().__init__(firm, *args, **kwargs)
        self.office = office


class ChangeProviderActiveStatusForm(ChangeForm, BaseForm):
    def __init__(self, firm: Firm, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm

        choice_hints = {}
        if firm.is_legal_services_provider:
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
        choices=PROVIDER_ACTIVE_STATUS_CHOICES,
    )


class AssignChambersForm(BaseForm):
    url = "provider/<firm:firm>/assign-chambers"
    template = "add_provider/assign-chambers.html"
    success_url = "main.providers"
    submit_button_text = "Submit"

    @property
    def title(self):
        return f"Assign chambers for {self.firm.firm_name}"

    search = StringField(
        "Search for a chambers",
        widget=GovTextInput(
            form_group_classes="govuk-!-width-two-thirds",
            heading_class="govuk-fieldset__legend--s",
            hint="You can search by name or account number",
        ),
        validators=[Length(max=100, message="Search term must be 100 characters or less"), ValidateSearchResults()],
    )

    provider = GovUKTableRadioField(
        "",
        structure=[
            {"text": "Provider", "id": "firm_name"},
            {"text": "Account number", "id": "account_number"},
        ],
        choices=[],  # This will be set when the user sends a request.
        radio_value_key="firm_id",
        validators=[],  # Will be set dynamically in __init__
    )

    def __init__(self, firm: Firm, search_term=None, page=1, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.firm = firm  # Advocate or barrister we are modifying

        # Set dynamic validation message based on firm type
        self.provider.validators = [
            InputRequired(message=f"Select a chambers to assign the {self.firm.firm_type.lower()} to")
        ]

        # Get firms data
        pda = current_app.extensions["pda"]
        all_firms = pda.get_all_provider_firms()

        # Advocates or Barristers can only have Chambers as their parent
        chambers: list[Firm] = [firm for firm in all_firms if firm.firm_type == "Chambers"]

        # Set search field data
        self.search_term = search_term
        if search_term:
            self.search.data = search_term

        # Filter chambers based on search term
        if self.search_term:
            search_lower = self.search_term.lower()
            chambers = [
                chamber
                for chamber in chambers
                if (search_lower in chamber.firm_name.lower() or search_lower in str(chamber.firm_id).lower())
            ]

        self.page = page
        self.providers_shown_per_page = 7
        self.num_results = len(chambers)

        # Limit results and populate choices
        start_id = self.providers_shown_per_page * (self.page - 1)
        end_id = self.providers_shown_per_page * (self.page - 1) + self.providers_shown_per_page

        chambers = chambers[start_id:end_id]
        choices = []
        for chamber in chambers:
            choices.append(
                (
                    chamber.firm_id,
                    {
                        "firm_name": chamber.firm_name,
                        "account_number": get_firm_account_number(chamber),
                        "firm_type": chamber.firm_type,
                    },
                )
            )

        self.provider.choices = choices


class ReassignHeadOfficeForm(BaseForm):
    url = "provider/<firm:firm>/reassign-head-office"
    title = "Reassign head office"
    template = "modify_provider/reassign_head_office.html"
    success_url = "main.view_provider_offices"
    submit_button_text = "Submit"

    office = GovUKTableRadioField(
        "",
        structure=[
            {"text": "Account number", "id": "account_number"},
            {"text": "Address", "id": "address_single_line"},
        ],  # Display as a table with columns for Account number and Address
        radio_value_key="firm_office_code",
        choices=[],  # Set dynamically to providers offices
        validators=[],  # Set dynamically to add provider name
    )
    firm: Firm
    current_head_office: Office

    def __init__(self, firm: Firm, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.firm = firm
        self.office.validators = [InputRequired(message=f"Select a new head office for {self.firm.firm_name}")]

        pda = current_app.extensions["pda"]
        firm_offices = pda.get_provider_offices(firm_id=self.firm.firm_id)
        # Preload the current (without change) head office so the view can determine any changes
        head_office = pda.get_head_office(firm_id=self.firm.firm_id)
        self.current_head_office = head_office

        # Populate the choice of offices for the firm
        choices = []
        for office in firm_offices:
            choices.append(
                (
                    office.firm_office_code,
                    {
                        "account_number": office.firm_office_code,
                        "address_single_line": format_office_address_one_line(office),
                    },
                )
            )

        self.office.choices = choices
