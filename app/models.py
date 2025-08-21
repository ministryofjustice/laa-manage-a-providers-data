from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .constants import YN, AdvocateLevel, ConstitutionalStatus, FirmType, YesNo, YNOrNA


class Firm(BaseModel):
    """Firm model

    Supports both snake_case (internal) and camelCase (API) field names.
    """

    model_config = ConfigDict(
        populate_by_name=True,  # Accept both snake_case AND camelCase
        str_strip_whitespace=True,  # Auto-strip whitespace from strings
        validate_assignment=True,  # Validate when fields are assigned
        extra="forbid",  # Don't allow extra fields
    )

    # Required fields
    firm_number: str = Field(alias="firmNumber", min_length=1, default=None)
    firm_id: int = Field(alias="firmId", gt=0, default=None)
    ccms_firm_id: int = Field(alias="ccmsFirmId", default=0)
    parent_firm_id: int = Field(alias="parentFirmId", default=0)
    firm_name: str = Field(alias="firmName", min_length=1, default=None)
    firm_type: FirmType = Field(alias="firmType", default=None)
    constitutional_status: ConstitutionalStatus = Field(alias="constitutionalStatus", default=None)
    solicitor_advocate: YesNo | None = Field(alias="solicitorAdvocateYN", default=None)
    advocate_level: Optional[AdvocateLevel] = Field(alias="advocateLevel", default=None)
    bar_council_roll: Optional[str] = Field(alias="barCouncilRoll", default=None)
    company_house_number: Optional[str] = Field(alias="companyHouseNumber", default=None)
    indemnity_received_date: str | None = Field(alias="indemnityReceivedDate", default=None)
    high_risk_supplier: Optional[YesNo] = Field(alias="highRiskSupplier", default=None)
    hold_all_payments_flag: YN = Field(alias="holdAllPaymentsFlag", default=None)
    hold_reason: str | None = Field(alias="holdReason", min_length=1, default=None)
    non_profit_organisation: YNOrNA = Field(alias="nonProfitOrganisation", default=None)
    small_business_flag: YN = Field(alias="smallBusinessFlag", default=None)
    women_owned_flag: YN = Field(alias="womenOwnedFlag", default=None)
    website_url: str | None = Field(alias="websiteUrl", min_length=1, default=None)

    def to_api_dict(self) -> dict:
        """Export as camelCase dictionary for API calls."""
        return self.model_dump(by_alias=True, exclude_none=True)

    def to_internal_dict(self) -> dict:
        """Export as snake_case dictionary for internal use."""
        return self.model_dump(by_alias=False, exclude_none=True)


class Office(BaseModel):
    """Office model

    Supports both snake_case (internal) and camelCase (API) field names.
    """

    model_config = ConfigDict(
        populate_by_name=True,  # Accept both snake_case AND camelCase
        str_strip_whitespace=True,  # Auto-strip whitespace from strings
        validate_assignment=True,  # Validate when fields are assigned
        extra="forbid",  # Don't allow extra fields
    )

    firm_office_id: int = Field(alias="firmOfficeId", default=0)
    ccms_firm_office_id: int = Field(alias="ccmsFirmOfficeId", default=0)
    firm_office_code: Optional[str] = Field(alias="firmOfficeCode", default=None)
    office_name: Optional[str] = Field(alias="officeName", default=None)
    office_code_alt: Optional[str] = Field(alias="officeCodeAlt", default=None)
    type: Optional[str] = Field(default=None)
    address_line_1: Optional[str] = Field(alias="addressLine1", default=None)
    address_line_2: Optional[str] = Field(alias="addressLine2", default=None)
    address_line_3: Optional[str] = Field(alias="addressLine3", default=None)
    address_line_4: Optional[str] = Field(alias="addressLine4", default=None)
    city: Optional[str] = Field(default=None)
    county: Optional[str] = Field(default=None)
    post_code: Optional[str] = Field(alias="postCode", default=None)
    dx_centre: Optional[str] = Field(alias="dxCentre", default=None)
    dx_number: Optional[str] = Field(alias="dxNumber", default=None)
    telephone_area_code: Optional[str] = Field(alias="telephoneAreaCode", default=None)
    telephone_number: Optional[str] = Field(alias="telephoneNumber", default=None)
    fax_area_code: Optional[str] = Field(alias="faxAreaCode", default=None)
    fax_number: Optional[str] = Field(alias="faxNumber", default=None)
    email_address: Optional[str] = Field(alias="emailAddress", default=None)
    vat_registration_number: Optional[str] = Field(alias="vatRegistrationNumber", default=None)
    head_office: Optional[str] = Field(alias="headOffice", default=None)
    creation_date: Optional[date] = Field(alias="creationDate", default=None)
    lsc_region: Optional[str] = Field(alias="lscRegion", default=None)
    lsc_bid_zone: Optional[str] = Field(alias="lscBidZone", default=None)
    lsc_area_office: Optional[str] = Field(alias="lscAreaOffice", default=None)
    cjs_force_name: Optional[str] = Field(alias="cjsForceName", default=None)
    local_authority: Optional[str] = Field(alias="localAuthority", default=None)
    police_station_area_name: Optional[str] = Field(alias="policeStationAreaName", default=None)
    duty_solicitor_area_name: Optional[str] = Field(alias="dutySolicitorAreaName", default=None)

    is_head_office: Optional[bool] = Field(
        default=False, exclude=True
    )  # Internal field that will be converted to head_office format when writing to PDA

    def to_api_dict(self) -> dict:
        """Export as camelCase dictionary for API calls."""
        return self.model_dump(by_alias=True, exclude_none=True)

    def to_internal_dict(self) -> dict:
        """Export as snake_case dictionary for internal use."""
        return self.model_dump(by_alias=False, exclude_none=True)
