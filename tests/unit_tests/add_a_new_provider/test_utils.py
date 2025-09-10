import pytest
from flask import get_flashed_messages, session

from app.main.utils import add_new_provider, create_provider_from_session
from app.models import Firm
from app.pda.api import ProviderDataApi
from app.pda.mock_api import MockProviderDataApi


class TestAddNewProvider:
    @pytest.fixture(autouse=True)
    def setup_mock_api(self, app):
        """Ensure each test starts with a clean MockProviderDataApi."""
        with app.app_context():
            # Always ensure we have MockProviderDataApi for these tests
            from app.pda.mock_api import MockProviderDataApi

            mock_pda = MockProviderDataApi()
            mock_pda.init_app(app)
            app.extensions["pda"] = mock_pda

    def test_add_new_provider_success(self, app):
        """Test successfully adding a new provider."""
        with app.app_context():
            # Create a test firm
            firm = Firm(firm_name="TEST FIRM", firm_type="Legal Services Provider", constitutional_status="Partnership")

            # Call add_new_provider
            result = add_new_provider(firm)

            # Verify the result
            assert isinstance(result, Firm)
            assert result.firm_name == "TEST FIRM"
            assert result.firm_type == "Legal Services Provider"
            assert result.firm_id is not None
            assert result.firm_id > 0

    def test_add_new_provider_pda_not_initialized(self, app):
        """Test error when PDA is not initialized."""
        with app.app_context():
            # Remove PDA from extensions
            if "pda" in app.extensions:
                del app.extensions["pda"]

            firm = Firm(firm_name="TEST FIRM", firm_type="Legal Services Provider")

            with pytest.raises(RuntimeError, match="Provider Data API not initialized"):
                add_new_provider(firm)

    def test_add_new_provider_unsupported_api(self, app):
        """Test error when using real PDA (not mock)."""
        with app.app_context():
            # Replace mock PDA with real PDA
            real_pda = ProviderDataApi()
            app.extensions["pda"] = real_pda

            firm = Firm(firm_name="TEST FIRM", firm_type="Legal Services Provider")

            with pytest.raises(RuntimeError, match="Provider Data API does not support this functionality yet"):
                add_new_provider(firm)

    def test_add_new_provider_preserves_firm_data(self, app):
        """Test that all firm data is preserved during creation."""
        with app.app_context():
            # Verify we're using MockProviderDataApi
            pda = app.extensions.get("pda")
            assert isinstance(pda, MockProviderDataApi), f"Expected MockProviderDataApi, got {type(pda)}"

            firm = Firm(
                firm_name="COMPREHENSIVE TEST FIRM",
                firm_type="Chambers",
                constitutional_status="Limited Company",
                website_url="https://example.com",
                small_business_flag="Y",
                women_owned_flag="Y",
            )

            result = add_new_provider(firm)

            # Verify all fields are preserved
            assert result.firm_name == "COMPREHENSIVE TEST FIRM"
            assert result.firm_type == "Chambers"
            assert result.constitutional_status == "Limited Company"
            assert result.website_url == "https://example.com"
            assert result.small_business_flag == "Y"
            assert result.women_owned_flag == "Y"
            # New fields should be assigned
            assert result.firm_id is not None
            assert result.firm_number is not None
            assert result.ccms_firm_id is not None

    def test_add_new_provider_shows_success_flash(self, app):
        """Test that success flash message is shown when provider is created."""
        with app.app_context():
            firm = Firm(
                firm_name="TEST FLASH FIRM", firm_type="Legal Services Provider", constitutional_status="Partnership"
            )

            # Call add_new_provider
            add_new_provider(firm)

            # Verify flash message was added
            messages = get_flashed_messages(with_categories=True)
            assert len(messages) == 1
            category, message = messages[0]
            assert category == "success"
            assert message == "<b>New legal services provider successfully created</b>"


