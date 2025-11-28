from app.models import Firm, Office


def get_firm_by_name(app, firm_name: str) -> Firm | None:
    pda = app.extensions["pda"]
    firms = pda.get_all_provider_firms()
    for firm in firms:
        if firm.firm_name == firm_name:
            return firm
    return None


def get_firm_office_by_office_code(app, office_code: str) -> Office:
    pda = app.extensions["pda"]
    return pda.get_provider_office(office_code)
