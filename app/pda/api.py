import logging
from typing import Any, Dict, List, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry


class ProviderDataApiError(Exception):
    """Base exception for Provider Data API errors."""

    pass


class ProviderDataApiConnectionError(ProviderDataApiError):
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
            raise ProviderDataApiError("API client not initialized. Call init_app() first.")

        try:
            response = self.get("/")  # TODO: See if we can get a better status endpoint
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to connect to Provider Data API: {e}")
            raise ProviderDataApiConnectionError(f"Connection test failed: {e}")

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
            raise ProviderDataApiError("API client not initialized. Call init_app() first.")

        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        self.logger.debug(f"{method} request to {url} with args: {kwargs}")

        try:
            response = self.session.request(method, url, **kwargs)
            self.logger.debug(f"Response: {response.status_code} from {url}")
            return response

        except requests.RequestException as e:
            self.logger.error(f"Request failed for {method} {url}: {e}")
            raise ProviderDataApiError(f"Request failed: {e}")

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
                raise ProviderDataApiError(f"Invalid JSON response: {e}")

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
                raise ProviderDataApiError(f"HTTP error: {e}")

    def get_provider_firm(self, firm_id: int) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific provider firm.

        Args:
            firm_id: The firm ID

        Returns:
            Dict containing firm details, or None if not found
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        response = self.get(f"/provider-firms/{firm_id}")
        return self._handle_response(response, {})

    def get_all_provider_firms(self) -> List[Dict[str, Any]]:
        """
        Get all provider firms.

        Returns:
            List of dictionaries containing firm details
        """
        response = self.get("/provider-firms")
        return self._handle_response(response, [])

    def get_provider_office(self, office_code: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific provider office.

        Args:
            office_code: The office code

        Returns:
            Dict containing office details, or None if not found
        """
        if not office_code or not isinstance(office_code, str):
            raise ValueError("office_code must be a non-empty string")

        response = self.get(f"/provider-offices/{office_code}")
        return self._handle_response(response, {})

    def get_provider_offices(self, firm_id: int) -> List[Dict[str, Any]]:
        """
        Get all offices for a specific firm.

        Args:
            firm_id: The firm ID

        Returns:
            List of dictionaries containing office details
        """
        if not isinstance(firm_id, int) or firm_id <= 0:
            raise ValueError("firm_id must be a positive integer")

        response = self.get(f"/provider-firms/{firm_id}/provider-offices")
        return self._handle_response(response, [])

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

        response = self.get(f"/provider-firms/{firm_id}/provider-offices/{office_code}/bank-account-details")
        return self._handle_response(response, {})
