from unittest.mock import Mock

import pytest
from werkzeug.exceptions import NotFound
from werkzeug.routing import Map

from app.models import Firm
from app.utils.converters import FirmConverter


class TestFirmConverter:
    def setup_method(self):
        self.url_map = Map()
        self.converter = FirmConverter(self.url_map)

    def test_to_python_valid_positive_id(self, app):
        """Test converting valid positive ID to Firm object."""
        with app.app_context():
            # The MockProviderDataApi is already set up in the test app
            result = self.converter.to_python("1")

            assert isinstance(result, Firm)
            assert result.firm_id == 1
            assert result.firm_name == "Smith & Partners Solicitors"

    def test_to_python_invalid_non_numeric_id(self):
        """Test that non-numeric ID raises NotFound."""
        with pytest.raises(NotFound, match="Invalid firm ID"):
            self.converter.to_python("abc")

    def test_to_python_invalid_negative_id(self):
        """Test that negative ID raises NotFound."""
        with pytest.raises(NotFound, match="Invalid firm ID"):
            self.converter.to_python("-1")

    def test_to_python_invalid_zero_id(self):
        """Test that zero ID raises NotFound."""
        with pytest.raises(NotFound, match="Invalid firm ID"):
            self.converter.to_python("0")

    def test_to_python_firm_not_found(self, app):
        """Test that non-existent firm raises NotFound."""
        with app.app_context():
            with pytest.raises(NotFound, match="Firm with ID 999999 not found"):
                self.converter.to_python("999999")

    def test_to_url_with_firm_object(self):
        """Test converting Firm object to URL parameter."""
        mock_firm = Mock(spec=Firm)
        mock_firm.firm_id = 123

        result = self.converter.to_url(mock_firm)

        assert result == "123"

    def test_to_url_with_integer(self):
        """Test converting integer to URL parameter."""
        result = self.converter.to_url(456)

        assert result == "456"

    def test_to_url_with_invalid_type(self):
        """Test that invalid type raises ValueError."""
        with pytest.raises(ValueError, match="Value must be a Firm object or integer"):
            self.converter.to_url("invalid")

    def test_to_url_with_string_number(self):
        """Test that string number raises ValueError."""
        with pytest.raises(ValueError, match="Value must be a Firm object or integer"):
            self.converter.to_url("123")

    def test_to_url_with_none(self):
        """Test that None raises ValueError."""
        with pytest.raises(ValueError, match="Value must be a Firm object or integer"):
            self.converter.to_url(None)

    def test_to_python_float_string_raises_error(self):
        """Test that float string raises NotFound."""
        with pytest.raises(NotFound, match="Invalid firm ID"):
            self.converter.to_python("123.45")

    def test_to_url_with_zero_firm_id(self):
        """Test Firm object with zero ID."""
        mock_firm = Mock(spec=Firm)
        mock_firm.firm_id = 0

        result = self.converter.to_url(mock_firm)

        assert result == "0"
