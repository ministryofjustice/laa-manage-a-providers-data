import logging
from typing import Dict, List, Literal, NoReturn

from flask import abort, current_app, redirect, render_template, request, url_for
from flask.views import MethodView

from app.components.tables import DataTable, SummaryList, TableStructureItem
from app.main.forms import firm_name_html, get_firm_statuses
from app.main.table_builders import (
    get_bank_account_tables,
    get_contact_tables,
    get_main_table,
    get_office_contact_table,
    get_office_overview_table,
    get_payment_information_table,
    get_status_table,
    get_vat_registration_table,
)
from app.main.utils import create_provider_from_session, firm_office_url_for, get_firm_tags, get_office_tags
from app.models import Firm, Office
from app.utils.formatting import (
    format_office_address_multi_line_html,
    format_office_address_one_line,
)
from app.views import BaseFormView

logger = logging.getLogger(__name__)


class ProviderList(BaseFormView):
    """View for provider list"""

    template = "providers.html"

    def get(self, context):
        form = self.get_form_class()(request.args)
        form.validate()
        return render_template(self.get_template(), **self.get_context_data(form, context))

    def post(self, context) -> NoReturn:
        """POST method not allowed for this resource."""
        abort(405)


class ViewProvider(MethodView):
    templates = {
        "Legal Services Provider": "view-provider-legal-services-provider.html",
        "Chambers": "view-provider-chambers.html",
        "Advocate": "view-provider-advocate-barrister.html",
        "Barrister": "view-provider-advocate-barrister.html",
    }

    def __init__(
        self, subpage: Literal["contact", "offices", "barristers-advocates", "bank-accounts-payment"] = "contact"
    ):
        if subpage:
            self.subpage = subpage

    def get_office_tables(self, firm, head_office: Office, other_offices: list[Office]) -> dict[str, DataTable]:
        """Gets two data tables one for the main office and one for other offices."""
        office_tables = {}

        def firm_office_html(row_data: dict[str, str]) -> str:
            # Renders the office account number as a link
            _office_code = row_data.get("firm_office_code", "")
            return f"<a class='govuk-link' href='{url_for('main.view_office', firm=firm.firm_id, office=_office_code)}'>{_office_code}</a>"

        def firm_office_statuses(row_data: dict[str, str]) -> str:
            status_tags = get_office_tags(office=row_data)
            if status_tags:
                return f"<div>{''.join([s.render() for s in status_tags])}</div>"
            return "<p class='govuk-visually-hidden'>No statuses</p>"

        office_table_structure: list[TableStructureItem] = [
            {"text": "Account number", "id": "firm_office_code", "html_renderer": firm_office_html},
            {"text": "Address", "text_renderer": format_office_address_one_line},
            {"text": "Status", "id": "firm_number", "html_renderer": firm_office_statuses},
        ]

        if head_office:
            head_office_data_table = DataTable(office_table_structure, head_office.to_internal_dict())
            office_tables.update({"head": head_office_data_table})

        if other_offices:
            other_offices_dict = list(map(lambda o: o.to_internal_dict(), other_offices))
            other_offices_data_table = DataTable(office_table_structure, other_offices_dict)
            office_tables.update({"other": other_offices_data_table})

        return office_tables

    def get_chambers_contact_details_table(self, firm, head_office: Office) -> SummaryList:
        """Gets information about the chambers head office"""
        table = SummaryList(additional_classes="chambers-contact-details")

        row_action_urls = {
            "address": {
                "enter": url_for("main.change_chambers_details", firm=firm, _anchor="address_line_1"),
                "change": url_for("main.change_chambers_details", firm=firm, _anchor="address_line_1"),
            },
            "email": {
                "enter": url_for("main.change_chambers_details", firm=firm, _anchor="email_address"),
                "change": url_for("main.change_chambers_details", firm=firm, _anchor="email_address"),
            },
            "telephone": {
                "enter": url_for("main.change_chambers_details", firm=firm, _anchor="telephone_number"),
                "change": url_for("main.change_chambers_details", firm=firm, _anchor="telephone_number"),
            },
            "dx_number": {
                "enter": url_for("main.change_chambers_details", firm=firm, _anchor="dx_number"),
                "change": url_for("main.change_chambers_details", firm=firm, _anchor="dx_number"),
            },
            "dx_centre": {
                "enter": url_for("main.change_chambers_details", firm=firm, _anchor="dx_centre"),
                "change": url_for("main.change_chambers_details", firm=firm, _anchor="dx_centre"),
            },
        }
        table.add_row(
            "Address",
            "test",
            html=format_office_address_multi_line_html(head_office),
            row_action_urls=row_action_urls["address"],
        )
        table.add_row("Email address", head_office.email_address, row_action_urls=row_action_urls["email"])
        table.add_row("Telephone number", head_office.telephone_number, row_action_urls=row_action_urls["telephone"])
        table.add_row("DX number", head_office.dx_number, row_action_urls=row_action_urls["dx_number"])
        table.add_row("DX centre", head_office.dx_centre, row_action_urls=row_action_urls["dx_centre"])

        return table

    @staticmethod
    def get_account_number_or_default(account_number: str | None) -> str:
        """
        Renders the office account number, defaulting to "Unknown" if no account number is provided.
        """
        if account_number not in (None, ""):
            return account_number
        return "Unknown"

    def get_child_firm_office_table_data(self, child_firms: List[Firm]) -> List[Dict]:
        """
        Adds the `account_number` to each child, which is taken from the `firm_office_code` value of the head office
        of the child.

        If the child does not have a head office, a warning will be logged and the `account_number` will be empty. For
        the link to the office to work, each child also has `_account_number_firm_id` populated with the child firm id.

        Args:
            child_firms: List of Firms to show in the table
        """
        pda = current_app.extensions["pda"]

        # Aggregate the child firm with its office
        aggregated_data = []
        for child in child_firms:
            child_data = child.to_internal_dict()
            child_head_office = pda.get_head_office(child.firm_id)
            if child_head_office:
                child_data["account_number"] = child_head_office.firm_office_code
                child_data["_account_number_firm_id"] = child.firm_id
            else:
                logger.warning(f"Firm {child.firm_id} does not have a head office.")
                child_data["account_number"] = ""
                child_data["_account_number_firm_id"] = ""

            aggregated_data.append(child_data)

        return aggregated_data

    def get_barristers_table(self, firm: Firm) -> DataTable | None:
        pda = current_app.extensions["pda"]
        child_barristers = pda.get_provider_children(firm_id=firm.firm_id, only_firm_type="Barrister")

        if len(child_barristers) == 0:
            return None

        columns: list[TableStructureItem] = [
            {"text": "Name", "id": "firm_name", "html_renderer": firm_name_html},
            {"text": "Account number", "id": "account_number", "format_text": self.get_account_number_or_default},
            {"text": "Bar Council roll number", "id": "bar_council_roll"},
            {"text": "Status", "html_renderer": get_firm_statuses},  # Add status tags here when available.
        ]
        child_firm_office_table_data = self.get_child_firm_office_table_data(child_barristers)
        table = DataTable(structure=columns, data=child_firm_office_table_data)

        return table

    def get_advocates_table(self, firm: Firm) -> DataTable | None:
        pda = current_app.extensions["pda"]
        child_advocates = pda.get_provider_children(firm_id=firm.firm_id, only_firm_type="Advocate")

        if len(child_advocates) == 0:
            return None

        columns: list[TableStructureItem] = [
            {"text": "Name", "id": "firm_name", "html_renderer": firm_name_html},
            {"text": "Account number", "id": "account_number", "format_text": self.get_account_number_or_default},
            {"text": "Solicitors Regulation Authority roll number", "id": "bar_council_roll"},
            {"text": "Status", "html_renderer": get_firm_statuses},  # Add status tags here when available.
        ]

        child_firm_office_table_data = self.get_child_firm_office_table_data(child_advocates)
        table = DataTable(structure=columns, data=child_firm_office_table_data)

        return table

    def get_context(self, firm):
        pda = current_app.extensions["pda"]

        head_office, parent_provider = None, None

        context = {"firm": firm, "firm_tags": get_firm_tags(firm)}

        if firm.firm_id:
            # Get head office for account number
            head_office: Office = pda.get_head_office(firm.firm_id)
            context.update({"head_office": head_office})

        if firm.parent_firm_id:
            # Get parent provider
            parent_provider: Firm = pda.get_provider_firm(firm.parent_firm_id)
            context.update({"parent_provider": parent_provider})

        if firm.is_advocate and parent_provider:
            chambers_head_office = pda.get_head_office(parent_provider.firm_id)
            context.update(
                {
                    "chambers_contact_details_table": self.get_chambers_contact_details_table(
                        parent_provider, chambers_head_office
                    )
                }
            )

        main_table = get_main_table(firm, head_office, parent_provider)
        context.update({"main_table": main_table})

        # Add status table
        status_table = get_status_table(firm)
        context.update({"status_table": status_table})

        if self.subpage == "offices":
            offices = pda.get_provider_offices(firm.firm_id)

            # Remove the head office from the list of offices
            other_offices = list(filter(lambda o: not o.get_is_head_office(), offices))

            office_tables = self.get_office_tables(firm, head_office, other_offices)
            context.update({"office_tables": office_tables})

        if self.subpage == "contact":
            if firm.firm_type == "Chambers" and head_office:
                context.update({"contact_details_table": self.get_chambers_contact_details_table(firm, head_office)})

            context.update({"contact_tables": get_contact_tables(firm, head_office)})

        if self.subpage == "barristers-advocates":
            context.update({"barristers_table": self.get_barristers_table(firm)})
            context.update({"advocates_table": self.get_advocates_table(firm)})

        if self.subpage == "bank-accounts-payment":
            if head_office:
                add_bank_account_url = firm_office_url_for("main.search_bank_account", firm=firm, office=head_office)
                context.update(
                    {
                        "vat_registration_table": get_vat_registration_table(firm, head_office),
                        "payment_information_table": get_payment_information_table(firm, head_office),
                        "bank_account_tables": get_bank_account_tables(
                            firm=firm, office=head_office, action_url=add_bank_account_url
                        ),
                        "add_new_bank_account_url": add_bank_account_url,
                    }
                )

        return context

    def get(self, firm: Firm | None = None):
        if not firm:
            if created_firm := create_provider_from_session():
                return redirect(url_for("main.view_provider", firm=created_firm))
            abort(404)

        context = self.get_context(firm)
        template = self.templates.get(firm.firm_type, "view-provider-legal-services-provider.html")

        return render_template(template, subpage=self.subpage, **context)


