import json
import logging
import os
import random
import string
import time
from datetime import date
from typing import Any, Dict, List, Optional
from unittest.mock import Mock

from pydantic import ValidationError

from app.constants import FirmType
from app.models import BankAccount, Contact, Firm, Office
from app.pda.errors import ProviderDataApiError


class MockPDAError(ProviderDataApiError):
    """Base exception for Mock Provider Data API errors."""

    pass


def _load_fixture(filepath: str) -> Dict[str, Any]:
    """Load a single fixture file."""
    with open(filepath, "r") as f:
        return json.load(f)


def _clean_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Remove fields that start with underscore from data."""
    return {k: v for k, v in data.items() if not k.startswith("_")}


def _generate_unique_office_code(existing_codes: List[str], max_attempts: int = 100) -> str:
    """Generate a unique office code that doesn't exist in the given list."""
    for _ in range(max_attempts):
        code = f"{random.randint(1, 9)}{random.choice(string.ascii_uppercase)}{random.randint(1, 999):03d}{random.choice(string.ascii_uppercase)}"
        if code not in existing_codes:
            return code
    raise MockPDAError(f"Could not generate unique office code after {max_attempts} attempts")


def _load_mock_data() -> Dict[str, Any]:
    """Load mock data from JSON fixture files."""
    fixtures_dir = os.path.join(os.path.dirname(__file__), "fixtures")

    # Load all fixture files - keep raw data with relationships
    providers_data = _load_fixture(os.path.join(fixtures_dir, "providers.json"))
    offices_data = _load_fixture(os.path.join(fixtures_dir, "offices.json"))
    contracts_data = _load_fixture(os.path.join(fixtures_dir, "contracts.json"))
    schedules_data = _load_fixture(os.path.join(fixtures_dir, "schedules.json"))
    bank_accounts_data = _load_fixture(os.path.join(fixtures_dir, "bank_accounts.json"))
    contacts_data = _load_fixture(os.path.join(fixtures_dir, "contacts.json"))

    # Store all data as-is for internal use
    return {
        "firms": providers_data.get("firms", []),
        "offices": offices_data.get("offices", []),
        "contracts": contracts_data.get("contracts", []),
        "schedules": schedules_data.get("schedules", []),
        "bank_accounts": bank_accounts_data.get("bank_accounts", []),
        "contacts": contacts_data.get("contacts", []),
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

    def _find_firm_data(self, firm_id: int) -> Optional[Dict[str, Any]]:
        """Find firm by firm_id."""
        for firm in self._mock_data["firms"]:
            if firm.get("firmId") == firm_id:
                return firm
        return None

    def init_app(self, app, base_url: str = None, api_key: str = None, **kwargs) -> None:
        """
        Initialize the mock API client with Flask app configuration.

        Args:
            app: Flask application instance
            base_url: Base URL for the Provider Data API (unused in mock)
            api_key: API key for authentication (unused in mock)
            **kwargs: Additional arguments (unused in mock)
        """
        self.app = app
        self.base_url = base_url.rstrip("/") if base_url else None

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["pda"] = self

        self._initialized = True
        self.logger.info("Mock Provider Data API initialized")

    def test_connection(self) -> bool:
        """
        Test connection to the Provider Data API.

        Returns:
            bool: Always True for mock implementation
        """
        if not self._initialized:
            raise MockPDAError("API client not initialized. Call init_app() first.")
        return True

    def get_provider_firm(self, firm_id: int) -> Firm | None:
        """
        Get details for a specific provider firm.

        Args:
            firm_id: The firm ID

        Returns:
            Firm model instance, or None if not found
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        for firm in self._mock_data["firms"]:
            if firm.get("firmId") == firm_id:
                try:
                    cleaned_firm = _clean_data(firm)
                    return Firm(**cleaned_firm)
                except ValidationError as e:
                    self.logger.error(f"Invalid firm data in mock for firm {firm_id}: {e}")
                    raise MockPDAError(f"Invalid firm data: {e}")
        return None

    def get_all_provider_firms(self) -> List[Firm]:
        """
        Get all provider firms.

        Returns:
            List of Firm model instances
        """
        try:
            cleaned_firms = [_clean_data(firm) for firm in self._mock_data["firms"]]
            return [Firm(**firm_data) for firm_data in cleaned_firms]
        except ValidationError as e:
            self.logger.error(f"Invalid firms data in mock: {e}")
            raise MockPDAError(f"Invalid firms data: {e}")

    def get_provider_office(self, office_code: str) -> Office | None:
        """
        Get details for a specific provider office.

        Args:
            office_code: The office code

        Returns:
            Office model instance, or None if not found
        """
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        for office in self._mock_data["offices"]:
            if office.get("firmOfficeCode") == office_code:
                try:
                    cleaned_office = _clean_data(office)
                    return Office(**cleaned_office)
                except ValidationError as e:
                    self.logger.error(f"Invalid office data in mock for office {office_code}: {e}")
                    raise MockPDAError(f"Invalid office data: {e}")
        return None

    def get_provider_offices(self, firm_id: int) -> List[Office]:
        """
        Get all offices for a specific firm.

        Args:
            firm_id: The firm ID

        Returns:
            List of Office model instances
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        filtered_offices = []
        for office in self._mock_data["offices"]:
            if office.get("_firmId") == firm_id:
                cleaned_office = _clean_data(office)
                filtered_offices.append(cleaned_office)

        if not filtered_offices:
            return []

        try:
            return [Office(**office_data) for office_data in filtered_offices]
        except ValidationError as e:
            self.logger.error(f"Invalid offices data in mock for firm {firm_id}: {e}")
            raise MockPDAError(f"Invalid offices data: {e}")

    def make_all_provider_offices_inactive(self, firm_id: int):
        offices = self.get_provider_offices(firm_id)
        for office in offices:
            # When need to update the office data in memory and not the office object
            item = self._find_office_data(firm_id, office.firm_office_code)
            item.update({"inactiveDate": date.today()})

    def get_head_office(self, firm_id: int) -> Office | None:
        """
        Gets the head office for a specific firm.

        Args:
            firm_id: The firm ID

        Returns:
            Office model instance for the head office, or None if not found
        """
        offices = self.get_provider_offices(firm_id)

        if not offices:
            return None

        for office in offices:
            # Child offices have headOffice = parent's office ID
            # Head offices have headOffice = "N/A"
            if office.get_is_head_office():
                return office
        return None

    def get_provider_users(self, firm_id: int) -> List[Dict[str, Any]]:
        """
        Get all users for a specific firm.

        Args:
            firm_id: The firm ID

        Returns:
            List of dictionaries containing user details
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        # Return empty list if no users data exists for this firm
        return self._mock_data.get("users", {}).get(firm_id, [])

    def get_provider_children(self, firm_id: int, only_firm_type: FirmType | None = None) -> List[Firm]:
        """
        Get all firms for which the specified firm_id is their parentFirmId, optionally
        filtering to only include a specified firm type.

        Args:
            firm_id: The parent firm ID
            only_firm_type: Optional firm type.

        Returns:
            List of Firm model instances, which may be empty.
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        provider_children = []

        for firm in self._mock_data["firms"]:
            if firm.get("parentFirmId") == firm_id:
                try:
                    cleaned_firm = _clean_data(firm)
                    child_firm = Firm(**cleaned_firm)
                    if only_firm_type is None or child_firm.firm_type == only_firm_type:
                        provider_children.append(child_firm)
                except ValidationError as e:
                    self.logger.error(f"Invalid firm data in mock for firm {firm_id}: {e}")

        return provider_children

    def get_office_contract_details(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
        """
        Get contract details for a specific office.

        Args:
            firm_id: The firm ID
            office_code: The office code

        Returns:
            Dict containing contract details
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            return {}

        firm = self.get_provider_firm(firm_id)
        office = self.get_provider_office(office_code)

        if not firm or not office:
            return None

        contracts = []
        office_id = office_data.get("firmOfficeId")
        for contract in self._mock_data["contracts"]:
            if contract.get("_firmOfficeId") == office_id:
                cleaned_contract = _clean_data(contract)
                contracts.append(cleaned_contract)

        return contracts

    def get_office_schedule_details(self, firm_id: int, office_code: str) -> list[Optional[Dict[str, Any]]]:
        """
        Get schedule details for a specific office.

        Args:
            firm_id: The firm ID
            office_code: The office code

        Returns:
            Dict containing schedule details
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            return None

        firm = self.get_provider_firm(firm_id)
        office = self.get_provider_office(office_code)

        if not firm or not office:
            return {}

        schedules = []
        office_id = office_data.get("firmOfficeId")
        for schedule in self._mock_data["schedules"]:
            if schedule.get("_firmOfficeId") == office_id:
                cleaned_schedule = _clean_data(schedule)
                schedules.append(cleaned_schedule)

        return schedules

    def get_office_bank_details(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
        """
        Get bank details for a specific office.

        Args:
            firm_id: The firm ID
            office_code: The office code

        Returns:
            Dict containing bank details
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            return {}

        firm = self.get_provider_firm(firm_id)
        office = self.get_provider_office(office_code)

        if not firm or not office:
            return {}

        # Mock bank details - you can expand this based on your fixture data structure
        return {
            "firm": firm.to_api_dict(),
            "office": office.to_api_dict(),
            "bankDetails": [],  # Add mock bank details here if needed
        }

    def update_office_payment_method(self, firm_id: int, office_code: str, payment_method: str) -> Office:
        """
        Update the payment method for an office.

        Args:
            firm_id: The firm ID
            office_code: The office code
            payment_method: The new payment method value (e.g., "Electronic" or "Cheque")

        Returns:
            Office: The updated Office model instance

        Raises:
            ProviderDataApiError: If the office doesn't exist
            ValueError: If parameters are invalid
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")
        if not payment_method or not isinstance(payment_method, str):
            raise ValueError("payment_method must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            raise MockPDAError(f"Office {office_code} not found for firm {firm_id}")

        # Update payment method using API/camelCase field name
        office_data["paymentMethod"] = payment_method

        # Return updated Office model
        try:
            cleaned_office = _clean_data(office_data)
            return Office(**cleaned_office)
        except ValidationError as e:
            self.logger.error(f"Invalid office data in mock after payment method update for office {office_code}: {e}")
            raise MockPDAError(f"Invalid office data: {e}")

    def create_provider_firm(self, firm: Firm) -> Firm:
        """
        Create a new provider firm in the mock data.

        Args:
            firm: Firm model instance to create

        Returns:
            Firm: The created Firm model instance with assigned ID
        """
        # Generate a new firm ID
        existing_ids = [firm_data.get("firmId", 0) for firm_data in self._mock_data["firms"]]
        new_firm_id = max(existing_ids, default=0) + 1

        # Create a copy with the generated ID fields
        updated_firm = firm.model_copy(
            update={"firm_id": new_firm_id, "firm_number": str(new_firm_id), "ccms_firm_id": new_firm_id}
        )

        # Add to mock data
        self._mock_data["firms"].append(updated_firm.to_api_dict())

        return updated_firm

    def create_provider_office(self, office: Office, firm_id: int) -> Office:
        """
        Create a new provider office in the mock data.

        Args:
            office: Office model instance to create
            firm_id: ID of the firm this office belongs to

        Returns:
            Office: The created Office model instance with assigned ID
        """
        # Generate a new office ID
        existing_ids = [office_data.get("firmOfficeId", 0) for office_data in self._mock_data["offices"]]
        new_office_id = max(existing_ids, default=0) + 1

        # Generate unique office code
        existing_codes = [o.get("firmOfficeCode") for o in self._mock_data["offices"]]
        office_code = _generate_unique_office_code(existing_codes)

        # Create a copy with the generated ID fields
        updated_office = office.model_copy(update={"firm_office_id": new_office_id, "firm_office_code": office_code})

        updated_office_dict = updated_office.to_api_dict()
        updated_office_dict.update({"_firmId": firm_id})

        # Add to mock data
        self._mock_data["offices"].append(updated_office_dict)

        return updated_office

    def get_office_bank_accounts(self, firm_id: int, office_code: str) -> List[BankAccount]:
        """
        Get the bank account for a specific office (each office has only one bank account).

        Args:
            firm_id: The firm ID
            office_code: The office code

        Returns:
            List[BankAccount]: The bank accounts for a specific office
        """
        bank_accounts = []
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            return bank_accounts

        office_id = office_data.get("firmOfficeId")
        if not office_id:
            return bank_accounts

        # Find the bank account for this office
        for account in self._mock_data["bank_accounts"]:
            if account.get("vendorSiteId") == office_id:
                try:
                    bank_accounts.append(BankAccount(**account))
                except ValidationError as e:
                    self.logger.error(f"Invalid bank account data in mock for office {office_code}: {e}")
                    raise MockPDAError(f"Invalid bank account data: {e}")

        return bank_accounts

    def _get_firm_bank_details_raw(self, firm_id: int) -> dict:
        """
        Get the bank accounts for a specific provider firm.
        This is all bank accounts belonging to an office of the given provider firm.

        Args:
            firm_id: The firm ID of the given provider firm

        Returns:
            dict of bank account data, the bank account id will be used as the key
        """

        # Get all the offices belonging to the given firm.
        firm_offices = self.get_provider_offices(firm_id)
        firm_office_ids = [office.firm_office_id for office in firm_offices]

        # Find the bank account belonging to offices of the given firm.
        bank_accounts = self._mock_data["bank_accounts"]
        bank_accounts = {
            account["bankAccountId"]: account for account in bank_accounts if account["vendorSiteId"] in firm_office_ids
        }
        return bank_accounts

    def get_provider_firm_bank_details(self, firm_id: int) -> List[BankAccount]:
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        bank_accounts = self._get_firm_bank_details_raw(firm_id)
        return [BankAccount(**account) for account in bank_accounts.values()]

    def create_office_bank_account(self, firm_id: int, office_code: str, bank_account: BankAccount) -> BankAccount:
        """
        Create a bank account for an office.

        Args:
            firm_id: The firm ID
            office_code: The office code
            bank_account: BankAccount model instance to create

        Returns:
            BankAccount: The created BankAccount model instance

        Raises:
            ProviderDataApiError: If office doesn't exist or already has a bank account
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            raise MockPDAError(f"Office {office_code} not found for firm {firm_id}")

        office_id = office_data.get("firmOfficeId")

        # Deactivate all existing bank accounts currently attached to this office
        for account in self._mock_data["bank_accounts"]:
            if account["vendorSiteId"] == office_id:
                account["primaryFlag"] = "N"
                if not account.get("endDate"):
                    account["endDate"] = date.today()

        # Set the vendor_site_id to the office ID
        updated_account = bank_account.model_copy(
            update={
                "vendor_site_id": office_id,
                "start_date": date.today(),
                "primary_flag": "Y",
            }
        )

        # Add to mock data
        self._mock_data["bank_accounts"].append(updated_account.to_api_dict())

        return updated_account

    def update_office_bank_account(self, firm_id: int, office_code: str, bank_account: BankAccount) -> BankAccount:
        """
        Update the bank account for an office.

        Args:
            firm_id: The firm ID
            office_code: The office code
            bank_account: BankAccount model instance with updated data

        Returns:
            BankAccount: The updated BankAccount model instance

        Raises:
            ProviderDataApiError: If office or bank account doesn't exist
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            raise MockPDAError(f"Office {office_code} not found for firm {firm_id}")

        office_id = office_data.get("firmOfficeId")

        # Find and update the bank account
        for i, account in enumerate(self._mock_data["bank_accounts"]):
            if account.get("vendorSiteId") == office_id:
                updated_account = bank_account.model_copy(update={"vendor_site_id": office_id})
                self._mock_data["bank_accounts"][i] = updated_account.to_api_dict()
                return updated_account

        raise MockPDAError(f"Bank account not found for office {office_code}")

    def get_office_contacts(self, firm_id: int, office_code: str) -> List[Contact]:
        """
        Get all contacts for a specific office.

        Args:
            firm_id: The firm ID
            office_code: The office code

        Returns:
            List of Contact model instances
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            return []

        office_id = office_data.get("firmOfficeId")
        if not office_id:
            return []

        # Find all contacts for this office
        contacts = []
        for contact in self._mock_data["contacts"]:
            if contact.get("vendorSiteId") == office_id:
                try:
                    contacts.append(Contact(**contact))
                except ValidationError as e:
                    self.logger.error(f"Invalid contact data in mock for office {office_code}: {e}")
                    raise MockPDAError(f"Invalid contact data: {e}")

        return contacts

    def create_office_contact(self, firm_id: int, office_code: str, contact: Contact) -> Contact:
        """
        Create a contact for an office.

        Args:
            firm_id: The firm ID
            office_code: The office code
            contact: Contact model instance to create

        Returns:
            Contact: The created Contact model instance

        Raises:
            ProviderDataApiError: If office doesn't exist
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        office_data = self._find_office_data(firm_id, office_code)
        if office_data is None:
            raise MockPDAError(f"Office {office_code} not found for firm {firm_id}")

        office_id = office_data.get("firmOfficeId")

        # Generate a new contact ID
        existing_ids = [contact_data.get("contactId", 0) for contact_data in self._mock_data["contacts"]]
        new_contact_id = max(existing_ids, default=0) + 1

        # Set the vendor_site_id to the office ID and creation_date to today in ISO format
        updates = {"vendor_site_id": office_id, "contact_id": new_contact_id}
        if not contact.creation_date:
            updates["creation_date"] = date.today()

        updated_contact = contact.model_copy(update=updates)

        # Add to mock data
        self._mock_data["contacts"].append(updated_contact.to_api_dict())

        return updated_contact

    def patch_office(self, firm_id: int, office_code: str, fields_to_update: dict) -> Office:
        office = self._find_office_data(firm_id, office_code)
        if office:
            office.update(fields_to_update)
        return office

    def patch_provider_firm(self, firm_id: int, fields_to_update: dict):
        firm = self.get_provider_firm(firm_id)
        if firm:
            firm = self._update_provider_firm(firm, fields_to_update)
            if "inactiveDate" in fields_to_update and fields_to_update["inactiveDate"]:
                self.make_all_provider_offices_inactive(firm_id)

        return firm

    def _update_provider_firm(self, firm: Firm, fields_to_update: dict):
        # Get the raw firm data from storage
        firm_dict = None
        for item in self._mock_data["firms"]:
            if item.get("firmId") == firm.firm_id:
                firm_dict = item
                break

        if firm_dict:
            firm_dict.update(fields_to_update)

        # Return updated firm as a Firm instance
        return self.get_provider_firm(firm.firm_id)

    def update_contact(self, firm_id: int, office_code: str, contact: Contact) -> Contact:
        """
        Update an existing contact.

        Args:
            firm_id: The firm ID
            office_code: The office code
            contact: Contact model instance with updated data (must have contact_id set)

        Returns:
            Contact: The updated Contact model instance

        Raises:
            ProviderDataApiError: If contact doesn't exist
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")
        if not contact.contact_id:
            raise ValueError("contact must have contact_id set")

        # Find the contact in mock data by contact_id
        contact_index = None
        for i, existing_contact in enumerate(self._mock_data["contacts"]):
            if existing_contact.get("contactId") == contact.contact_id:
                contact_index = i
                break

        if contact_index is None:
            raise MockPDAError(f"Contact with contact_id {contact.contact_id} not found")

        # Update the contact data
        self._mock_data["contacts"][contact_index] = contact.to_api_dict()

        return contact

    def patch_provider(self, firm_id: int, fields_to_update: dict):
        firm: dict = self._find_firm_data(firm_id)
        if not firm:
            raise ProviderDataApiError(f"Provider with firm {firm_id} not found")
        firm.update(fields_to_update)
        return firm

    def assign_bank_account_to_office(self, firm_id: int, office_code: str, bank_account_id: int) -> BankAccount:
        """
        Assign a bank account to a specific office. This creates a new bank account by duplicating the given bank account.

        Args:
            firm_id: The firm ID that the office belongs to
            office_code: The office code to assign the bank account to
            bank_account_id: The bank account ID to assign the office to

        Returns:
            BankAccount: The bank account that was assigned to the office
        """

        selected_bank_account = list(
            filter(lambda account: account["bankAccountId"] == int(bank_account_id), self._mock_data["bank_accounts"])
        )[0]
        # Copy the selected bank account
        copy_bank_account_data = selected_bank_account.copy()
        copy_bank_account_data.update(
            {
                "bankAccountId": int(time.time()),
                "startDate": date.today(),
                "endDate": None,
            }
        )
        new_bank_account = BankAccount(**copy_bank_account_data)

        # Create the new bank account and assign it to the office
        return self.create_office_bank_account(firm_id, office_code, new_bank_account)

    def update_office_contact_details(self, firm_id, firm_office_code, payload):
        office_data = self._find_office_data(firm_id, firm_office_code)
        office_data.update(payload)

    def add_bank_account_to_office(self, firm_id: int, office_code: str, bank_account: BankAccount) -> BankAccount:
        bank_account.bank_account_id = int(time.time())
        return self.create_office_bank_account(firm_id, office_code, bank_account)

    def get_all_bank_accounts(self) -> List[BankAccount]:
        # Get all bank accounts
        bank_accounts = []
        for account in self._mock_data["bank_accounts"]:
            bank_accounts.append(BankAccount(**account))
        return bank_accounts

    def update_provider_firm_name(self, firm_id: int, new_firm_name: str) -> Firm:
        firm_data = self._find_firm_data(firm_id)
        firm_data.update({"firmName": new_firm_name})
        return Firm(**firm_data)

    def update_legal_service_provider_details(self, firm_id: int, data: dict) -> Firm:
        firm_details = self._find_firm_data(firm_id)
        firm_details.update(data)
        return Firm(**firm_details)

    def update_barrister_details(self, firm_id, barrister_details: dict) -> Firm:
        firm_details = self._find_firm_data(firm_id)
        firm_details.update(barrister_details)
        return Firm(**firm_details)

    def update_advocate_details(self, firm_id, advocate_details: dict) -> Firm:
        firm_details = self._find_firm_data(firm_id)
        firm_details.update(advocate_details)
        return Firm(**firm_details)

    def update_office_false_balance(self, firm_id: int, office_code: str, data: dict) -> Office:
        return self.patch_office(firm_id, office_code, data)

    def update_office_debt_recovery(self, firm_id: int, office_code: str, data: dict) -> Office:
        office_data = self._find_office_data(firm_id, office_code)
        office_data.update(data)
        return Office(**_clean_data(office_data))

    def get_list_of_contract_manager_names(self):
        # Static list of 12 fake contract managers
        return [
            {"name": "Alice Johnson"},
            {"name": "Robert Smith"},
            {"name": "Sarah Wilson"},
            {"name": "Michael Brown"},
            {"name": "Emma Davis"},
            {"name": "Lewis Green"},
            {"name": "Olivia Garcia"},
            {"name": "William Martinez"},
            {"name": "Sophia Anderson"},
            {"name": "David Taylor"},
            {"name": "Isabella Thomas"},
            {"name": "Christopher Lee"},
        ]
