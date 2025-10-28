from unittest.mock import Mock, patch

import pytest

from app.main.utils import (
    _create_head_office_from_parent,
    _replicate_office_contacts,
    create_advocate_from_form_data,
    create_barrister_from_form_data,
    replicate_office_for_child_firm,
)
from app.models import Contact, Firm, Office


class TestCreateBarristerFromFormData:
    @patch("app.main.utils.add_new_provider")
    @patch("app.main.utils._create_head_office_from_parent")
    def test_creates_barrister_with_correct_data(self, mock_create_office, mock_add_provider):
        mock_firm = Mock(spec=Firm)
        mock_firm.firm_id = 123
        mock_add_provider.return_value = mock_firm

        result = create_barrister_from_form_data(
            barrister_name="John Smith",
            barrister_level="Junior",
            bar_council_roll_number="12345",
            parent_firm_id=456,
        )

        mock_add_provider.assert_called_once()
        firm_arg = mock_add_provider.call_args[0][0]
        assert firm_arg.firm_name == "John Smith"
        assert firm_arg.firm_type == "Barrister"
        assert firm_arg.solicitor_advocate == "No"
        assert firm_arg.advocate_level == "Junior"
        assert firm_arg.bar_council_roll == "12345"
        assert firm_arg.parent_firm_id == 456

        mock_create_office.assert_called_once_with(123, 456)
        assert result == mock_firm


class TestCreateAdvocateFromFormData:
    @patch("app.main.utils.add_new_provider")
    @patch("app.main.utils._create_head_office_from_parent")
    def test_creates_advocate_with_correct_data(self, mock_create_office, mock_add_provider):
        mock_firm = Mock(spec=Firm)
        mock_firm.firm_id = 789
        mock_add_provider.return_value = mock_firm

        result = create_advocate_from_form_data(
            advocate_name="Jane Doe", advocate_level="KC", sra_roll_number="67890", parent_firm_id=101
        )

        mock_add_provider.assert_called_once()
        firm_arg = mock_add_provider.call_args[0][0]
        assert firm_arg.firm_name == "Jane Doe"
        assert firm_arg.firm_type == "Advocate"
        assert firm_arg.solicitor_advocate == "Yes"
        assert firm_arg.advocate_level == "KC"
        assert firm_arg.bar_council_roll == "67890"
        assert firm_arg.parent_firm_id == 101

        mock_create_office.assert_called_once_with(789, 101)
        assert result == mock_firm


class TestReplicateOfficeForChildFirm:
    @patch("app.main.utils.add_new_office")
    def test_replicates_office_as_head_office(self, mock_add_office):
        source_office = Mock(spec=Office)
        source_office.to_internal_dict.return_value = {
            "firm_office_id": 999,
            "ccms_firm_office_id": 888,
            "firm_office_code": "OLD123",
            "address_line_1": "123 Test Street",
            "city": "Test City",
            "postcode": "TE1 2ST",
            "telephone_number": "01234567890",
            "creation_date": "2023-01-01",
        }

        mock_new_office = Mock(spec=Office)
        mock_add_office.return_value = mock_new_office

        new_firm_id = 555

        result = replicate_office_for_child_firm(source_office, new_firm_id, as_head_office=True)

        mock_add_office.assert_called_once()
        office_arg = mock_add_office.call_args[0][0]
        firm_id_arg = mock_add_office.call_args[1]["firm_id"]
        show_message_arg = mock_add_office.call_args[1]["show_success_message"]

        assert firm_id_arg == new_firm_id
        assert show_message_arg is False

        office_dict = office_arg.to_internal_dict()

        assert office_dict["firm_office_id"] == 0
        assert office_dict["ccms_firm_office_id"] == 0
        assert "firm_office_code" not in office_dict
        assert "creation_date" not in office_dict

        assert office_dict["address_line_1"] == "123 Test Street"
        assert office_dict["city"] == "Test City"
        assert office_dict["postcode"] == "TE1 2ST"
        assert office_dict["telephone_number"] == "01234567890"
        assert office_dict["head_office"] == "N/A"
        assert office_dict["payment_method"] == "Electronic"

        assert result == mock_new_office

    @patch("app.main.utils.add_new_office")
    def test_replicates_office_as_branch_office(self, mock_add_office):
        source_office = Mock(spec=Office)
        source_office.to_internal_dict.return_value = {"address_line_1": "456 Branch Street", "city": "Branch City"}

        mock_new_office = Mock(spec=Office)
        mock_add_office.return_value = mock_new_office

        replicate_office_for_child_firm(source_office, 666, as_head_office=False)

        office_arg = mock_add_office.call_args[0][0]
        office_dict = office_arg.to_internal_dict()

        assert office_dict.get("head_office") is None
        assert office_dict["payment_method"] == "Electronic"


