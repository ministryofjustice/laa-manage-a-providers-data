from datetime import date
from unittest.mock import MagicMock, Mock, patch

import pytest
from flask import Blueprint
from flask_wtf import FlaskForm
from wtforms import StringField

from app.main.utils import change_liaison_manager, reassign_head_office
from app.models import Contact
from app.pda.mock_api import MockPDAError, MockProviderDataApi
from app.utils import register_form_view
from app.views import BaseFormView


class MockForm(FlaskForm):
    url = "test-form"
    name = StringField("Name")


class MockCustomView(BaseFormView):
    pass


class TestRegisterFormView:
    def test_register_with_default_blueprint_and_view(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.utils.utils.BaseFormView", mock_view_class), patch("app.main.bp", mock_blueprint):
            register_form_view(MockForm, login_required=False)

        mock_blueprint.add_url_rule.assert_called_once_with(
            "/test-form", view_func="mock_view_func", methods=["GET", "POST"]
        )
        mock_view_class.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_register_with_custom_blueprint(self):
        custom_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.utils.utils.BaseFormView", mock_view_class):
            register_form_view(MockForm, blueprint=custom_blueprint, login_required=False)

            custom_blueprint.add_url_rule.assert_called_once_with(
                "/test-form", view_func="mock_view_func", methods=["GET", "POST"]
            )
            mock_view_class.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_register_with_custom_view_class(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_custom_view = Mock()
        mock_custom_view.as_view.return_value = "custom_view_func"

        with patch("app.main.bp", mock_blueprint):
            register_form_view(MockForm, view_class=mock_custom_view, login_required=False)

            mock_blueprint.add_url_rule.assert_called_once_with(
                "/test-form", view_func="custom_view_func", methods=["GET", "POST"]
            )
            mock_custom_view.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_register_with_all_custom_parameters(self):
        custom_blueprint = Mock(spec=Blueprint)
        mock_custom_view = Mock()
        mock_custom_view.as_view.return_value = "custom_view_func"

        register_form_view(MockForm, view_class=mock_custom_view, blueprint=custom_blueprint, login_required=False)

        custom_blueprint.add_url_rule.assert_called_once_with(
            "/test-form", view_func="custom_view_func", methods=["GET", "POST"]
        )
        mock_custom_view.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_url_generation_from_form_class(self):
        class CustomUrlForm(FlaskForm):
            url = "custom-url-path"

        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.utils.BaseFormView", mock_view_class):
            register_form_view(CustomUrlForm, login_required=False)

            mock_blueprint.add_url_rule.assert_called_once_with(
                "/custom-url-path", view_func="mock_view_func", methods=["GET", "POST"]
            )

    def test_view_name_generation_from_form_class(self):
        class VeryLongFormClassName(FlaskForm):
            url = "test"

        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.utils.BaseFormView", mock_view_class):
            register_form_view(VeryLongFormClassName, login_required=False)

            mock_view_class.as_view.assert_called_once_with("test", form_class=VeryLongFormClassName)

    def test_methods_are_always_get_and_post(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.utils.BaseFormView", mock_view_class):
            register_form_view(MockForm, login_required=False)

            call_args = mock_blueprint.add_url_rule.call_args
            assert call_args[1]["methods"] == ["GET", "POST"]

    def test_form_class_passed_to_as_view(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.utils.BaseFormView", mock_view_class):
            register_form_view(MockForm, login_required=False)

            call_args = mock_view_class.as_view.call_args
            assert call_args[1]["form_class"] == MockForm

    def test_function_returns_none(self):
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.main.bp", mock_blueprint), patch("app.utils.utils.BaseFormView", mock_view_class):
            result = register_form_view(MockForm, login_required=False)

            assert result is None


class TestRegisterFormViewIntegration:
    def test_register_with_real_blueprint(self):
        real_blueprint = Blueprint("test", __name__)
        mock_view_class = Mock()
        mock_view_func = Mock()
        mock_view_class.as_view.return_value = mock_view_func

        register_form_view(MockForm, view_class=mock_view_class, blueprint=real_blueprint, login_required=False)

        # Verify the view class was called correctly
        mock_view_class.as_view.assert_called_once_with("test_form", form_class=MockForm)

    def test_register_multiple_forms_same_blueprint(self):
        class Form1(FlaskForm):
            url = "form1"

        class Form2(FlaskForm):
            url = "form2"

        real_blueprint = Blueprint("test", __name__)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = Mock()

        register_form_view(Form1, view_class=mock_view_class, blueprint=real_blueprint, login_required=False)
        register_form_view(Form2, view_class=mock_view_class, blueprint=real_blueprint, login_required=False)

        # Both forms should be registered
        assert mock_view_class.as_view.call_count == 2

        # Check the calls were made with correct form classes
        calls = mock_view_class.as_view.call_args_list
        assert calls[0][1]["form_class"] == Form1
        assert calls[1][1]["form_class"] == Form2

    def test_register_form_with_special_characters_in_name(self):
        class FormWithNumbers123(FlaskForm):
            url = "special-form"

        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        with patch("app.utils.utils.BaseFormView", mock_view_class):
            register_form_view(FormWithNumbers123, blueprint=mock_blueprint, login_required=False)

            mock_view_class.as_view.assert_called_once_with("special_form", form_class=FormWithNumbers123)

    def test_parameter_types_are_correct(self):
        # Test that the function accepts the expected parameter types
        mock_blueprint = Mock(spec=Blueprint)
        mock_view_class = Mock()
        mock_view_class.as_view.return_value = "mock_view_func"

        # This should not raise any type errors if the function signature is correct
        register_form_view(
            form_class=MockForm, view_class=mock_view_class, blueprint=mock_blueprint, login_required=False
        )

        # Verify it was called
        mock_blueprint.add_url_rule.assert_called_once()
        mock_view_class.as_view.assert_called_once()


class TestChangeLiaisonManager:
    @pytest.fixture(autouse=True)
    def setup_mock_api(self, app):
        """Ensure each test starts with a clean MockProviderDataApi."""
        with app.app_context():
            mock_pda = MockProviderDataApi()
            mock_pda.init_app(app)
            app.extensions["pda"] = mock_pda

    def test_successful_change_with_mock_api(self, app):
        """Test successful liaison manager change with MockPDA."""
        mock_contact = Contact(
            first_name="Jane", last_name="Doe", email_address="jane.doe@example.com", telephone_number="01234567890"
        )

        with app.test_request_context():
            result = change_liaison_manager(mock_contact, 1)

            assert result.first_name == "Jane"
            assert result.last_name == "Doe"
            assert result.email_address == "jane.doe@example.com"
            assert result.job_title == "Liaison manager"
            assert result.primary == "Y"

    def test_invalid_firm_id_raises_value_error(self, app):
        """Test that ValueError is raised for invalid firm_id."""
        mock_contact = Contact(
            first_name="Jane", last_name="Doe", email_address="jane.doe@example.com", telephone_number="01234567890"
        )

        with app.test_request_context():
            with pytest.raises(ValueError, match="firm_id must be a positive integer"):
                change_liaison_manager(mock_contact, 0)

            with pytest.raises(ValueError, match="firm_id must be a positive integer"):
                change_liaison_manager(mock_contact, -1)

    def test_success_with_existing_liaison_managers(self, app):
        """Test setting a new primary liaison manager when existing ones exist."""
        with app.test_request_context():
            mock_api = app.extensions["pda"]
            mock_api._mock_data = {
                "firms": [{"firmId": 1, "firmName": "Test Firm"}],
                "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101, "headOffice": "N/A"}],
                "contacts": [
                    {
                        "vendorSiteId": 101,
                        "firstName": "John",
                        "lastName": "Smith",
                        "emailAddress": "john.smith@example.com",
                        "jobTitle": "Liaison manager",
                        "primary": "Y",
                        "activeFrom": "2024-01-01",
                    }
                ],
            }

            new_contact = Contact(
                first_name="Alice",
                last_name="Johnson",
                email_address="alice.johnson@example.com",
                telephone_number="01234567890",
            )

            result = change_liaison_manager(new_contact, 1)

            assert result.vendor_site_id == 101
            assert result.first_name == "Alice"
            assert result.last_name == "Johnson"
            assert result.email_address == "alice.johnson@example.com"
            assert result.primary == "Y"
            assert result.job_title == "Liaison manager"

    def test_creates_contacts_for_all_offices(self, app):
        """Test that contacts are created for all offices of the firm."""
        with app.test_request_context():
            mock_api = app.extensions["pda"]
            mock_api._mock_data = {
                "firms": [{"firmId": 1, "firmName": "Test Firm"}],
                "offices": [
                    {"_firmId": 1, "firmOfficeCode": "HEAD01", "firmOfficeId": 101, "headOffice": "N/A"},
                    {"_firmId": 1, "firmOfficeCode": "BRANCH01", "firmOfficeId": 102, "headOffice": "101"},
                    {"_firmId": 1, "firmOfficeCode": "BRANCH02", "firmOfficeId": 103, "headOffice": "101"},
                ],
                "contacts": [],
            }

            new_contact = Contact(
                first_name="Multi",
                last_name="Office",
                email_address="multi.office@example.com",
            )

            result = change_liaison_manager(new_contact, 1)

            assert result.vendor_site_id == 101
            assert result.primary == "Y"

            contacts = mock_api._mock_data["contacts"]
            liaison_contacts = [c for c in contacts if c.get("jobTitle") == "Liaison manager"]
            assert len(liaison_contacts) == 3

            for contact in liaison_contacts:
                assert contact["firstName"] == "Multi"
                assert contact["lastName"] == "Office"
                assert contact["emailAddress"] == "multi.office@example.com"
                assert contact["primary"] == "Y"

            office_ids = [c["vendorSiteId"] for c in liaison_contacts]
            assert 101 in office_ids
            assert 102 in office_ids
            assert 103 in office_ids

    def test_sets_active_from_date(self, app):
        """Test that active_from is set to today's date when not provided."""
        with app.test_request_context():
            mock_api = app.extensions["pda"]
            mock_api._mock_data = {
                "firms": [{"firmId": 1, "firmName": "Test Firm"}],
                "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101, "headOffice": "N/A"}],
                "contacts": [],
            }

            new_contact = Contact(
                first_name="Test",
                last_name="User",
                email_address="test@example.com",
            )

            result = change_liaison_manager(new_contact, 1)

            assert result.active_from is not None
            expected_date = date.today().isoformat()
            assert result.active_from == expected_date

    @patch("app.main.utils.logger")
    def test_update_contact_error_handling(self, mock_logger, app):
        """Test error handling when updating existing liaison manager fails."""
        with app.test_request_context():
            mock_api = app.extensions["pda"]
            mock_api._mock_data = {
                "firms": [{"firmId": 1, "firmName": "Test Firm"}],
                "offices": [{"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101, "headOffice": "N/A"}],
                "contacts": [
                    {
                        "vendorSiteId": 101,
                        "firstName": "John",
                        "lastName": "Smith",
                        "emailAddress": "john.smith@example.com",
                        "jobTitle": "Liaison manager",
                        "primary": "Y",
                        "activeFrom": "2024-01-01",
                    }
                ],
            }

            # Mock the update_contact method to raise an error
            mock_api.update_contact = MagicMock(side_effect=MockPDAError("Update failed"))

            new_contact = Contact(
                first_name="Jane",
                last_name="Doe",
                email_address="jane.doe@example.com",
            )

            with patch("app.main.utils.flash") as mock_flash:
                result = change_liaison_manager(new_contact, 1)

                # Should still create new contact despite update failure
                assert result.first_name == "Jane"
                assert result.last_name == "Doe"

                # Should log error and flash error message
                mock_logger.error.assert_called_once_with("Failed to update Liaison manager for office 1A001L")
                mock_flash.assert_any_call("Failed to update Liaison manager for office 1A001L", "error")

    @patch("app.main.utils.logger")
    def test_create_contact_error_handling(self, mock_logger, app):
        """Test error handling when creating new liaison manager fails."""
        with app.test_request_context():
            mock_api = app.extensions["pda"]
            mock_api._mock_data = {
                "firms": [{"firmId": 1, "firmName": "Test Firm"}],
                "offices": [
                    {"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101, "headOffice": "N/A"},
                    {"_firmId": 1, "firmOfficeCode": "1A002L", "firmOfficeId": 102, "headOffice": "101"},
                ],
                "contacts": [],
            }

            # Mock create_office_contact to fail for one office
            original_create = mock_api.create_office_contact

            def side_effect(firm_id, office_code, contact):
                if office_code == "1A002L":
                    raise MockPDAError("Create failed")
                return original_create(firm_id, office_code, contact)

            mock_api.create_office_contact = MagicMock(side_effect=side_effect)

            new_contact = Contact(
                first_name="Jane",
                last_name="Doe",
                email_address="jane.doe@example.com",
            )

            with patch("app.main.utils.flash") as mock_flash:
                result = change_liaison_manager(new_contact, 1)

                # Should still return contact for head office
                assert result.vendor_site_id == 101
                assert result.first_name == "Jane"

                # Should log error and flash error message for failed office
                mock_logger.error.assert_called_once_with("Failed to create Liaison manager for office 1A002L")
                mock_flash.assert_any_call("Failed to create Liaison manager for office 1A002L", "error")

    @patch("app.main.utils.logger")
    def test_partial_failure_with_mixed_errors(self, mock_logger, app):
        """Test handling when both update and create operations have failures."""
        with app.test_request_context():
            mock_api = app.extensions["pda"]
            mock_api._mock_data = {
                "firms": [{"firmId": 1, "firmName": "Test Firm"}],
                "offices": [
                    {"_firmId": 1, "firmOfficeCode": "1A001L", "firmOfficeId": 101, "headOffice": "N/A"},
                    {"_firmId": 1, "firmOfficeCode": "1A002L", "firmOfficeId": 102, "headOffice": "101"},
                ],
                "contacts": [
                    {
                        "vendorSiteId": 101,
                        "firstName": "Old",
                        "lastName": "Manager",
                        "emailAddress": "old.manager@example.com",
                        "jobTitle": "Liaison manager",
                        "primary": "Y",
                        "activeFrom": "2024-01-01",
                    }
                ],
            }

            # Mock both operations to fail
            mock_api.update_contact = MagicMock(side_effect=MockPDAError("Update failed"))

            original_create = mock_api.create_office_contact

            def create_side_effect(firm_id, office_code, contact):
                if office_code == "1A002L":
                    raise MockPDAError("Create failed")
                return original_create(firm_id, office_code, contact)

            mock_api.create_office_contact = MagicMock(side_effect=create_side_effect)

            new_contact = Contact(
                first_name="Jane",
                last_name="Doe",
                email_address="jane.doe@example.com",
            )

            with patch("app.main.utils.flash") as mock_flash:
                result = change_liaison_manager(new_contact, 1)

                # Should still return contact for head office (successful create)
                assert result.vendor_site_id == 101
                assert result.first_name == "Jane"

                # Should log both errors
                assert mock_logger.error.call_count == 2
                mock_logger.error.assert_any_call("Failed to update Liaison manager for office 1A001L")
                mock_logger.error.assert_any_call("Failed to create Liaison manager for office 1A002L")

                # Should flash both error messages
                mock_flash.assert_any_call("Failed to update Liaison manager for office 1A001L", "error")
                mock_flash.assert_any_call("Failed to create Liaison manager for office 1A002L", "error")


class TestReassignHeadOffice:
    @pytest.fixture(autouse=True)
    def setup_mock_api(self, app):
        """Ensure each test starts with a clean MockProviderDataApi."""
        with app.app_context():
            mock_pda = MockProviderDataApi()
            mock_pda.init_app(app)
            app.extensions["pda"] = mock_pda
            mock_pda._mock_data = {
                "firms": [{"firmId": 1, "firmName": "Test Firm"}],
                "offices": [
                    {"_firmId": 1, "firmOfficeCode": "HEAD01", "firmOfficeId": 101, "headOffice": "N/A"},
                    {"_firmId": 1, "firmOfficeCode": "BRANCH01", "firmOfficeId": 102, "headOffice": "HEAD01"},
                    {"_firmId": 1, "firmOfficeCode": "BRANCH02", "firmOfficeId": 103, "headOffice": "HEAD01"},
                ],
                "contacts": [],
            }

    def test_successful_change_with_mock_api(self, app):
        with app.test_request_context():
            new_head = reassign_head_office(firm=1, new_head_office="BRANCH01")

            assert new_head.head_office == "N/A"
            assert new_head.firm_office_code == "BRANCH01"

            mock_api = app.extensions["pda"]
            old_head_office = mock_api.get_provider_office("HEAD01")
            assert old_head_office.head_office == "BRANCH01"