class TestCreateProviderFromSession:
    @pytest.fixture(autouse=True)
    def setup_mock_api(self, app):
        """Ensure each test starts with a clean MockProviderDataApi."""
        with app.app_context():
            from app.pda.mock_api import MockProviderDataApi

            mock_pda = MockProviderDataApi()
            mock_pda.init_app(app)
            app.extensions["pda"] = mock_pda

    def test_create_provider_from_session_no_session_data(self, app):
        """Test that function returns None when no session data exists."""
        with app.test_request_context():
            result = create_provider_from_session()
            assert result is None

    def test_create_provider_from_session_firm_only(self, app):
        """Test creating provider with only firm data in session."""
        with app.test_request_context():
            # Set up firm session data
            session["new_provider"] = {
                "firm_name": "Test Session Firm",
                "firm_type": "Legal Services Provider",
                "constitutional_status": "Limited Company",
            }

            result = create_provider_from_session()

            # Verify firm was created
            assert result is not None
            assert isinstance(result, Firm)
            assert result.firm_name == "Test Session Firm"
            assert result.firm_type == "Legal Services Provider"
            assert result.firm_id is not None

            # Verify session was cleaned up
            assert "new_provider" not in session

    def test_create_provider_from_session_with_office(self, app):
        """Test creating provider with firm and office data in session."""
        with app.test_request_context():
            # Set up session data
            session["new_provider"] = {
                "firm_name": "Test Firm With Office",
                "firm_type": "Legal Services Provider",
                "constitutional_status": "Partnership",
            }
            session["new_head_office"] = {
                "address_line_1": "123 Test Street",
                "city": "Test City",
                "postcode": "TE1 5ST",
                "telephone_number": "01234567890",
                "email_address": "test@example.com",
            }

            result = create_provider_from_session()

            # Verify firm was created
            assert result is not None
            assert result.firm_name == "Test Firm With Office"

            # Verify office was created
            pda = app.extensions["pda"]
            offices = pda.get_provider_offices(result.firm_id)
            assert len(offices) == 1
            office = offices[0]
            assert office.address_line_1 == "123 Test Street"
            assert office.city == "Test City"
            assert office.postcode == "TE1 5ST"

            # Verify sessions were cleaned up
            assert "new_provider" not in session
            assert "new_head_office" not in session

    def test_create_provider_from_session_with_bank_account(self, app):
        """Test creating provider with firm, office, and bank account data."""
        with app.test_request_context():
            # Set up session data
            session["new_provider"] = {
                "firm_name": "Test Firm With Bank",
                "firm_type": "Legal Services Provider",
                "constitutional_status": "Limited Company",
            }
            session["new_head_office"] = {
                "address_line_1": "456 Banking Street",
                "city": "Finance City",
                "postcode": "FC2 1BA",
                "telephone_number": "09876543210",
                "email_address": "finance@example.com",
            }
            session["new_head_office_bank_account"] = {
                "bank_account_name": "Test Business Account",
                "sort_code": "123456",
                "account_number": "87654321",
            }

            result = create_provider_from_session()

            # Verify firm was created
            assert result is not None
            assert result.firm_name == "Test Firm With Bank"

            # Verify office was created
            pda = app.extensions["pda"]
            offices = pda.get_provider_offices(result.firm_id)
            assert len(offices) == 1
            office = offices[0]
            assert office.address_line_1 == "456 Banking Street"

            # Verify bank account was created
            bank_account = pda.get_office_bank_account(result.firm_id, office.firm_office_code)
            assert bank_account is not None
            assert bank_account.bank_account_name == "Test Business Account"
            assert bank_account.sort_code == "123456"
            assert bank_account.account_number == "87654321"

            # Verify sessions were cleaned up
            assert "new_provider" not in session
            assert "new_head_office" not in session
            assert "new_head_office_bank_account" not in session

    def test_create_provider_from_session_partial_bank_data(self, app):
        """Test that bank account is created with partial data (only required fields)."""
        with app.test_request_context():
            # Set up session data with only required bank account fields
            session["new_provider"] = {
                "firm_name": "Test Partial Bank Firm",
                "firm_type": "Chambers",
                "constitutional_status": "Partnership",
            }
            session["new_head_office"] = {
                "address_line_1": "789 Partial Street",
                "city": "Incomplete City",
                "postcode": "IC3 2PA",
                "telephone_number": "01111111111",
                "email_address": "partial@example.com",
            }
            session["new_head_office_bank_account"] = {
                # Only required bank account data
                "bank_account_name": "Partial Account",
                "sort_code": "123456",
                "account_number": "87654321",
                # Missing optional fields like bank_name, bank_branch_name, etc.
            }

            result = create_provider_from_session()

            # Verify firm was created
            assert result is not None
            assert result.firm_name == "Test Partial Bank Firm"

            # Verify office was created
            pda = app.extensions["pda"]
            offices = pda.get_provider_offices(result.firm_id)
            assert len(offices) == 1
            office = offices[0]
            assert office.address_line_1 == "789 Partial Street"

            # Verify bank account was created with required fields only
            bank_account = pda.get_office_bank_account(result.firm_id, office.firm_office_code)
            assert bank_account is not None
            assert bank_account.bank_account_name == "Partial Account"
            assert bank_account.sort_code == "123456"
            assert bank_account.account_number == "87654321"
            # Optional fields should be None or defaults
            assert bank_account.bank_name is None
            assert bank_account.bank_branch_name is None

    def test_create_provider_from_session_no_bank_account_when_skipped(self, app):
        """Test that no bank account is created when user skipped the bank account step."""
        with app.test_request_context():
            # Set up session data without bank account session key (simulating skip)
            session["new_provider"] = {
                "firm_name": "Test Skip Bank Firm",
                "firm_type": "Legal Services Provider",
                "constitutional_status": "Partnership",
            }
            session["new_head_office"] = {
                "address_line_1": "789 Skip Street",
                "city": "Skip City",
                "postcode": "SK1 5IP",
                "telephone_number": "09876543210",
                "email_address": "skip@example.com",
            }
            # No new_head_office_bank_account session key (simulating skip)

            result = create_provider_from_session()

            # Verify firm was created
            assert result is not None
            assert result.firm_name == "Test Skip Bank Firm"

            # Verify office was created
            pda = app.extensions["pda"]
            offices = pda.get_provider_offices(result.firm_id)
            assert len(offices) == 1
            office = offices[0]
            assert office.address_line_1 == "789 Skip Street"

            # Verify no bank account was created (since skip was used)
            bank_account = pda.get_office_bank_account(result.firm_id, office.firm_office_code)
            assert bank_account is None
