from flask import current_app, render_template

from app import auth
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


@bp.get("/provider/<int:firm_id>/office/<string:office_code>/contracts")
@auth.login_required
def contracts(firm_id: int, office_code: str, context):
    columns: list[TableStructure] = [
        {"text": "Category of Law", "id": "categoryOfLaw"},
        {"text": "Sub Category of Law", "id": "subCategoryLaw"},
        {"text": "Authorisation Type", "id": "authorisationType"},
        {"text": "New Matters", "id": "newMatters"},
        {"text": "Contractual Devolved Powers", "id": "contractualDevolvedPowers"},
        {"text": "Remainder Authorisation", "id": "remainderAuthorisation"},
        {"text": "Full info", "html_renderer": get_full_info_html},
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
@auth.login_required
def schedules(firm_id: int, office_code: str, context):
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
@auth.login_required
def bank_details(firm_id: int, office_code: str, context):
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
