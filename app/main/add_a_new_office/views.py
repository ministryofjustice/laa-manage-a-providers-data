from flask import Response, redirect, render_template, url_for

from app.constants import STATUS_CONTRACT_MANAGER_NAMES
from app.main.utils import add_new_office
from app.models import Firm, Office
from app.views import BaseFormView


class OfficeContactDetailsFormView(BaseFormView):
    """Form view for the Office Contact Details page"""

    def get_success_url(self, new_office: Office, firm: Firm) -> str:
        # Check if the head office has a status workaround contract manager
        head_office: Office = self.get_api().get_head_office(firm.firm_id)
        if head_office.contract_manager in STATUS_CONTRACT_MANAGER_NAMES:
            # Set contract manager on office if head office has a status workaround contract manager
            return url_for("main.change_office_contract_manager", firm=firm, office=new_office)
        return url_for("main.view_office", firm=firm, office=new_office)

    def form_valid(self, form):
        head_office: Office = self.get_api().get_head_office(form.firm.firm_id)
        # Add contact details to the existing office dict
        office_details = {
            "office_name": form.firm.firm_name,
            "head_office": str(head_office.firm_office_id) if head_office else "N/A",
            "address_line_1": form.data.get("address_line_1"),
            "address_line_2": form.data.get("address_line_2"),
            "address_line_3": form.data.get("address_line_3"),
            "address_line_4": form.data.get("address_line_4"),
            "city": form.data.get("city"),
            "county": form.data.get("county"),
            "postcode": form.data.get("postcode"),
            "telephone_number": form.data.get("telephone_number"),
            "email_address": form.data.get("email_address"),
            "dx_number": form.data.get("dx_number"),
            "dx_centre": form.data.get("dx_centre"),
            "payment_method": "Electronic",  # The new office must be set to Electronic payment method so we do it here before the office is created
            "contract_manager": head_office.contract_manager,  # Inherit the contract manager from the head office
        }

        # Create the office
        office = Office(**office_details)
        new_office = add_new_office(office, firm_id=form.firm.firm_id)

        return redirect(self.get_success_url(new_office, form.firm))

    def get(self, context, firm: Firm, **kwargs):
        form = self.get_form_class()(firm=firm)
        return render_template(self.template, **self.get_context_data(form, **kwargs))

    def post(self, firm: Firm, *args, **kwargs) -> Response | str:
        form = self.get_form_class()(firm=firm)

        if form.validate_on_submit():
            return self.form_valid(form)
        else:
            return self.form_invalid(form, **kwargs)
