import math

from flask import abort, render_template, request, url_for

from app import provider_data_api as pda
from app.main import bp
from app.main.table import Column, DataTable
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
def providers():
    def firm_name_html(row_data: dict[str, str]) -> str:
        _firm_id = row_data.get("firmId", "")
        _firm_name = row_data.get("firmName", "")
        return f"<a class='govuk-link', href={url_for('main.offices', firm_id=_firm_id)}>{_firm_name}"

    providers_shown_per_page = 10

    data = pda.get_all_provider_firms()
    provider_data = data["firms"]

    columns: list[Column] = [
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

    table = DataTable(columns=columns, data=provider_data[start_id:end_id])

    return render_template(
        "providers.html",
        table=table,
        current_page=page,
        num_shown_per_page=providers_shown_per_page,
        num_results=len(provider_data),
    )


@bp.get("/provider/<int:firm_id>/offices")
def offices(firm_id: int):
    def firm_office_html(row_data: dict[str, str]) -> str:
        _office_code = row_data.get("firmOfficeCode", "")
        return f"<a class='govuk-link' href='{url_for('main.contracts', firm_id=firm_id, office_code=_office_code)}'>{_office_code}</a>"

    data = pda.get_provider_offices(firm_id)
    office_data = data["offices"]
    provider_name = data["firm"]["firmName"]

    columns: list[Column] = [
        {"text": "Office Code", "id": "firmOfficeCode", "html": firm_office_html},
        {"text": "Name", "id": "officeName"},
        {"text": "City", "id": "city", "format_text": lambda x: x.title()},
        {"text": "Type", "id": "type"},
        {"text": "Head Office", "id": "headOffice", "format_text": lambda x: "Yes" if x == "N/A" else ""},
        {"text": "Creation Date", "id": "creationDate"},
        {"text": "Full info", "html": get_full_info_html},
    ]

    table = DataTable(columns=columns, data=office_data)

    return render_template("offices.html", provider=provider_name, firm_id=firm_id, table=table)


@bp.get("/provider/<int:firm_id>/office/<string:office_code>/contracts")
def contracts(firm_id: int, office_code: str):
    columns: list[Column] = [
        {"text": "Category of Law", "id": "categoryOfLaw"},
        {"text": "Sub Category of Law", "id": "subCategoryLaw"},
        {"text": "Authorisation Type", "id": "authorisationType"},
        {"text": "New Matters", "id": "newMatters"},
        {"text": "Contractual Devolved Powers", "id": "contractualDevolvedPowers"},
        {"text": "Remainder Authorisation", "id": "remainderAuthorisation"},
        {"text": "Full info", "html": get_full_info_html},
    ]

    data = pda.get_office_contract_details(firm_id, office_code)

    contract_data = data["contracts"] if "contracts" in data else []
    if len(contract_data) != 0:
        office_name = data["office"]["officeName"].lstrip(f"{office_code},")
    else:
        office_name = pda.get_provider_office(office_code)["office"]["officeName"].lstrip(f"{office_code},")

    table = DataTable(columns=columns, data=contract_data)

    return render_template(
        "contracts.html", firm_id=firm_id, office_code=office_code, office_name=office_name, table=table
    )


@bp.get("/provider/<int:firm_id>/office/<string:office_code>/schedules")
def schedules(firm_id: int, office_code: str):
    columns = [
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

    data = pda.get_office_schedule_details(firm_id, office_code)
    schedule_data = data["schedules"] if "schedules" in data else []
    if len(schedule_data) != 0:
        office_name = data["office"]["officeName"].lstrip(f"{office_code},")
    else:
        office_name = pda.get_provider_office(office_code)["office"]["officeName"].lstrip(f"{office_code},")

    table = DataTable(columns=columns, data=schedule_data)

    return render_template(
        "schedules.html", firm_id=firm_id, office_code=office_code, office_name=office_name, table=table
    )


@bp.get("/provider/<int:firm_id>/office/<string:office_code>/bank-details")
def bank_details(firm_id: int, office_code: str):
    columns = [
        {"text": "Bank Branch Name", "id": "bankBranchName"},
        {"text": "Account Number", "id": "accountNumber"},
        {"text": "Sort Code", "id": "sortCode"},
        {"text": "Account Type", "id": "accountType"},
        {"text": "Primary", "id": "primaryFlag"},
        {"text": "Full info", "html": get_full_info_html},
    ]
    office_name = pda.get_provider_office(office_code)["office"]["officeName"].lstrip(f"{office_code},")

    return render_template(
        "bank-details.html", firm_id=firm_id, office_code=office_code, office_name=office_name, headings=columns
    )
