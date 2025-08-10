import json
import logging
import os
from typing import Any, Dict, List, Optional
from unittest.mock import Mock


def _load_fixture(filepath: str) -> Dict[str, Any]:
    """Load a single fixture file."""
    with open(filepath, "r") as f:
        return json.load(f)


def _clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove fields that start with underscore from data."""
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _load_mock_data() -> Dict[str, Any]:
    """Load mock data from JSON fixture files."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")

    # Load all fixture files - keep raw data with relationships
    providers_data = _load_fixture(os.path.join(fixtures_dir, "providers.json"))
    offices_data = _load_fixture(os.path.join(fixtures_dir, "offices.json"))
    contracts_data = _load_fixture(os.path.join(fixtures_dir, "contracts.json"))
    schedules_data = _load_fixture(os.path.join(fixtures_dir, "schedules.json"))

    # Store all data as-is for internal use
    return {
        "firms": providers_data.get("firms", []),
        "offices": offices_data.get("offices", []),
        "contracts": contracts_data.get("contracts", []),
        "schedules": schedules_data.get("schedules", []),
    }


class MockProviderDataApi:
    """
    Mock implementation of the Provider Data API for local development and testing.

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
        self._mock_data = _load_mock_data()

    def _find_office_data(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
        """Find office by firm_id and office_code."""
        for office in self._mock_data["offices"]:
            if office.get("_firmId") == firm_id and office.get("firmOfficeCode") == office_code:
                return office
        return None

    def init_app(self, app, base_url: str = None, **kwargs) -> None:
        self.app = app
        self.base_url = base_url.rstrip("/") if base_url else None

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["pda"] = self

        self._initialized = True
        self.logger.info("Mock Provider Data API initialized")

    def get_provider_firm(self, firm_id: int) -> Optional[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        for firm in self._mock_data["firms"]:
            if firm.get("firmId") == firm_id:
                return {"firm": _clean_data(firm)}
        return {"firm": {}}

    def get_all_provider_firms(self) -> Dict[str, Any]:
        cleaned_firms = [_clean_data(firm) for firm in self._mock_data["firms"]]
        return {"firms": cleaned_firms}

    def get_provider_office(self, office_code: str) -> Optional[Dict[str, Any]]:
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        for office in self._mock_data["offices"]:
            if office.get("firmOfficeCode") == office_code:
                return {"office": _clean_data(office)}
        return {"office": {}}

    def get_provider_offices(self, firm_id: int) -> dict[str, Any]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        filtered_offices = []
        for office in self._mock_data["offices"]:
            if office.get("_firmId") == firm_id:
                cleaned_office = _clean_data(office)
                filtered_offices.append(cleaned_office)

        firm = self.get_provider_firm(firm_id)["firm"]
        return {"firm": firm, "offices": filtered_offices}

    def get_provider_users(self, firm_id: int) -> List[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        return self._mock_data["users"].get(firm_id, [])

    def get_office_contract_details(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            return {"firm": {}, "office": {}, "contracts": []}

        firm_data = self.get_provider_firm(firm_id)["firm"]
        cleaned_office = _clean_data(office_data)

        contracts = []
        office_id = office_data.get("firmOfficeId")
        for contract in self._mock_data["contracts"]:
            if contract.get("_firmOfficeId") == office_id:
                cleaned_contract = _clean_data(contract)
                contracts.append(cleaned_contract)

        return {"firm": firm_data, "office": cleaned_office, "contracts": contracts}

    def get_office_schedule_details(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            return {"firm": {}, "office": {}, "pds": True, "schedules": []}

        firm_data = self.get_provider_firm(firm_id)["firm"]
        cleaned_office = _clean_data(office_data)

        schedules = []
        office_id = office_data.get("firmOfficeId")
        for schedule in self._mock_data["schedules"]:
            if schedule.get("_firmOfficeId") == office_id:
                cleaned_schedule = _clean_data(schedule)
                schedules.append(cleaned_schedule)

        return {"firm": firm_data, "office": cleaned_office, "pds": True, "schedules": schedules}
