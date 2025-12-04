import logging
from typing import Any, Dict, List, Optional, Union

import requests
from pydantic import ValidationError
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from app.constants import YesNo
from app.models import BankAccount, Contact, Firm, Office
from app.pda.errors import ProviderDataApiError


class PDAError(ProviderDataApiError):
    """Base exception for Provider Data API errors."""

    pass


class PDAConnectionError(PDAError):
    """Raised when unable to connect to the Provider Data API."""

    pass


class ProviderDataApi:
    """
    Client for interacting with the Provider Data API.

    Provides methods to read provider firms, offices, users,
    and related data through a REST API.

    Will retry on unsuccessful requests.
    """

    RETRY_STRATEGY = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[429, 500, 502, 503, 504],
        raise_on_status=False,  # We'll handle status codes ourselves
    )

    def __init__(self):
        self.app = None
        self.base_url: Optional[str] = None
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self._initialized = False
        self._mock_fallback = None

    def init_app(self, app, base_url: str = None, api_key: str = None) -> None:
        """
        Initialize the API client with Flask app configuration.

        Args:
            app: Flask application instance
            base_url: Base URL for the Provider Data API
            api_key: API key for authentication

        Raises:
            ValueError: If base_url or api_key are not provided
        """
        if not base_url:
            raise ValueError("Must provide a base URL for the Provider Data API.")
        if not api_key:
            raise ValueError("Must provide an API key for the Provider Data API.")

        self.app = app
        self.base_url = base_url.rstrip("/")

        self.session.headers.update(
            {
                "X-Authorization": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        self._setup_session_adapter()

        if not hasattr(app, "extensions"):
            app.extensions = {}
        app.extensions["pda"] = self

        self._initialized = True
        self.logger.info(f"Provider Data API initialized with base URL: {self.base_url}")

    def _setup_session_adapter(self) -> None:
        """Setup HTTP adapter with retry strategy for the session."""
        adapter = HTTPAdapter(max_retries=self.RETRY_STRATEGY)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def test_connection(self) -> bool:
        """
        Test connection to the Provider Data API.

        Returns:
            bool: True if connection successful, False otherwise

        Raises:
            ProviderDataApiConnectionError: If connection fails
        """
        if not self._initialized:
            raise PDAError("API client not initialized. Call init_app() first.")

        try:
            response = self.get("/")  # TODO: See if we can get a better status endpoint
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to connect to Provider Data API: {e}")
            raise PDAConnectionError(f"Connection test failed: {e}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request to the API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            requests.Response: The response object

        Raises:
            ProviderDataApiError: If the request fails
        """
        if not self._initialized:
            raise PDAError("API client not initialized. Call init_app() first.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        if params := kwargs.get("params"):
            self.logger.debug(f"{method} request to {url} with params: {params}")
        else:
            self.logger.debug(f"{method} request to {url}")

        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.debug(f"Response: {response.status_code} from {url}")
            return response

        except requests.RequestException as e:
            self.logger.error(f"Request failed for {method} {url}: {e}")
            raise PDAError(f"Request failed: {e}")

    def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """
        Make a GET request to the specified endpoint.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            requests.Response: The response object
        """
        return self._make_request("GET", endpoint, params=params)

    def patch(self, endpoint: str, json: Dict[str, Any] = None) -> requests.Response:
        """
        Make a PATCH request to the specified endpoint.

        Args:
            endpoint: API endpoint path
            json: Data to be sent as JSON

        Returns:
            requests.Response: The response object
        """
        return self._make_request("PATCH", endpoint, json=json)

    def _handle_response(
        self, response: requests.Response, empty_return: Union[Dict, List, None]
    ) -> Union[Dict, List, None]:
        """
        Handle common response patterns.

        Args:
            response: The HTTP response
            empty_return: What to return for 204/404 responses

        Returns:
            Parsed JSON data, empty_return, or None

        Raises:
            ProviderDataApiError: For HTTP errors
        """
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                self.logger.error(f"Failed to parse JSON response: {e}")
                raise PDAError(f"Invalid JSON response: {e}")

        elif response.status_code in [204, 404]:
            # 204: No Content (successful but empty)
            # 404: Not Found (resource doesn't exist)
            self.logger.debug(f"Empty response ({response.status_code}) from {response.url}")
            return empty_return

        else:
            # Handle other HTTP errors
            self.logger.error(f"HTTP {response.status_code} error from {response.url}")
            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                raise PDAError(f"HTTP error: {e}")

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

        response = self.get(f"/provider-firms/{firm_id}")
        raw_data = self._handle_response(response, None)

        if raw_data is None:
            return None

        try:
            firm = raw_data.get("firm")
            return Firm(**firm)
        except ValidationError as e:
            self.logger.error(f"Invalid firm data from API for firm {firm_id}: {e}")
            raise PDAError(f"Invalid firm data: {e}")

    def get_all_provider_firms(self) -> List[Firm]:
        """
        Get all provider firms.

        Returns:
            List of Firm model instances
        """
        response = self.get("/provider-firms")
        raw_data = self._handle_response(response, [])

        if not raw_data:
            return []

        try:
            return [Firm(**firm_data) for firm_data in raw_data["firms"]]
        except ValidationError as e:
            self.logger.error(f"Invalid firms data from API: {e}")
            raise PDAError(f"Invalid firms data: {e}")

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

        response = self.get(f"/provider-offices/{office_code}")
        raw_data = self._handle_response(response, None)

        if raw_data is None:
            return None

        try:
            office = raw_data.get("office", raw_data)  # Handle both wrapped and direct responses
            return Office(**office)
        except ValidationError as e:
            self.logger.error(f"Invalid office data from API for office {office_code}: {e}")
            raise PDAError(f"Invalid office data: {e}")

    def get_provider_offices(self, firm_id: int) -> List[Office]:
        """
        Get all offices for a specific firm.

        Args:
            firm_id: The firm ID

        Returns:
            List of FirmOffice model instances
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        response = self.get(f"/provider-firms/{firm_id}/provider-offices")
        raw_data = self._handle_response(response, [])

        if not raw_data:
            return []

        try:
            offices_data = raw_data.get("offices", raw_data)  # Handle both wrapped and direct responses
            return [Office(**office_data) for office_data in offices_data]
        except ValidationError as e:
            self.logger.error(f"Invalid offices data from API for firm {firm_id}: {e}")
            raise PDAError(f"Invalid offices data: {e}")

    def get_head_office(self, firm_id: int) -> Office | None:
        """
        Gets the head office for a specific firm.

        Args:
            firm_id: The firm ID

        Returns:
            FirmOffice model instance for the head office, or None if not found
        """
        offices = self.get_provider_offices(firm_id)

        if not offices:
            return None

        for office in offices:
            # Child offices have headOffice = parent's office ID
            # Head offices have headOffice = "N/A"
            if office.head_office == "N/A":
                return office
        return None

    def get_provider_users(self, firm_id: int) -> List[Dict[str, Any]]:
        """
        Get all users for a specific firm.

        Args:
            firm_id: The firm ID (changed from str to int for consistency)

        Returns:
            List of dictionaries containing user details
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        response = self.get(f"/provider-firms/{firm_id}/provider-users")
        return self._handle_response(response, [])

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

        response = self.get(f"/provider-firms/{firm_id}/provider-offices/{office_code}/office-contract-details")
        return self._handle_response(response, {})

    def get_office_schedule_details(self, firm_id: int, office_code: str) -> Optional[Dict[str, Any]]:
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

        response = self.get(f"/provider-firms/{firm_id}/provider-offices/{office_code}/schedules")
        return self._handle_response(response, {})

    def get_office_bank_accounts(self, firm_id: int, office_code: str) -> List[BankAccount]:
        """
        Get bank details for a specific office.

        Args:
            firm_id: The firm ID
            office_code: The office code

        Returns:
            List of BankAccount model instances
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        response = self.get(f"/provider-firms/{firm_id}/provider-offices/{office_code}/bank-account-details")
        data = self._handle_response(response, [])
        bank_accounts = []
        if response:
            for bank_account in data:
                bank_accounts.append(BankAccount(**bank_account))
        return bank_accounts

    def patch_office(self, firm_id: int, office_code: str, fields_to_update: dict):
        response = self.patch(
            f"/provider-firms/{firm_id}/offices/{office_code}",
            json=fields_to_update,
        )
        return self._handle_response(response, {})

    def get_office_contacts(self, firm_id: int, office_code: str) -> List[Contact]:
        """
        Get all contacts for a specific office.

        Args:
            firm_id: The firm ID
            office_code: The office code

        Returns:
            List of Contact model instances

        Raises:
            NotImplementedError: This functionality is not yet supported by the real API
        """
        raise NotImplementedError("Getting office contacts is not yet supported by the real Provider Data API")

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
            NotImplementedError: This functionality is not yet supported by the real API
        """
        raise NotImplementedError("Creating office contacts is not yet supported by the real Provider Data API")

    def update_contact(self, firm_id: int, office_code: str, contact: Contact) -> Contact:
        """
        Update an existing contact.

        Args:
            firm_id: The firm ID
            office_code: The office code
            contact: Contact model instance with updated data

        Returns:
            Contact: The updated Contact model instance

        Raises:
            NotImplementedError: This functionality is not yet supported by the real API
        """
        raise NotImplementedError("Updating contacts is not yet supported by the real Provider Data API")

    def patch_provider(self, firm_id: int, fields_to_update: dict):
        response = self.patch(
            f"/provider-firms/{firm_id}",
            json=fields_to_update,
        )
        self._handle_response(response, {})
        return self.get_provider_firm(firm_id)

    def assign_bank_account_to_office(self, firm_id: int, office_code: str, bank_account_id: int) -> BankAccount:
        """
        Assign a bank account to a specific office.

        Args:
            firm_id: The firm ID that the office belongs to
            office_code: The office code
            bank_account_id: The bank account ID to assign the office to

        Returns:
        """
        raise NotImplementedError("Assigning bank account is not yet supported by the real Provider Data API")

    def get_bank_details(self, firm_id, bank_account_id: str) -> Optional[BankAccount]:
        response = self.get(f"/provider-firms/{firm_id}/bank-details/{bank_account_id}")
        data = self._handle_response(response, {})
        return BankAccount(**data)

    def get_provider_firm_bank_details(self, firm_id: int) -> List[BankAccount]:
        """
        Get all bank details for a specific provider.

        Args:
            firm_id: The id of the firm to get bank details for

        Returns:
            List[BankAccount]: List of bank accounts that belong to the given firm.
        """
        response = self.get(f"/provider-firms/{firm_id}/bank-account-details")
        items = self._handle_response(response, [])
        accounts = []
        for item in items:
            accounts.append(BankAccount(**item))
        return accounts

    def update_office_contact_details(self, firm_id, firm_office_code, payload):
        raise NotImplementedError("Update contact details has not been implemented yet")

    def add_bank_account_to_office(self, firm_id: int, office_code: str, bank_account: BankAccount) -> BankAccount:
        """
        Add a bank account to a specific office.

        Args:
            firm_id: Firm Id of the firm that the office belongs to
            office_code: The office code to add the bank account to
            bank_account: The bank account to add

        Returns:
            BankAccount: The bank account added to the given office
        """
        raise NotImplementedError("Adding bank account to an office is not yet supported by the real Provider Data API")

    def get_all_bank_accounts(self) -> List[BankAccount]:
        """
        Get all bank accounts.
        Returns: List[BankAccount]
        """
        raise NotImplementedError("Getting all bank accounts is currently not supported by the real Provider Data API")

    def update_provider_firm_name(self, firm_id: int, new_firm_name: str) -> Firm:
        """
        Update an existing firm name.
        Args:
            firm_id: The firm ID of the firm to update
            new_firm_name: The new firm name
        Returns: Firm
        """
        raise NotImplementedError("Updating provider firm name is not yet supported by the real API")

    def update_legal_service_provider_details(self, firm_id: int, data: dict):
        raise NotImplementedError(
            "Updating legal services provider details is not yet supported by the real Provider Data API"
        )

    def update_barrister_details(self, firm_id, barrister_details: dict) -> Firm:
        """
        Update an existing barrister details.
        Args:
            firm_id: Firm Id of the firm that the office belongs to
            barrister_details: A dict of fields to update

        Returns: Firm
        """
        raise NotImplementedError("Updating barrister details is currently not supported by the real Provider Data API")

    def update_advocate_details(self, firm_id, advocate_details: dict) -> Firm:
        """
        Update an existing advocate details.
        Args:
            firm_id: The advocate firm Id
            advocate_details: A dict of fields to update

        Returns: Firm
        """
        raise NotImplementedError("Updating advocate details is currently not supported by the real API")

    def update_office_false_balance(self, firm_id: int, office_code: str, data: dict) -> Office:
        """
        Update an existing office false balance.
        Args:
            firm_id: Firm Id of the firm that the office belongs to
            office_code: The code of the office to update
            data: a dict containing the office false balance

        Returns: Office
        """
        raise NotImplementedError(
            "Updating office false balance is currently not supported by the real Provider Data API"
        )

    def update_office_debt_referral(self, firm_id: int, office_code: str, debt_referral: YesNo) -> Office:
        """
        Update an existing office debt referral.
        Args:
            firm_id: The advocate firm Id
            office_code: The code of the office to update
            debt_referral: Yes | No

        Returns: Office
        """
        raise NotImplementedError("Updating office debt referral is currently not supported by the real API")
