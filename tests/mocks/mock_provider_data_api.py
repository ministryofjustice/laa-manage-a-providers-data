import logging
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

from tests.fixtures.loader import fixture_loader


class MockProviderDataApi:
    """
    Mock implementation of ProviderDataApi for testing purposes.

    This class provides the same interface as ProviderDataApi but returns
    predefined mock data instead of making actual HTTP requests.
    """

    def __init__(self):
        self.app = None
        self.base_url: Optional[str] = None
        self.session = Mock()
        self.logger = logging.getLogger(__name__)
        self._initialized = False

        # Mock data storage - load from JSON fixtures
        self._mock_data = fixture_loader.load_provider_data()

    def init_app(self, app, base_url: str = None, api_key: str = None) -> None:
        if not base_url:
            raise ValueError("Must provide a base URL for the Provider Data API.")
        if not api_key:
            raise ValueError("Must provide an API key for the Provider Data API.")

        self.app = app
        self.base_url = base_url.rstrip("/")
        self._initialized = True
        self.logger.info(f"Mock Provider Data API initialized with base URL: {self.base_url}")

    def get_provider_firm(self, firm_id: int) -> Optional[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        return self._mock_data["firms"].get(firm_id, {})

    def get_all_provider_firms(self) -> List[Dict[str, Any]]:
        return list(self._mock_data["firms"].values())

    def get_provider_office(self, office_code: str) -> Optional[Dict[str, Any]]:
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        return self._mock_data["offices"].get(office_code, {})

    def get_provider_offices(self, firm_id: int) -> List[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        # Filter offices by firm_id
        return [office for office in self._mock_data["offices"].values() if office["firm_id"] == firm_id]

    def get_provider_users(self, firm_id: int) -> List[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        return self._mock_data["users"].get(firm_id, [])

    def get_office_contract_details(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        return self._mock_data["contract_details"].get((firm_id, office_code), {})

    def get_office_schedule_details(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        return self._mock_data["schedule_details"].get((firm_id, office_code), {})

    def get_office_bank_details(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        return self._mock_data["bank_details"].get((firm_id, office_code), {})

    def add_mock_firm(self, firm_id: int, firm_data: Dict[str, Any]) -> None:
        """Add a mock firm to the test data."""
        self._mock_data["firms"][firm_id] = firm_data

    def add_mock_office(self, office_code: str, office_data: Dict[str, Any]) -> None:
        """Add a mock office to the test data."""
        self._mock_data["offices"][office_code] = office_data