class ViewOffice(MethodView):
    template = "view-office.html"

    def __init__(self, subpage: Literal["overview", "contact", "bank-payment-details"] = "overview"):
        if subpage:
            self.subpage = subpage

    def get_context(self, firm: Firm, office: Office) -> Dict:
        add_bank_account_url = url_for("main.search_bank_account", firm=firm, office=office.firm_office_code)
        context = {
            "firm": firm,
            "office": office,
            "subpage": self.subpage,
            "office_tags": get_office_tags(office),
            "add_bank_account_url": add_bank_account_url,
        }

        # Add status table
        status_table = get_status_table(office, firm=firm, office=office)
        context.update({"status_table": status_table})

        if self.subpage == "bank-payment-details":
            context.update(
                {
                    "vat_registration_table": get_vat_registration_table(firm, office),
                    "payment_information_table": get_payment_information_table(firm, office),
                    "bank_account_tables": get_bank_account_tables(
                        firm=firm, office=office, action_url=add_bank_account_url
                    ),
                }
            )

        if self.subpage == "contact":
            contact_table = get_office_contact_table(firm, office)
            context.update(
                {
                    "office_contact_details": [
                        contact_table,
                    ]
                    if contact_table
                    else None
                }
            )
            context.update({"contact_tables": get_contact_tables(firm, office, changing_office=True)})

        if self.subpage == "overview":
            context.update({"overview_table": get_office_overview_table(firm, office)})

        return context

    def get(self, firm: Firm, office: Office | None = None):
        if not firm or not office:
            abort(404)

        context = self.get_context(firm, office)

        return render_template(self.template, **context)


class AdvocateBarristerOfficeMixin:
    def get_success_url(self, form) -> str:
        if form.firm.is_advocate or form.firm.is_barrister:
            return url_for(self.provider_success_url, firm=form.firm)

        return url_for(self.office_success_url, firm=form.firm, office=form.office)

    def dispatch_request(self, *args, **kwargs):
        firm: Firm = kwargs.get("firm")
        office: Office | None = kwargs.get("office")

        if not firm.is_advocate and not firm.is_barrister and not office:
            abort(404)

        kwargs["office"] = office if office else self.get_api().get_head_office(firm.firm_id)

        return super().dispatch_request(*args, **kwargs)
