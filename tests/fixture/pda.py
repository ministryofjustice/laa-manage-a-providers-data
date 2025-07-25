"""This is a basic mock as a proof of concept, a full mock will be developed as a subsequent ticket."""

from unittest.mock import MagicMock


class MockPDA(MagicMock):
    def init_app(self, app, **kwargs):
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["pda"] = self


def mock_provider_data_api():
    mock_api = MockPDA()

    mock_api.get_provider_firm.return_value = {"id": 1, "name": "Test Firm", "status": "active"}

    mock_api.get_all_provider_firms.return_value = {
        "firms": [{"firmId": 1, "firmName": "Test Firm 1"}, {"firmId": 2, "firmName": "Test Firm 2"}]
    }

    mock_api.get_provider_office.return_value = {"office": {"firmOfficeCode": "TEST001", "officeName": "Test Office 1"}}

    mock_api.get_provider_offices.return_value = {
        "firm": {"firmName": "Test Firm"},
        "offices": [
            {"firmOfficeCode": "TEST001", "officeName": "Test Office 1"},
            {"firmOfficeCode": "TEST002", "officeName": "Test Office 2"},
        ],
    }

    mock_api.get_provider_users.return_value = [{"id": 1, "name": "Test User", "email": "test@example.com"}]

    mock_api.get_office_contract_details.return_value = {
        "firm": {
            "firmId": 0,
            "firmName": "string",
        },
        "office": {
            "firmOfficeId": 0,
            "firmOfficeCode": "string",
            "officeName": "Test Office 1",
        },
        "contracts": [
            {
                "categoryOfLaw": "Family",
                "subCategoryLaw": "string",
                "authorisationType": "string",
                "newMatters": "string",
                "contractualDevolvedPowers": "string",
                "remainderAuthorisation": "string",
            }
        ],
    }

    mock_api.get_office_schedule_details.return_value = {
        "firm": {
            "firmNumber": "string",
            "firmId": 1,
            "ccmsFirmId": 0,
            "parentFirmId": 0,
            "firmName": "Test Firm 1",
            "firmType": "string",
            "constitutionalStatus": "string",
            "solicitorAdvocateYN": "string",
            "advocateLevel": "string",
            "barCouncilRoll": "string",
            "companyHouseNumber": "string",
        },
        "office": {
            "firmOfficeId": 0,
            "ccmsFirmOfficeId": 0,
            "firmOfficeCode": "string",
            "officeName": "Test Office 1",
            "officeCodeAlt": "string",
            "type": "string",
        },
        "pds": "true",
        "schedules": [
            {
                "contractType": "string",
                "contractDescription": "2022 Civil Contract",
                "contractNumber": "string",
                "contractReference": "string",
                "contractStatus": "string",
                "contractAuthorizationStatus": "string",
                "contractStartDate": "2025-07-22",
                "contractEndDate": "2025-07-22",
                "areaOfLaw": "string",
                "scheduleType": "string",
                "scheduleNumber": "string",
                "scheduleContractNumber": "string",
                "scheduleContractReference": "string",
                "scheduleAuthorizationStatus": "string",
                "scheduleStatus": "string",
                "scheduleStartDate": "2025-07-22",
                "scheduleEndDate": "2025-07-22",
                "scheduleLines": [
                    {
                        "areaOfLaw": "Family",
                        "categoryOfLaw": "string",
                        "description": "string",
                        "devolvedPowersStatus": "string",
                        "dpTypeOfChange": "string",
                        "dpReasonForChange": "string",
                        "dpDateOfChange": "string",
                        "remainderWorkFlag": "string",
                        "minimumCasesAllowedCount": "string",
                        "maximumCasesAllowedCount": "string",
                        "minimumToleranceCount": "string",
                        "maximumToleranceCount": "string",
                        "minimumLicenseCount": "string",
                        "maximumLicenseCount": "string",
                        "workInProgressCount": "string",
                        "outreach": "string",
                        "cancelFlag": "string",
                        "cancelReason": "string",
                        "cancelDate": "2025-07-22",
                        "closedDate": "2025-07-22",
                        "closedReason": "string",
                    }
                ],
                "nmsAuths": [
                    {
                        "description": "string",
                        "minMatterStarts": 0,
                        "maxMatterStarts": 0,
                        "authorisedLitigator": "string",
                        "supervision": "string",
                        "serviceCombinations": "string",
                        "typeOfPresence": "string",
                        "lawSocietyChildrenFlag": "string",
                        "advLawSocFamVioFlag": "string",
                        "advLawSocFamNoVioFlag": "string",
                        "resAccrSpecDomAbuseFlag": "string",
                        "resAccrSpecOtherFlag": "string",
                        "consortiaId": "string",
                        "authorisationStatus": "string",
                        "withdrawalType": "string",
                        "withdrawalReason": "string",
                        "attributeCategory": "string",
                    }
                ],
            }
        ],
    }

    mock_api.get_office_bank_details.return_value = {"account_number": "12345678", "bank_name": "Test Bank"}

    # Mock the status and init_app methods
    mock_api.status.return_value = None
    mock_api.init_app.return_value = None
    mock_api.base_url = "http://mock-api.test"

    return mock_api
