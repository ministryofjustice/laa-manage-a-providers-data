import json
import logging
import os
from typing import Any, Dict, List, Optional
from unittest.mock import Mock


class MockProviderDataApi:
    """
    Mock implementation of ProviderDataApi for local development.

    This class provides the same interface as ProviderDataApi but returns
    predefined mock data instead of making actual HTTP requests.
    """

    def __init__(self):
        self.app = None
        self.base_url: Optional[str] = None
        self.session = Mock()
        self.logger = logging.getLogger(__name__)
        self._initialized = False

        # Load mock data from fixtures
        self._mock_data = self._load_mock_data()

    def _load_mock_data(self) -> Dict[str, Any]:
        """Load mock data from JSON fixture file."""
        try:
            fixture_path = os.path.join(os.path.dirname(__file__), "..", "..", "tests", "fixtures", "providers.json")
            with open(fixture_path, "r") as f:
                data = json.load(f)

            # Convert to the expected format, using firmId as key
            mock_data = {
                "firms": {firm.get("firmId", firm.get("id", 0)): firm for firm in data.get("firms", [])},
                "offices": {office["office_code"]: office for office in data.get("offices", [])},
                "users": {user["firm_id"]: [user] for user in data.get("users", [])},
                "contract_details": {(cd["firm_id"], cd["office_code"]): cd for cd in data.get("contract_details", [])},
                "schedule_details": {(sd["firm_id"], sd["office_code"]): sd for sd in data.get("schedule_details", [])},
                "bank_details": {(bd["firm_id"], bd["office_code"]): bd for bd in data.get("bank_details", [])},
            }
            return mock_data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            self.logger.warning(f"Could not load mock data: {e}. Using sample data.")
            # Return some sample data for development
            return {
                "firms": {
                    1: {"firmId": 1, "firmName": "Sample Provider 1", "firmType": "Legal Services Provider"},
                    2: {"firmId": 2, "firmName": "Sample Provider 2", "firmType": "Legal Services Provider"},
                },
                "offices": {},
                "users": {},
                "contract_details": {},
                "schedule_details": {},
                "bank_details": {},
            }

    def init_app(self, app, base_url: str = None, api_key: str = None) -> None:
        if not base_url:
            raise ValueError("Must provide a base URL for the Provider Data API.")
        if not api_key:
            raise ValueError("Must provide an API key for the Provider Data API.")

        self.app = app
        self.base_url = base_url.rstrip("/")

        # Register as Flask extension
        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["pda"] = self

        self._initialized = True
        self.logger.info(f"Mock Provider Data API initialized with base URL: {self.base_url}")

    def get_provider_firm(self, firm_id: int) -> Optional[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        return {"firm": self._mock_data["firms"].get(firm_id, {})}

    def get_all_provider_firms(self) -> Dict[str, Any]:
        return {"firms": list(self._mock_data["firms"].values())}

    def get_provider_office(self, office_code: str) -> Optional[Dict[str, Any]]:
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        return {"offices": self._mock_data["offices"].get(office_code, {})}

    def get_provider_offices(self, firm_id: int) -> dict[str, Any]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        # Filter offices by firm_id
        offices = [office for office in self._mock_data["offices"].values() if office["firm_id"] == firm_id]

        firm = self.get_provider_firm(firm_id)["firm"]
        return {"firm": firm, "offices": offices}

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
