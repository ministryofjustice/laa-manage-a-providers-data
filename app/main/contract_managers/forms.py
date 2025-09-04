from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired, InputRequired, Length

from app.fields import GovUKTableCheckboxField
from app.forms import BaseForm
from app.services.contract_managers import ContractManagerService
from app.widgets import GovTextInput


class ValidateContractManagerDoesNotExist:
    """Validator to check if a contract manager name doesn't already exist"""

    def __init__(self, message=None):
        if not message:
            message = "Contract manager already exists"
        self.message = message

    def __call__(self, form, field):
        service = ContractManagerService()
        existing_managers = service.get_all()

        if field.data and field.data.strip() in existing_managers:
            raise ValidationError(self.message)


class AddContractManagerForm(BaseForm):
    title = "Add Contract Manager"
    url = "contract-managers"
    submit_button_text = "Add Manager"

    name = StringField(
        "Contract manager's name",
        widget=GovTextInput(heading_class="govuk-fieldset__legend--m"),
        validators=[
            InputRequired(message="Enter the contract manager's name"),
            Length(max=100, message="Name must be 100 characters or less"),
            ValidateContractManagerDoesNotExist(),
        ],
    )


class BulkRemoveContractManagerForm(BaseForm):
    title = "Remove Selected Managers"
    url = "contract-managers"
    submit_button_text = "Remove Selected"

    selected_managers = GovUKTableCheckboxField(
        "",
        structure=[
            {"text": "Contract manager's name", "id": "name"},
        ],
        checkbox_value_key="name",
        validators=[DataRequired(message="Please select at least one manager to remove")],
    )

    def __init__(self, page=1, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize pagination attributes
        self.page = page
        self.managers_shown_per_page = 10

        # Get paginated managers
        service = ContractManagerService()
        paginated_data = service.get_paginated(page=page, per_page=self.managers_shown_per_page)

        # Set pagination attributes for template
        self.num_results = paginated_data["total_count"]
        self.has_next = paginated_data["has_next"]
        self.has_prev = paginated_data["has_prev"]

        # Populate choices with current page of managers
        managers = paginated_data["managers"]
        self.selected_managers.choices = [(manager, {"name": manager}) for manager in managers]