class TestCreateHeadOfficeFromParent:
    @patch("app.main.utils.replicate_office_for_child_firm")
    @patch("app.main.utils._replicate_office_contacts")
    def test_creates_head_office_and_replicates_contacts(self, mock_replicate_contacts, mock_replicate_office, app):
        with app.app_context():
            mock_pda = app.extensions["pda"]

            mock_head_office = Mock(spec=Office)
            mock_head_office.get_is_head_office.return_value = True
            mock_head_office.firm_office_code = "HEAD123"

            mock_branch_office = Mock(spec=Office)
            mock_branch_office.get_is_head_office.return_value = False

            mock_pda.get_provider_offices = Mock(return_value=[mock_branch_office, mock_head_office])

            mock_new_office = Mock(spec=Office)
            mock_new_office.firm_office_code = "NEW456"
            mock_replicate_office.return_value = mock_new_office

            result = _create_head_office_from_parent(777, 888)

            mock_pda.get_provider_offices.assert_called_once_with(888)
            mock_replicate_office.assert_called_once_with(mock_head_office, 777, as_head_office=True)
            mock_replicate_contacts.assert_called_once_with(888, "HEAD123", 777, "NEW456")
            assert result == mock_new_office

    def test_raises_error_when_no_head_office_found(self, app):
        with app.app_context():
            mock_pda = app.extensions["pda"]

            mock_branch_office = Mock(spec=Office)
            mock_branch_office.get_is_head_office.return_value = False
            mock_pda.get_provider_offices = Mock(return_value=[mock_branch_office])

            with pytest.raises(RuntimeError, match="No head office found for parent firm 999"):
                _create_head_office_from_parent(123, 999)


class TestReplicateOfficeContacts:
    @patch("app.main.utils.add_new_contact")
    def test_replicates_all_contacts(self, mock_add_contact, app):
        with app.app_context():
            mock_pda = app.extensions["pda"]

            contact1 = Mock(spec=Contact)
            contact1.to_internal_dict.return_value = {
                "vendor_site_id": 111,
                "first_name": "Alice",
                "last_name": "Johnson",
                "email_address": "alice@example.com",
                "primary": "Y",
            }

            contact2 = Mock(spec=Contact)
            contact2.to_internal_dict.return_value = {
                "vendor_site_id": 222,
                "first_name": "Bob",
                "last_name": "Smith",
                "email_address": "bob@example.com",
                "primary": "N",
            }

            mock_pda.get_office_contacts = Mock(return_value=[contact1, contact2])

            mock_new_contact1 = Mock(spec=Contact)
            mock_new_contact2 = Mock(spec=Contact)
            mock_add_contact.side_effect = [mock_new_contact1, mock_new_contact2]

            result = _replicate_office_contacts(888, "SOURCE123", 999, "TARGET456")

            mock_pda.get_office_contacts.assert_called_once_with(888, "SOURCE123")

            assert mock_add_contact.call_count == 2

            first_call = mock_add_contact.call_args_list[0]
            contact_arg1 = first_call[0][0]
            firm_id1 = first_call[1]["firm_id"]
            office_code1 = first_call[1]["office_code"]
            show_msg1 = first_call[1]["show_success_message"]
            assert firm_id1 == 999
            assert office_code1 == "TARGET456"
            assert show_msg1 is False

            contact1_dict = contact_arg1.to_internal_dict()
            assert "vendor_site_id" not in contact1_dict
            assert contact1_dict["first_name"] == "Alice"
            assert contact1_dict["last_name"] == "Johnson"
            assert contact1_dict["primary"] == "Y"

            second_call = mock_add_contact.call_args_list[1]
            contact_arg2 = second_call[0][0]
            contact2_dict = contact_arg2.to_internal_dict()
            assert contact2_dict["first_name"] == "Bob"
            assert contact2_dict["primary"] == "N"

            assert result == [mock_new_contact1, mock_new_contact2]

    def test_returns_empty_list_when_no_contacts(self, app):
        with app.app_context():
            mock_pda = app.extensions["pda"]
            mock_pda.get_office_contacts = Mock(return_value=[])

            result = _replicate_office_contacts(123, "CODE1", 456, "CODE2")

            assert result == []
