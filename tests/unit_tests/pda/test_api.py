from unittest.mock import Mock

import pytest
import requests

from app.models import Firm, Office
from app.pda.api import PDAConnectionError, PDAError, ProviderDataApi


class TestProviderDataApi:
    @pytest.fixture
    def api_client(self):
        return ProviderDataApi()

    @pytest.fixture
    def mock_app(self):
        app = Mock()
        app.extensions = {}
        return app

    @pytest.fixture
    def initialized_client(self, api_client, mock_app):
        api_client.init_app(mock_app, base_url="https://mock.provider-data-api.com", api_key="test-key")
        return api_client

    def test_init_app_success(self, api_client, mock_app):
        api_client.init_app(mock_app, base_url="https://mock.provider-data-api.com", api_key="test-key")

        assert api_client.base_url == "https://mock.provider-data-api.com"
        assert api_client._initialized
        assert mock_app.extensions["pda"] == api_client
        assert api_client.session.headers["X-Authorization"] == "test-key"

    def test_init_app_missing_base_url(self, api_client, mock_app):
        with pytest.raises(ValueError, match="Must provide a base URL"):
            api_client.init_app(mock_app, base_url=None, api_key="test-key")

    def test_init_app_missing_api_key(self, api_client, mock_app):
        with pytest.raises(ValueError, match="Must provide an API key"):
            api_client.init_app(mock_app, base_url="https://mock.provider-data-api.com", api_key=None)

    def test_test_connection_success(self, initialized_client):
        mock_response = Mock()
        mock_response.status_code = 200
        initialized_client.session.request = Mock(return_value=mock_response)

        result = initialized_client.test_connection()

        assert result is True

    def test_test_connection_failure(self, initialized_client):
        initialized_client.session.request = Mock(side_effect=requests.RequestException("Connection failed"))

        with pytest.raises(PDAConnectionError):
            initialized_client.test_connection()

    def test_test_connection_not_initialized(self, api_client):
        with pytest.raises(PDAError, match="API client not initialized"):
            api_client.test_connection()

    def test_make_request_success(self, initialized_client):
        mock_response = Mock()
        initialized_client.session.request = Mock(return_value=mock_response)

        result = initialized_client._make_request("GET", "/test")

        assert result == mock_response

    def test_make_request_failure(self, initialized_client):
        initialized_client.session.request = Mock(side_effect=requests.RequestException("Request failed"))

        with pytest.raises(PDAError):
            initialized_client._make_request("GET", "/test")

    def test_handle_response_200(self, initialized_client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value"}

        result = initialized_client._handle_response(mock_response, {})

        assert result == {"key": "value"}

    def test_handle_response_204(self, initialized_client):
        mock_response = Mock()
        mock_response.status_code = 204

        result = initialized_client._handle_response(mock_response, [])

        assert result == []

    def test_handle_response_404(self, initialized_client):
        mock_response = Mock()
        mock_response.status_code = 404

        result = initialized_client._handle_response(mock_response, None)

        assert result is None

    def test_handle_response_http_error(self, initialized_client):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError("Server Error")

        with pytest.raises(PDAError):
            initialized_client._handle_response(mock_response, {})

    def test_get_provider_firm_success(self, initialized_client):
        initialized_client.get = Mock(return_value=Mock(status_code=200))
        mock_firm = {
            "firmId": 123,
            "constitutionalStatus": "Charity",
        }
        initialized_client._handle_response = Mock(return_value={"firm": mock_firm})

        result = initialized_client.get_provider_firm(123)

        initialized_client.get.assert_called_once_with("/provider-firms/123")
        assert result == Firm(**mock_firm)

    def test_get_provider_firm_invalid_id(self, initialized_client):
        with pytest.raises(ValueError, match="firm_id must be a positive integer"):
            initialized_client.get_provider_firm(-1)

    def test_get_all_provider_firms(self, initialized_client):
        initialized_client.get = Mock(return_value=Mock(status_code=200))
        mock_firm = {
            "firmId": 123,
            "constitutionalStatus": "Charity",
        }
        initialized_client._handle_response = Mock(return_value={"firms": [mock_firm]})

        result = initialized_client.get_all_provider_firms()

        initialized_client.get.assert_called_once_with("/provider-firms")
        assert result == [Firm(**mock_firm)]

    def test_get_provider_office_success(self, initialized_client):
        initialized_client.get = Mock(return_value=Mock(status_code=200))
        initialized_client._handle_response = Mock(return_value={"firm_office_code": "1A234B"})

        result = initialized_client.get_provider_office("1A234B")

        initialized_client.get.assert_called_once_with("/provider-offices/1A234B")
        assert result == Office(firm_office_code="1A234B")

    def test_get_provider_office_invalid_code(self, initialized_client):
        with pytest.raises(ValueError, match="office_code must be a non-empty string"):
            initialized_client.get_provider_office("")

    def test_get_provider_offices(self, initialized_client):
        initialized_client.get = Mock(return_value=Mock(status_code=200))
        initialized_client._handle_response = Mock(return_value={"offices": [{"firm_office_code": "1A234B"}]})

        result = initialized_client.get_provider_offices(123)

        initialized_client.get.assert_called_once_with("/provider-firms/123/provider-offices")
        assert result == [Office(firm_office_code="1A234B")]

    def test_get_provider_users(self, initialized_client):
        initialized_client.get = Mock(return_value=Mock(status_code=200))
        initialized_client._handle_response = Mock(return_value=[{"user_id": 1}])

        result = initialized_client.get_provider_users(123)

        initialized_client.get.assert_called_once_with("/provider-firms/123/provider-users")
        assert result == [{"user_id": 1}]

    def test_get_office_contract_details(self, initialized_client):
        initialized_client.get = Mock(return_value=Mock(status_code=200))
        initialized_client._handle_response = Mock(return_value={"contract_id": "1A234B"})

        result = initialized_client.get_office_contract_details(123, "1A234B")

        initialized_client.get.assert_called_once_with(
            "/provider-firms/123/provider-offices/1A234B/office-contract-details"
        )
        assert result == {"contract_id": "1A234B"}

    def test_get_office_schedule_details(self, initialized_client):
        initialized_client.get = Mock(return_value=Mock(status_code=200))
        initialized_client._handle_response = Mock(return_value={"scheduleId": "456"})

        result = initialized_client.get_office_schedule_details(123, "1A234B")

        initialized_client.get.assert_called_once_with("/provider-firms/123/provider-offices/1A234B/schedules")
        assert result == {"scheduleId": "456"}

    def test_get_office_bank_details(self, initialized_client):
        initialized_client.get = Mock(return_value=Mock(status_code=200))
        initialized_client._handle_response = Mock(return_value={"accountNumber": "12345678"})

        result = initialized_client.get_office_bank_details(123, "1A234B")

        initialized_client.get.assert_called_once_with(
            "/provider-firms/123/provider-offices/1A234B/bank-account-details"
        )
        assert result == {"accountNumber": "12345678"}
