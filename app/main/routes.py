import math

from flask import abort, current_app, render_template, request, url_for

from app.auth import requires_authentication
from app.components.tables import DataTable, TableStructure, TransposedDataTable
from app.main import bp
from app.main.utils import get_full_info_html


@bp.get("/")
def index():
    """Directs the user to the start page of the service
    This is the endpoint directed to from the header text, clicking this link will reset the users' session.
    """
    return render_template("index.html")


@bp.route("/status", methods=["GET"])
def status():
    return "OK"


@bp.get("/providers")
@requires_authentication
def providers():
    def firm_name_html(row_data: dict[str, str]) -> str:
        _firm_id = row_data.get("firmId", "")
        _firm_name = row_data.get("firmName", "")
        return f"<a class='govuk-link', href={url_for('main.offices', firm_id=_firm_id)}>{_firm_name}"

    providers_shown_per_page = 20

    start_provider_firm_num = 0

    if not current_app.config["TESTING"]:
        start_provider_firm_num = 50647  # ID where the test data begins in PDA UAT.

    pda = current_app.extensions["pda"]
    data = pda.get_all_provider_firms()

    print(pda.get_all_provider_firms()["firms"])
    provider_data = data["firms"][start_provider_firm_num:]

    columns: list[TableStructure] = [
        {"text": "Name", "id": "firmName", "html": firm_name_html},
        {"text": "Type", "id": "firmType"},
        {"text": "Constitutional status", "id": "constitutionalStatus"},
        {"text": "Website", "id": "websiteUrl"},
        {"text": "Full info", "html": get_full_info_html},
    ]

    page = request.args.get("page", 1, type=int)
    max_page = math.ceil(len(provider_data) / providers_shown_per_page)

    if page < 1 or page > max_page:
        return abort(404)

    start_id = providers_shown_per_page * (page - 1)
    end_id = providers_shown_per_page * (page - 1) + providers_shown_per_page

    table = DataTable(structure=columns, data=provider_data[start_id:end_id])

    return render_template(
        "providers.html",
        table=table,
        current_page=page,
        num_shown_per_page=providers_shown_per_page,
        num_results=len(provider_data),
    )


@bp.get("/provider/<int:firm_id>/offices")
@requires_authentication
def offices(firm_id: int):
    def firm_office_html(row_data: dict[str, str]) -> str:
        _office_code = row_data.get("firmOfficeCode", "")
        return f"<a class='govuk-link' href='{url_for('main.contracts', firm_id=firm_id, office_code=_office_code)}'>{_office_code}</a>"

    pda = current_app.extensions["pda"]
    data = pda.get_provider_offices(firm_id)
    office_data = data["offices"]
    provider_name = data["firm"]["firmName"]

    columns: list[TableStructure] = [
        {"text": "Office Code", "id": "firmOfficeCode", "html": firm_office_html},
        {"text": "Name", "id": "officeName"},
        {"text": "City", "id": "city", "format_text": lambda x: x.title()},
        {"text": "Type", "id": "type"},
        {"text": "Head Office", "id": "headOffice", "format_text": lambda x: "Yes" if x == "N/A" else ""},
        {"text": "Creation Date", "id": "creationDate"},
        {"text": "Full info", "html": get_full_info_html},
    ]

    table = DataTable(structure=columns, data=office_data)

    return render_template("offices.html", provider=provider_name, firm_id=firm_id, table=table)


@bp.get("/provider/<int:firm_id>/office/<string:office_code>/contracts")
@requires_authentication
def contracts(firm_id: int, office_code: str):
    columns: list[TableStructure] = [
        {"text": "Category of Law", "id": "categoryOfLaw"},
        {"text": "Sub Category of Law", "id": "subCategoryLaw"},
        {"text": "Authorisation Type", "id": "authorisationType"},
        {"text": "New Matters", "id": "newMatters"},
        {"text": "Contractual Devolved Powers", "id": "contractualDevolvedPowers"},
        {"text": "Remainder Authorisation", "id": "remainderAuthorisation"},
        {"text": "Full info", "html": get_full_info_html},
    ]

    pda = current_app.extensions["pda"]
    data = pda.get_office_contract_details(firm_id, office_code)

    contract_data = data["contracts"] if "contracts" in data else []
    if len(contract_data) != 0:
        office_name = data["office"]["officeName"]
    else:
        office_name = pda.get_provider_office(office_code)["office"]["officeName"]

    table = DataTable(structure=columns, data=contract_data)

    return render_template(
        "contracts.html", firm_id=firm_id, office_code=office_code, office_name=office_name, table=table
    )


