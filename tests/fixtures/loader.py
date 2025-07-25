import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class FixtureLoader:
    """Utility class for loading test fixture data from JSON files."""

    def __init__(self):
        self.base_path = Path(__file__).parent

    def load_json(self, filename: str) -> Dict[str, Any]:
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
            firms = self.load_json("provider_data/providers.json")

            return {"firms": firms.items()}
        except (FileNotFoundError, ValueError) as e:
            raise RuntimeError(f"Failed to load default provider data: {e}")

    def get_firm_by_id(self, firm_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific firm by ID."""
        data = self.load_provider_data()
        return data["firms"].get(firm_id)

    def get_offices_by_firm(self, firm_id: int) -> List[Dict[str, Any]]:
        """Get all offices for a specific firm."""
        data = self.load_provider_data()
        return [office for office in data["offices"].values() if office["firm_id"] == firm_id]

    def get_users_by_firm(self, firm_id: int) -> List[Dict[str, Any]]:
        """Get all users for a specific firm."""
        data = self.load_provider_data()
        return data["users"].get(firm_id, [])


fixture_loader = FixtureLoader()
