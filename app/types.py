from typing import Literal, TypedDict

FirmType = Literal["Advocate", "Chambers", "Legal Services Provider"]
ConstitutionalStatus = Literal[
    "Charity", "Government Funded Organisation", "LLP", "Limited Company", "Partnership", "Sole Practitioner", "N/A"
]
AdvocateLevel = Literal["KC", "Junior", None]
DateString = str  # Dates should be in the format '2025/01/31 00:00:00'
YesNo = Literal["Yes", "No"]
YN = Literal["Y", "N"]
YNOrNA = Literal["Y", "N", "N/A"]


class Firm(TypedDict, total=False):
    firm_number: str
    firm_id: int
    ccms_firm_id: int | None
    parent_firm_id: int | None
    firm_name: str
    firm_type: FirmType
    constitutional_status: ConstitutionalStatus
    solicitor_advocate: YesNo | None
    advocate_level: AdvocateLevel
    bar_council_role: str | None
    company_house_number: str | None
    indemnity_received_date: str | None
    high_risk_supplier: YesNo | None
    hold_all_payments_flag: YN
    hold_reason: str
    non_profit_organisation: YNOrNA
    small_business_flag: YN
    women_owned_flag: YN
    website_url: str