@bp.get("/provider/<int:firm_id>/office/<string:office_code>/schedules")
@requires_authentication
def schedules(firm_id: int, office_code: str):
    columns: list[TableStructure] = [
        {"text": "Contract Description", "id": "contractDescription"},
        {"text": "Contract Reference", "id": "contractReference"},
        {"text": "Contract Type", "id": "contractType"},
        {"text": "Contract Authorization Status", "id": "contractAuthorizationStatus"},
        {"text": "Area of Law", "id": "areaOfLaw"},
        {"text": "Schedule Type", "id": "scheduleType"},
        {"text": "Schedule Number", "id": "scheduleNumber"},
        {"text": "Start Date", "id": "scheduleStartDate"},
        {"text": "End Date", "id": "scheduleEndDate"},
        {"text": "Schedule Authorization Status", "id": "scheduleAuthorizationStatus"},
        {"text": "Schedule Status", "id": "scheduleStatus"},
        {"text": "Full info", "html": get_full_info_html},
    ]

    pda = current_app.extensions["pda"]
    data = pda.get_office_schedule_details(firm_id, office_code)
    schedule_data = data["schedules"] if "schedules" in data else []
    if len(schedule_data) != 0:
        office_name = data["office"]["officeName"]
    else:
        office_name = pda.get_provider_office(office_code)["office"]["officeName"]

    table = DataTable(structure=columns, data=schedule_data)

    return render_template(
        "schedules.html", firm_id=firm_id, office_code=office_code, office_name=office_name, table=table
    )


@bp.get("/provider/<int:firm_id>/office/<string:office_code>/bank-details")
@requires_authentication
def bank_details(firm_id: int, office_code: str):
    rows: list[TableStructure] = [
        {"text": "Vendor Site ID", "id": "vendorSiteId"},
        {"text": "Bank Name", "id": "bankName"},
        {"text": "Bank Branch Name", "id": "bankBranchName"},
        {"text": "Sort Code", "id": "sortCode"},
        {"text": "Account Number", "id": "accountNumber"},
        {"text": "Bank Account Name", "id": "bankAccountName"},
        {"text": "Currency Code", "id": "currencyCode"},
        {"text": "Account Type", "id": "accountType"},
        {"text": "Primary", "id": "primaryFlag"},
        {"text": "Address Line 1", "id": "addressLine1"},
        {"text": "Address Line 2", "id": "addressLine2"},
        {"text": "Address Line 3", "id": "addressLine3"},
        {"text": "City", "id": "city"},
        {"text": "County", "id": "county"},
        {"text": "Country", "id": "country"},
        {"text": "Postcode", "id": "zip"},
        {"text": "Full info", "html": get_full_info_html},
    ]

    pda = current_app.extensions["pda"]
    office_name = pda.get_provider_office(office_code)["office"]["officeName"]

    example_data = {
        "vendorSiteId": "0",
        "bankName": "Example Bank",
        "bankBranchName": "Branch Name",
        "sortCode": "12-34-56",
        "accountNumber": "12345678",
        "bankAccountName": "Account Holder Name",
        "currencyCode": "GBP",
        "accountType": "Account type",
        "primaryFlag": "Y",
        "addressLine1": "123 Main Street",
        "addressLine2": "Business District",
        "addressLine3": "",
        "city": "London",
        "county": "Greater London",
        "country": "United Kingdom",
        "zip": "SW1A 1AA",
    }

    table = TransposedDataTable(structure=rows, data=example_data)

    return render_template(
        "bank-details.html", firm_id=firm_id, office_code=office_code, office_name=office_name, table=table
    )
