import logging

import requests

logger = logging.getLogger(__name__)


class ProviderDataApi:
    def __init__(self):
        self.app = None
        self.base_url = None
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)

    def init_app(self, app, base_url: str = None, api_key: str = None) -> None:
        self.app = app
        if not base_url:
            raise ValueError("Must provide a base URL for the Provider Data API.")
        if not api_key:
            raise ValueError("Must provide an API key for the Provider Data API.")
        self.base_url = base_url.rstrip("/")

        self.session.headers.update(
            {
                "X-Authorization": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

        app.extensions["pda"] = self

        self.status()  # Test the connection

    def _make_request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        logger.info(f"{method} - {url} - {kwargs}")

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            logger.error(f"PDA API request failed: {e}")
            raise

    def get(self, endpoint: str, params: dict[str, str] | None = None) -> requests.Response:
        return self._make_request("GET", endpoint, params=params)

    def status(self) -> None:
        """Attempts to connect to the PDA API, raises a ConnectionError if no connection can be established."""
        response = self.get("/")  # TODO: See if we can get a better status endpoint
        if response.status_code != 200:
            raise ConnectionError(f"Failed to establish connection to PDA API: {response}")

    def get_provider_firm(self, firm_id: int) -> dict[str, str] | None:
        response = self.get(f"/provider-firms/{firm_id}")
        if response.status_code == 204:
            return {}
        return response.json()

    def get_all_provider_firms(self) -> list[dict[str, str | None]]:
        response = self.get("/provider-firms")
        if response.status_code == 204:
            return []
        return response.json()

    def get_provider_office(self, office_code: str) -> dict[str, str | None]:
        response = self.get(f"/provider-offices/{office_code}")
        if response.status_code == 204:
            return {}
        return response.json()

    def get_provider_offices(self, firm_id: int) -> list[dict[str, str | None]]:
        response = self.get(f"/provider-firms/{firm_id}/provider-offices")
        if response.status_code == 204:
            return []
        return response.json()

    def get_provider_users(self, firm_id: str) -> list[dict[str, str] | None]:
        response = self.get(f"/provider-firms/{firm_id}/provider-users")
        if response.status_code == 204:
            return {}
        return response.json()

    def get_office_contract_details(self, firm_id: int, office_code: str) -> dict[str, str | None]:
        response = self.get(f"/provider-firms/{firm_id}/provider-offices/{office_code}/office-contract-details")
        if response.status_code == 204:
            return {}
        return response.json()

    def get_office_schedule_details(self, firm_id: int, office_code: str) -> dict[str, str | None]:
        response = self.get(f"/provider-firms/{firm_id}/provider-offices/{office_code}/schedules")
        if response.status_code == 204:
            return {}
        return response.json()

    def get_office_bank_details(self, firm_id: int, office_code: str) -> dict[str, str | None]:
        response = self.get(f"/provider-firms/{firm_id}/provider-offices/{office_code}/bank-account-details")
        if response.status_code == 204:
            return {}
        return response.json()
