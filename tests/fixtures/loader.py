import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class FixtureLoader:
    """Utility class for loading test fixture data from JSON files."""

    def __init__(self, base_path: Optional[str] = None):
        if base_path is None:
            # Default to the fixtures directory relative to this file
            self.base_path = Path(__file__).parent
        else:
            self.base_path = Path(base_path)

    def load_json(self, filename: str) -> Dict[str, Any]:
        """Load JSON data from a file."""
        file_path = self.base_path / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Fixture file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in fixture file {filename}: {e}")

    def load_provider_data(self) -> Dict[str, Any]:
        """Load the default provider data from individual JSON files."""
        try:
            firms = self.load_json("provider_data/firms.json")
            offices = self.load_json("provider_data/offices.json")
            users = self.load_json("provider_data/users.json")
            contract_details = self.load_json("provider_data/contract_details.json")
            schedule_details = self.load_json("provider_data/schedule_details.json")
            bank_details = self.load_json("provider_data/bank_details.json")

            return {
                "firms": {int(k): v for k, v in firms.items()},  # Convert string keys to int
                "offices": offices,
                "users": {int(k): v for k, v in users.items()},  # Convert string keys to int
                "contract_details": self._convert_contract_keys(contract_details),
                "schedule_details": self._convert_schedule_keys(schedule_details),
                "bank_details": self._convert_bank_keys(bank_details),
            }
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Failed to load default provider data: {e}")

    def _load_scenario_data(self, scenario: str) -> Dict[str, Any]:
        """Load data for a specific test scenario."""
        scenario_file = f"provider_data/scenarios/{scenario}.json"
        return self.load_json(scenario_file)

    def _convert_contract_keys(self, contract_details: Dict[str, Any]) -> Dict[tuple, Any]:
        """Convert contract detail keys from 'firm_id_office_code' to (firm_id, office_code) tuples."""
        converted = {}
        for key, value in contract_details.items():
            parts = key.split("_", 1)  # Split on first underscore only
            if len(parts) == 2:
                firm_id = int(parts[0])
                office_code = parts[1]
                converted[(firm_id, office_code)] = value
        return converted

    def _convert_schedule_keys(self, schedule_details: Dict[str, Any]) -> Dict[tuple, Any]:
        """Convert schedule detail keys from 'firm_id_office_code' to (firm_id, office_code) tuples."""
        return self._convert_contract_keys(schedule_details)  # Same logic

    def _convert_bank_keys(self, bank_details: Dict[str, Any]) -> Dict[tuple, Any]:
        """Convert bank detail keys from 'firm_id_office_code' to (firm_id, office_code) tuples."""
        return self._convert_contract_keys(bank_details)  # Same logic

    def get_firm_by_id(self, firm_id: int, scenario: str = "default") -> Optional[Dict[str, Any]]:
        """Get a specific firm by ID."""
        data = self.load_provider_data(scenario)
        return data["firms"].get(firm_id)

    def get_offices_by_firm(self, firm_id: int, scenario: str = "default") -> List[Dict[str, Any]]:
        """Get all offices for a specific firm."""
        data = self.load_provider_data(scenario)
        return [office for office in data["offices"].values() if office["firm_id"] == firm_id]

    def get_users_by_firm(self, firm_id: int, scenario: str = "default") -> List[Dict[str, Any]]:
        """Get all users for a specific firm."""
        data = self.load_provider_data(scenario)
        return data["users"].get(firm_id, [])

    def create_custom_dataset(
        self,
        firms: Optional[Dict[int, Dict]] = None,
        offices: Optional[Dict[str, Dict]] = None,
        users: Optional[Dict[int, List[Dict]]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create a custom dataset by overriding default data."""
        base_data = self.load_provider_data("default")

        if firms:
            base_data["firms"].update(firms)
        if offices:
            base_data["offices"].update(offices)
        if users:
            base_data["users"].update(users)

        # Allow overriding other data types
        for key, value in kwargs.items():
            if key in base_data:
                if isinstance(value, dict):
                    base_data[key].update(value)
                else:
                    base_data[key] = value

        return base_data


fixture_loader = FixtureLoader()
