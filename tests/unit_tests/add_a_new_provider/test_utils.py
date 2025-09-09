import pytest
from flask import get_flashed_messages

from app.main.utils import add_new_provider
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
