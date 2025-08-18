from unittest.mock import Mock, patch

import pytest

from app.pda.mock_api import MockProviderDataApi, _clean_data, _load_fixture, _load_mock_data


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
        ]

        result = _load_mock_data()

        expected = {
            "firms": [{"firmId": 1}],
            "offices": [{"officeId": 101}],
            "contracts": [{"contractId": 1}],
            "schedules": [{"scheduleId": 1}],
        }
        assert result == expected
        assert mock_load_fixture.call_count == 4


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

        assert result == {"firm": {"firmId": 1, "firmName": "Test Firm"}}

    def test_get_provider_firm_not_found(self, mock_api):
        mock_api._mock_data = {"firms": [{"firmId": 1, "firmName": "Test Firm"}]}

        result = mock_api.get_provider_firm(999)

        assert result == {"firm": {}}

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

        expected = {"firms": [{"firmId": 1, "firmName": "Test Firm"}, {"firmId": 2, "firmName": "Other Firm"}]}
        assert result == expected

    def test_get_provider_office_success(self, mock_api):
        mock_api._mock_data = {
            "offices": [{"firmOfficeCode": "1A001L", "officeName": "Test Office", "_secret": "data"}]
        }

        result = mock_api.get_provider_office("1A001L")

        assert result == {"office": {"firmOfficeCode": "1A001L", "officeName": "Test Office"}}

    def test_get_provider_office_not_found(self, mock_api):
        mock_api._mock_data = {"offices": []}

        result = mock_api.get_provider_office("NONEXISTENT")

        assert result == {"office": {}}

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

        expected = {
            "firm": {"firmId": 1, "firmName": "Test Firm"},
            "offices": [{"firmOfficeCode": "1A001L"}, {"firmOfficeCode": "1A002L"}],
        }
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

        expected = {
            "firm": {"firmId": 1, "firmName": "Test Firm"},
            "office": {"firmOfficeCode": "1A001L", "firmOfficeId": 101},
            "contracts": [{"categoryOfLaw": "MAT"}],
        }
        assert result == expected

    def test_get_office_contract_details_office_not_found(self, mock_api):
        mock_api._mock_data = {"firms": [], "offices": [], "contracts": []}

        result = mock_api.get_office_contract_details(1, "NONEXISTENT")

        assert result == {"firm": {}, "office": {}, "contracts": []}

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

        expected = {
            "firm": {"firmId": 1, "firmName": "Test Firm"},
            "office": {"firmOfficeCode": "1A001L", "firmOfficeId": 101},
            "pds": True,
            "schedules": [{"contractType": "Standard"}],
        }
        assert result == expected

    def test_get_office_schedule_details_office_not_found(self, mock_api):
        mock_api._mock_data = {"firms": [], "offices": [], "schedules": []}

        result = mock_api.get_office_schedule_details(1, "NONEXISTENT")

        assert result == {"firm": {}, "office": {}, "pds": True, "schedules": []}

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
        mock_load_data.return_value = {"firms": [], "offices": [], "contracts": [], "schedules": []}

        MockProviderDataApi()

        mock_load_data.assert_called_once()
