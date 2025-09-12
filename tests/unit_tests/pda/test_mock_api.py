from unittest.mock import Mock, patch

import pytest

from app.models import BankAccount, Contact, Firm, Office
from app.pda.mock_api import (
    MockProviderDataApi,
    ProviderDataApiError,
    _clean_data,
    _generate_unique_office_code,
    _load_fixture,
    _load_mock_data,
)


class TestDataLoadFunctions:
    def test_clean_data_removes_underscore_fields(self):
        data = {"_firmId": 1, "firmId": 101, "firmName": "Test Firm", "_internal": "secret"}

        cleaned = _clean_data(data)

        assert cleaned == {"firmId": 101, "firmName": "Test Firm"}
        assert "_firmId" not in cleaned
        assert "_internal" not in cleaned

    def test_clean_data_empty_dict(self):
        assert _clean_data({}) == {}

    def test_clean_data_no_underscore_fields(self):
        data = {"firmId": 1, "firmName": "Test"}
        assert _clean_data(data) == data

    @patch("builtins.open")
    @patch("json.load")
    def test_load_fixture_success(self, mock_json_load, mock_open):
        mock_json_load.return_value = {"test": "data"}

        result = _load_fixture("/path/to/fixture.json")

        mock_open.assert_called_once_with("/path/to/fixture.json", "r")
        mock_json_load.assert_called_once()
        assert result == {"test": "data"}

    @patch("app.pda.mock_api._load_fixture")
    @patch("os.path.join")
    @patch("os.path.dirname")
    def test_load_mock_data_success(self, mock_dirname, mock_path_join, mock_load_fixture):
        # Mock the path construction
        mock_dirname.return_value = "/app/pda"
        mock_path_join.side_effect = lambda *args: "/".join(args)

        # Mock fixture loading
        mock_load_fixture.side_effect = [
            {"firms": [{"firmId": 1}]},  # providers.json
            {"offices": [{"officeId": 101}]},  # offices.json
            {"contracts": [{"contractId": 1}]},  # contracts.json
            {"schedules": [{"scheduleId": 1}]},  # schedules.json
            {"bank_accounts": [{"vendorSiteId": 101}]},  # bank_accounts.json
            {"contacts": [{"vendorSiteId": 101}]},  # contacts.json
        ]

        result = _load_mock_data()

        expected = {
            "firms": [{"firmId": 1}],
            "offices": [{"officeId": 101}],
            "contracts": [{"contractId": 1}],
            "schedules": [{"scheduleId": 1}],
            "bank_accounts": [{"vendorSiteId": 101}],
            "contacts": [{"vendorSiteId": 101}],  # contacts.json
        }
        assert result == expected
        assert mock_load_fixture.call_count == 6

    def test_generate_unique_office_code(self):
        """Test generation of unique office code."""
        existing_codes = ["1A001L", "2R006L"]

        code = _generate_unique_office_code(existing_codes)

        assert len(code) == 6
        assert code[0].isdigit()
        assert code[1].isupper()
        assert code[2:5].isdigit()
        assert code[5].isupper()
        assert code not in existing_codes

    def test_generate_unique_office_code_max_attempts(self):
        """Test error when max attempts reached."""
        with (
            patch("app.pda.mock_api.random.randint", return_value=1),
            patch("app.pda.mock_api.random.choice", return_value="A"),
        ):
            existing_codes = ["1A001A"]

            with pytest.raises(ProviderDataApiError):
                _generate_unique_office_code(existing_codes, max_attempts=5)


