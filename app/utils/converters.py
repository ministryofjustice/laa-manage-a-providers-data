from flask import current_app
from werkzeug.exceptions import NotFound
from werkzeug.routing import BaseConverter

from app.models import Firm, Office


class FirmConverter(BaseConverter):
    """
    Custom URL converter that converts a firm_id to a Firm object.

    Usage in routes:
        @bp.route('/firm/<firm:firm>')
        def view_firm(firm):
            # firm is now a Firm object, not an int
            return f"Firm name: {firm.firm_name}"
    """

    def to_python(self, value):
        """Convert URL parameter to a Firm object."""
        try:
            firm_id = int(value)
            if firm_id <= 0:
                raise ValueError("Firm ID must be positive")
        except ValueError:
            raise NotFound("Invalid firm ID")

        pda = current_app.extensions.get("pda")
        if not pda:
            raise RuntimeError("Provider Data API not initialized")

        firm = pda.get_provider_firm(firm_id)
        if not firm:
            raise NotFound(f"Firm with ID {firm_id} not found")

        return firm

    def to_url(self, value):
        """Convert Firm object back to URL parameter."""
        if isinstance(value, Firm):
            return str(value.firm_id)
        elif isinstance(value, int):
            return str(value)
        else:
            raise ValueError("Value must be a Firm object or integer")


class OfficeConverter(BaseConverter):
    """
    Custom URL converter that converts a firm_office_code to an Office object.

    Usage in routes:
        @bp.route('/office/<office:office>')
        def view_office(office):
            # office is now an Office object, not an int
            return f"Office name: {office.office_name}"
    """

    def to_python(self, office_code):
        """Convert URL parameter to an Office object."""

        pda = current_app.extensions.get("pda")
        if not pda:
            raise RuntimeError("Provider Data API not initialized")

        office = pda.get_provider_office(office_code)
        if not office:
            raise NotFound(f"Office with code {office_code} not found")

        return office

    def to_url(self, value):
        """Convert Firm object back to URL parameter."""
        if isinstance(value, Office):
            return str(value.firm_office_code)
        elif isinstance(value, str):
            return value
        else:
            raise ValueError("Value must be a Firm object or a string")
