from unittest.mock import patch

from flask import session, url_for

from app.main.add_a_new_provider.forms import AddBarristerCheckForm, AddBarristerLiaisonManagerForm
from app.main.add_a_new_provider.views import (
    AddAdvocateBarristersCheckFormView,
    AddAdvocateBarristersLiaisonManagerFormView,
    BaseFormView,
    Contact,
)
from app.models import Firm


class TestAddAdvocateBarristerCheckForm:
    def test_dispatch_request_no_barrister_details(self, app):
        """Should redirect to barrister add form if no barrister details are provided."""
        firm = Firm(firmName="Test firm", firmId=1)
        view = AddAdvocateBarristersCheckFormView(model_type="barrister", form_class=AddBarristerCheckForm(firm))
        with app.test_request_context("/"):
            response = view.dispatch_request(firm=firm)
            assert response.location == url_for("main.add_barrister_details_form", firm=1)

    def test_dispatch_request_barrister_details(self, app):
        """Should show the check form when barrister details are provided."""
        firm = Firm(firmName="Test firm", firmId=1)
        view = AddAdvocateBarristersCheckFormView(model_type="barrister", form_class=AddBarristerCheckForm(firm))
        session["new_barrister"] = {"barrister_name": "New Barrister"}
        with patch.object(BaseFormView, "dispatch_request") as mock_parent_dispatch_request:
            view.dispatch_request(firm=firm)
            del session["new_barrister"]
            assert mock_parent_dispatch_request.called

    @patch("app.main.add_a_new_provider.views.create_barrister_from_form_data")
    def test_create_model_barrister(self, mock_create_barrister_from_form_data, app):
        """Test the create_model method can create a barrister from the session"""
        firm = Firm(firmName="Test firm", firmId=1)
        view = AddAdvocateBarristersCheckFormView(model_type="barrister", form_class=AddBarristerCheckForm(firm))
        data = dict(
            barrister_name="Test Barrister",
            barrister_level="Junior",
            bar_council_roll_number="11111",
            parent_firm_id=firm.firm_id,
        )
        session["new_barrister"] = data
        view.create_model()
        assert mock_create_barrister_from_form_data.called
        mock_create_barrister_from_form_data.assert_called_once_with(**data)

    @patch("app.main.add_a_new_provider.views.create_advocate_from_form_data")
    def test_create_model_advocate(self, mock_create_advocate_from_form_data, app):
        """Test the create_model method can create a advocate from the session"""
        firm = Firm(firmName="Test firm", firmId=1)
        view = AddAdvocateBarristersCheckFormView(model_type="advocate", form_class=AddBarristerCheckForm)
        data = dict(
            advocate_name="Test Advocate",
            advocate_level="Junior",
            sra_roll_number="1111 2222",
            parent_firm_id=firm.firm_id,
        )
        session["new_advocate"] = data
        view.create_model()
        assert mock_create_advocate_from_form_data.called
        mock_create_advocate_from_form_data.assert_called_once_with(**data)


class TestAddAdvocateBarristersLiaisonManagerFormView:
    @patch("app.main.add_a_new_provider.views.change_liaison_manager")
    def test_form_valid(self, mock_change_liaison_manager, app):
        """Test creating a new liaison manager for new barrister form."""
        firm = Firm(firmName="Test firm", firmId=1)
        form = AddBarristerLiaisonManagerForm(
            firm=firm,
            first_name="Unit",
            last_name="Tester",
            email_address="unit.tester@justice.gov.uk",
            telephone_number="0208 111 2222",
            website="https://gov.uk",
            job_title="Tester",
        )
        expected_contact = Contact(
            firstName=form.data.get("first_name"),
            lastName=form.data.get("last_name"),
            emailAddress=form.data.get("email_address"),
            telephoneNumber=form.data.get("telephone_number"),
            website=form.data.get("website"),
            jobTitle="Liaison manager",
            primary="Y",
        )
        view = AddAdvocateBarristersLiaisonManagerFormView(
            model_type="barrister", form_class=AddBarristerLiaisonManagerForm
        )
        with patch.object(view, "create_model") as mock_create_model:
            mock_create_model.return_value = Firm(firmId=999)
            view.form_valid(form, firm)
            mock_change_liaison_manager.assert_called_once_with(contact=expected_contact, firm_id=999)