class TestMockProviderDataApi:
    @pytest.fixture
    def mock_api(self):
        return MockProviderDataApi()

    @pytest.fixture
    def mock_app(self):
        app = Mock()
        app.extensions = {}
        return app

    def test_init_sets_up_mock_data(self, mock_api):
        assert mock_api.app is None
        assert mock_api.base_url is None
        assert hasattr(mock_api, "_mock_data")
        assert mock_api._initialized is False

    def test_init_app_success(self, mock_api, mock_app):
        mock_api.init_app(mock_app, base_url="https://test.com")

        assert mock_api.app == mock_app
        assert mock_api.base_url == "https://test.com"
        assert mock_api._initialized is True
        assert mock_app.extensions["pda"] == mock_api

    def test_init_app_without_base_url(self, mock_api, mock_app):
        mock_api.init_app(mock_app)

        assert mock_api.base_url is None
        assert mock_api._initialized is True

    def test_find_office_data_success(self, mock_api):
        mock_api._mock_data = {
            "offices": [
                {"_firmId": 1, "firmOfficeCode": "1A001L", "officeName": "Test Office"},
                {"_firmId": 2, "firmOfficeCode": "2R006L", "officeName": "Other Office"},
            ]
        }

        result = mock_api._find_office_data(1, "1A001L")

        assert result == {"_firmId": 1, "firmOfficeCode": "1A001L", "officeName": "Test Office"}

    def test_find_office_data_not_found(self, mock_api):
        mock_api._mock_data = {"offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "officeName": "Test Office"}]}

        result = mock_api._find_office_data(1, "NONEXISTENT")

        assert result is None

    def test_get_provider_firm_success(self, mock_api):
        mock_api._mock_data = {
            "firms": [
                {"firmId": 1, "firmName": "Test Firm", "_internal": "secret"},
                {"firmId": 2, "firmName": "Other Firm"},
            ]
        }

        result = mock_api.get_provider_firm(1)

        assert result == Firm(firm_id=1, firm_name="Test Firm")

    def test_get_provider_firm_not_found(self, mock_api):
        mock_api._mock_data = {"firms": [{"firmId": 1, "firmName": "Test Firm"}]}

        result = mock_api.get_provider_firm(999)

        assert result is None

    def test_get_provider_firm_invalid_id(self, mock_api):
        with pytest.raises(ValueError, match="firm_id must be a positive integer"):
            mock_api.get_provider_firm(0)

        with pytest.raises(ValueError, match="firm_id must be a positive integer"):
            mock_api.get_provider_firm(-1)

    def test_get_all_provider_firms(self, mock_api):
        mock_api._mock_data = {
            "firms": [
                {"firmId": 1, "firmName": "Test Firm", "_internal": "secret"},
                {"firmId": 2, "firmName": "Other Firm", "_other": "hidden"},
            ]
        }

        result = mock_api.get_all_provider_firms()

        expected = [Firm(**{"firmId": 1, "firmName": "Test Firm"}), Firm(**{"firmId": 2, "firmName": "Other Firm"})]
        assert result == expected

    def test_get_provider_office_success(self, mock_api):
        mock_api._mock_data = {
            "offices": [{"firmOfficeCode": "1A001L", "officeName": "Test Office", "_secret": "data"}]
        }

        result = mock_api.get_provider_office("1A001L")

        assert result == Office(**{"firmOfficeCode": "1A001L", "officeName": "Test Office"})

    def test_get_provider_office_not_found(self, mock_api):
        mock_api._mock_data = {"offices": []}

        result = mock_api.get_provider_office("NONEXISTENT")

        assert result is None

    def test_get_provider_office_invalid_code(self, mock_api):
        with pytest.raises(ValueError, match="office_code must be a non-empty string"):
            mock_api.get_provider_office("")

        with pytest.raises(ValueError, match="office_code must be a non-empty string"):
            mock_api.get_provider_office(None)

    def test_get_provider_offices_success(self, mock_api):
        mock_api._mock_data = {
            "firms": [{"firmId": 1, "firmName": "Test Firm"}],
            "offices": [
                {"_firmId": 1, "firmOfficeCode": "1A001L", "_secret": "data"},
                {"_firmId": 2, "firmOfficeCode": "2R006L"},
                {"_firmId": 1, "firmOfficeCode": "1A002L", "_hidden": "value"},
            ],
        }

        result = mock_api.get_provider_offices(1)

        expected = [Office(**{"firmOfficeCode": "1A001L"}), Office(**{"firmOfficeCode": "1A002L"})]
        assert result == expected

    def test_get_provider_offices_invalid_firm_id(self, mock_api):
        with pytest.raises(ValueError, match="firm_id must be a positive integer"):
            mock_api.get_provider_offices(0)

    def test_get_office_contract_details_success(self, mock_api):
        mock_api._mock_data = {
            "firms": [{"firmId": 1, "firmName": "Test Firm"}],
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "contracts": [
                {"_firmOfficeId": 101, "categoryOfLaw": "MAT", "_internal": "secret"},
                {"_firmOfficeId": 102, "categoryOfLaw": "HOU"},
            ],
        }

        result = mock_api.get_office_contract_details(1, "1A001L")

        expected = [{"categoryOfLaw": "MAT"}]
        assert result == expected

    def test_get_office_contract_details_office_not_found(self, mock_api):
        mock_api._mock_data = {"firms": [], "offices": [], "contracts": []}

        result = mock_api.get_office_contract_details(1, "NONEXISTENT")

        assert result == {}

    def test_get_office_schedule_details_success(self, mock_api):
        mock_api._mock_data = {
            "firms": [{"firmId": 1, "firmName": "Test Firm"}],
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "schedules": [
                {"_firmOfficeId": 101, "contractType": "Standard", "_private": "data"},
                {"_firmOfficeId": 102, "contractType": "Other"},
            ],
        }

        result = mock_api.get_office_schedule_details(1, "1A001L")

        expected = [{"contractType": "Standard"}]
        assert result == expected

    def test_get_office_schedule_details_office_not_found(self, mock_api):
        mock_api._mock_data = {"firms": [], "offices": [], "schedules": []}

        result = mock_api.get_office_schedule_details(1, "NONEXISTENT")

        assert result is None

    def test_get_provider_users_success(self, mock_api):
        mock_api._mock_data = {"users": {1: [{"userId": 1, "name": "John"}], 2: [{"userId": 2, "name": "Jane"}]}}

        result = mock_api.get_provider_users(1)

        assert result == [{"userId": 1, "name": "John"}]

    def test_get_provider_users_no_users(self, mock_api):
        mock_api._mock_data = {"users": {}}

        result = mock_api.get_provider_users(1)

        assert result == []

    def test_get_provider_users_invalid_firm_id(self, mock_api):
        with pytest.raises(ValueError, match="firm_id must be a positive integer"):
            mock_api.get_provider_users(-1)

    @patch("app.pda.mock_api._load_mock_data")
    def test_load_mock_data_called_on_init(self, mock_load_data):
        mock_load_data.return_value = {
            "firms": [],
            "offices": [],
            "contracts": [],
            "schedules": [],
            "bank_accounts": [],
        }

        MockProviderDataApi()

        mock_load_data.assert_called_once()

    def test_create_provider_firm_basic(self, mock_api):
        """Test creating a basic provider firm."""
        # Create a Firm instance
        firm_data = Firm(
            firm_name="TEST FIRM", firm_type="Legal Services Provider", constitutional_status="Partnership"
        )

        # Create a new firm
        new_firm = mock_api.create_provider_firm(firm_data)

        # Verify the firm was created
        assert new_firm.firm_name == "TEST FIRM"
        assert new_firm.firm_type == "Legal Services Provider"
        assert new_firm.firm_id > 0

        # Verify we can retrieve it
        retrieved_firm = mock_api.get_provider_firm(new_firm.firm_id)
        assert retrieved_firm is not None
        assert retrieved_firm.firm_name == "TEST FIRM"

    def test_create_provider_firm_with_all_fields(self, mock_api):
        """Test creating a firm with all optional fields."""
        firm_data = Firm(
            firm_name="COMPREHENSIVE TEST FIRM",
            firm_type="Chambers",
            constitutional_status="Limited Company",
            website_url="https://example.com",
            small_business_flag="Y",
            women_owned_flag="Y",
        )

        new_firm = mock_api.create_provider_firm(firm_data)

        assert new_firm.firm_name == "COMPREHENSIVE TEST FIRM"
        assert new_firm.firm_type == "Chambers"
        assert new_firm.constitutional_status == "Limited Company"
        assert new_firm.website_url == "https://example.com"
        assert new_firm.small_business_flag == "Y"
        assert new_firm.women_owned_flag == "Y"

    def test_create_multiple_firms_get_unique_ids(self, mock_api):
        """Test that multiple firms get unique IDs."""
        firm1_data = Firm(firm_name="FIRM ONE", firm_type="Legal Services Provider")
        firm1 = mock_api.create_provider_firm(firm1_data)

        firm2_data = Firm(firm_name="FIRM TWO", firm_type="Chambers")
        firm2 = mock_api.create_provider_firm(firm2_data)

        assert firm1.firm_id != firm2.firm_id
        assert firm2.firm_id > firm1.firm_id

    def test_create_provider_office(self, mock_api):
        """Test creating an office generates valid code."""
        office_data = Office(office_name="Test Office", city="London")

        new_office = mock_api.create_provider_office(office_data, firm_id=1)

        assert new_office.office_name == "Test Office"
        assert new_office.firm_office_id > 0
        assert len(new_office.firm_office_code) == 6

        # Check that the office is associated with the firm in mock data
        office_in_data = next(
            (o for o in mock_api._mock_data["offices"] if o["firmOfficeCode"] == new_office.firm_office_code), None
        )
        assert office_in_data["_firmId"] == 1

    def test_get_office_bank_account_success(self, mock_api):
        """Test getting a bank account for an office."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "bank_accounts": [
                {
                    "vendorSiteId": 101,
                    "bankName": "Test Bank",
                    "bankBranchName": "Test Branch",
                    "sortCode": "123456",
                    "accountNumber": "12345678",
                    "bankAccountName": "Test Account",
                    "currencyCode": "GBP",
                    "accountType": "Current Account",
                    "primaryFlag": "Y",
                    "country": "GB",
                }
            ],
        }

        result = mock_api.get_office_bank_account(1, "1A001L")

        assert result is not None
        assert result.vendor_site_id == 101
        assert result.bank_name == "Test Bank"
        assert result.sort_code == "123456"
        assert result.account_number == "12345678"

    def test_get_office_bank_account_not_found(self, mock_api):
        """Test getting a bank account when none exists."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "bank_accounts": [],
        }

        result = mock_api.get_office_bank_account(1, "1A001L")

        assert result is None

    def test_get_office_bank_account_office_not_found(self, mock_api):
        """Test getting a bank account when office doesn't exist."""
        mock_api._mock_data = {"offices": [], "bank_accounts": []}

        result = mock_api.get_office_bank_account(1, "NONEXISTENT")

        assert result is None

    def test_get_office_bank_account_invalid_params(self, mock_api):
        """Test validation of parameters."""
        with pytest.raises(ValueError, match="firm_id must be a positive integer"):
            mock_api.get_office_bank_account(0, "1A001L")

        with pytest.raises(ValueError, match="office_code must be a non-empty string"):
            mock_api.get_office_bank_account(1, "")

    def test_create_office_bank_account_success(self, mock_api):
        """Test creating a bank account for an office."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "bank_accounts": [],
        }

        bank_account = BankAccount(
            vendor_site_id=999,  # This should be overridden
            bank_name="New Bank",
            bank_branch_name="New Branch",
            sort_code="654321",
            account_number="87654321",
            bank_account_name="New Account",
            currency_code="GBP",
            account_type="Business Account",
            primary_flag="Y",
            country="GB",
        )

        result = mock_api.create_office_bank_account(1, "1A001L", bank_account)

        assert result.vendor_site_id == 101  # Should be set to office ID
        assert result.bank_name == "New Bank"
        assert len(mock_api._mock_data["bank_accounts"]) == 1

    def test_create_office_bank_account_office_not_found(self, mock_api):
        """Test creating bank account when office doesn't exist."""
        mock_api._mock_data = {"offices": [], "bank_accounts": []}

        bank_account = BankAccount(
            vendor_site_id=101,
            bank_name="Test Bank",
            bank_branch_name="Test Branch",
            sort_code="123456",
            account_number="12345678",
            bank_account_name="Test Account",
        )

        with pytest.raises(ProviderDataApiError, match="Office NONEXISTENT not found"):
            mock_api.create_office_bank_account(1, "NONEXISTENT", bank_account)

    def test_create_office_bank_account_already_exists(self, mock_api):
        """Test creating bank account when one already exists."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "bank_accounts": [{"vendorSiteId": 101, "bankName": "Existing Bank"}],
        }

        bank_account = BankAccount(
            vendor_site_id=101,
            bank_name="New Bank",
            bank_branch_name="New Branch",
            sort_code="123456",
            account_number="12345678",
            bank_account_name="New Account",
        )

        with pytest.raises(ProviderDataApiError, match="Office 1A001L already has a bank account"):
            mock_api.create_office_bank_account(1, "1A001L", bank_account)

    def test_update_office_bank_account_success(self, mock_api):
        """Test updating a bank account for an office."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "bank_accounts": [
                {
                    "vendorSiteId": 101,
                    "bankName": "Old Bank",
                    "bankBranchName": "Old Branch",
                    "sortCode": "111111",
                    "accountNumber": "11111111",
                    "bankAccountName": "Old Account",
                    "currencyCode": "GBP",
                    "accountType": "Current Account",
                    "primaryFlag": "Y",
                    "country": "GB",
                }
            ],
        }

        updated_account = BankAccount(
            vendor_site_id=999,  # This should be overridden
            bank_name="Updated Bank",
            bank_branch_name="Updated Branch",
            sort_code="222222",
            account_number="22222222",
            bank_account_name="Updated Account",
            currency_code="GBP",
            account_type="Business Account",
            primary_flag="Y",
            country="GB",
        )

        result = mock_api.update_office_bank_account(1, "1A001L", updated_account)

        assert result.vendor_site_id == 101  # Should be set to office ID
        assert result.bank_name == "Updated Bank"
        assert result.sort_code == "222222"
        assert mock_api._mock_data["bank_accounts"][0]["bankName"] == "Updated Bank"

    def test_update_office_bank_account_not_found(self, mock_api):
        """Test updating bank account when none exists."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "bank_accounts": [],
        }

        bank_account = BankAccount(
            vendor_site_id=101,
            bank_name="Test Bank",
            bank_branch_name="Test Branch",
            sort_code="123456",
            account_number="12345678",
            bank_account_name="Test Account",
        )

        with pytest.raises(ProviderDataApiError, match="Bank account not found for office 1A001L"):
            mock_api.update_office_bank_account(1, "1A001L", bank_account)

    def test_update_office_bank_account_office_not_found(self, mock_api):
        """Test updating bank account when office doesn't exist."""
        mock_api._mock_data = {"offices": [], "bank_accounts": []}

        bank_account = BankAccount(
            vendor_site_id=101,
            bank_name="Test Bank",
            bank_branch_name="Test Branch",
            sort_code="123456",
            account_number="12345678",
            bank_account_name="Test Account",
        )

        with pytest.raises(ProviderDataApiError, match="Office NONEXISTENT not found"):
            mock_api.update_office_bank_account(1, "NONEXISTENT", bank_account)

    def test_get_office_contacts_success(self, mock_api):
        """Test getting contacts for an office."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "contacts": [
                {
                    "vendorSiteId": 101,
                    "firstName": "John",
                    "lastName": "Smith",
                    "emailAddress": "john.smith@example.com",
                    "telephoneNumber": "0123 456 7890",
                    "website": "https://www.example.com",
                    "jobTitle": "Liaison manager",
                    "primary": "Y",
                },
                {
                    "vendorSiteId": 101,
                    "firstName": "Jane",
                    "lastName": "Doe",
                    "emailAddress": "jane.doe@example.com",
                    "telephoneNumber": "0123 456 7891",
                    "website": None,
                    "jobTitle": "Liaison manager",
                    "primary": "N",
                },
                {
                    "vendorSiteId": 102,
                    "firstName": "Bob",
                    "lastName": "Brown",
                    "emailAddress": "bob.brown@example.com",
                    "jobTitle": "Liaison manager",
                    "primary": "Y",
                },
            ],
        }

        result = mock_api.get_office_contacts(1, "1A001L")

        assert len(result) == 2
        assert result[0].first_name == "John"
        assert result[0].primary == "Y"
        assert result[1].first_name == "Jane"
        assert result[1].primary == "N"

    def test_get_office_contacts_empty(self, mock_api):
        """Test getting contacts when none exist."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "contacts": [],
        }

        result = mock_api.get_office_contacts(1, "1A001L")

        assert result == []

    def test_get_office_contacts_office_not_found(self, mock_api):
        """Test getting contacts when office doesn't exist."""
        mock_api._mock_data = {"offices": [], "contacts": []}

        result = mock_api.get_office_contacts(1, "NONEXISTENT")

        assert result == []

    def test_get_office_contacts_invalid_params(self, mock_api):
        """Test validation of parameters."""
        with pytest.raises(ValueError, match="firm_id must be a positive integer"):
            mock_api.get_office_contacts(0, "1A001L")

        with pytest.raises(ValueError, match="office_code must be a non-empty string"):
            mock_api.get_office_contacts(1, "")

    def test_create_office_contact_success(self, mock_api):
        """Test creating a contact for an office."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "contacts": [],
        }

        contact = Contact(
            vendor_site_id=999,  # This should be overridden
            first_name="Jane",
            last_name="Doe",
            email_address="jane.doe@example.com",
            telephone_number="0987 654 3210",
            website="https://www.test.example",
            job_title="Liaison manager",
            primary="Y",
        )

        result = mock_api.create_office_contact(1, "1A001L", contact)

        assert result.vendor_site_id == 101  # Should be set to office ID
        assert result.first_name == "Jane"
        assert result.primary == "Y"
        assert len(mock_api._mock_data["contacts"]) == 1

    def test_create_office_contact_multiple_allowed(self, mock_api):
        """Test creating multiple contacts for the same office."""
        mock_api._mock_data = {
            "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101}],
            "contacts": [
                {
                    "vendorSiteId": 101,
                    "firstName": "John",
                    "lastName": "Smith",
                    "emailAddress": "john.smith@example.com",
                    "jobTitle": "Liaison manager",
                    "primary": "Y",
                }
            ],
        }

        contact = Contact(
            vendor_site_id=101,
            first_name="Jane",
            last_name="Doe",
            email_address="jane.doe@example.com",
            job_title="Liaison manager",
            primary="N",
        )

        result = mock_api.create_office_contact(1, "1A001L", contact)

        assert result.first_name == "Jane"
        assert result.primary == "N"
        assert len(mock_api._mock_data["contacts"]) == 2

    def test_create_office_contact_office_not_found(self, mock_api):
        """Test creating contact when office doesn't exist."""
        mock_api._mock_data = {"offices": [], "contacts": []}

        contact = Contact(
            vendor_site_id=101,
            first_name="John",
            last_name="Smith",
            email_address="john.smith@example.com",
            job_title="Liaison manager",
            primary="Y",
        )

        with pytest.raises(ProviderDataApiError, match="Office NONEXISTENT not found"):
            mock_api.create_office_contact(1, "NONEXISTENT", contact)

    def test_create_office_contact_invalid_params(self, mock_api):
        """Test validation of parameters for create contact."""
        contact = Contact(
            vendor_site_id=101,
            first_name="Test",
            last_name="User",
            email_address="test@example.com",
            job_title="Liaison manager",
            primary="Y",
        )

        with pytest.raises(ValueError, match="firm_id must be a positive integer"):
            mock_api.create_office_contact(0, "1A001L", contact)

        with pytest.raises(ValueError, match="office_code must be a non-empty string"):
            mock_api.create_office_contact(1, "", contact)
