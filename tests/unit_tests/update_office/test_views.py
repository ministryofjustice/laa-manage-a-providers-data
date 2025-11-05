from unittest import mock

import pytest
from flask import url_for
from werkzeug.exceptions import NotFound

from app.main.update_office.forms import BankAccountSearchForm, UpdateVATRegistrationNumberForm
from app.main.update_office.views import SearchBankAccountFormView, UpdateVATRegistrationNumberFormView
from app.models import Firm, Office


class TestUpdateVATRegistrationNumberFormView:
    def test_get_form_instance(self, app):
        with app.app_context():
            view = UpdateVATRegistrationNumberFormView(form_class=UpdateVATRegistrationNumberForm)
            firm = Firm(firmName="Test Firm Name", firmType="Legal Services Provider", firmId=1001)
            office = Office(officeName="Test Office Name", firmOfficeId=2001, firmOfficeCode="A0001")
            form = view.get_form_instance(firm=firm, office=office)
            assert form.firm == firm
            assert form.office == office

    def test_get_form_instance_use_head_office(self, app):
        with app.app_context():
            view = UpdateVATRegistrationNumberFormView(form_class=UpdateVATRegistrationNumberForm)
            firm = Firm(firmName="Test Firm Name", firmType="Advocate", firmId=1001)
            with mock.patch.object(view, "get_api") as mock_get_api:
                head_office = Office(officeName="Test Office Name", firmOfficeId=2001, firmOfficeCode="A0001")
                mock_get_api.return_value.get_head_office.return_value = head_office
                form = view.get_form_instance(firm=firm)
                assert form.firm == firm
                assert form.office == head_office

    def test_get_form_instance_called_without_expected_office(self, app):
        """Expecting a office argument but not passed"""
        with app.app_context():
            view = UpdateVATRegistrationNumberFormView(form_class=UpdateVATRegistrationNumberForm)
            firm = Firm(firmName="Test Firm Name", firmType="Legal Services Provider", firmId=1001)
            with pytest.raises(NotFound):
                view.get_form_instance(firm=firm)

    def test_post(self, app, client):
        """Test changing the VAT registration number of an office"""
        with app.app_context():
            test_vat_registration_number = "GB123459999"
            pda = app.extensions["pda"]
            firm = pda.get_all_provider_firms()[0]
            office = pda.get_provider_offices(firm.firm_id)[0]
            assert office.vat_registration_number != test_vat_registration_number

            url = url_for("main.add_office_vat_number", firm=firm, office=office)
            payload = dict(vat_registration_number=test_vat_registration_number)
            response = client.post(url, data=payload)
            expected_redirect_url = url_for("main.view_office_bank_payment_details", firm=firm, office=office)
            assert response.status_code == 302
            assert response.headers["Location"] == expected_redirect_url

            office = pda.get_provider_offices(firm.firm_id)[0]
            assert office.vat_registration_number == test_vat_registration_number


class TestSearchBankAccountsFormView:
    def test_get_returns_redirect_lsp(self, app, client):
        pda = app.extensions["pda"]
        firm = pda.create_provider_firm(
            Firm(
                **{
                    "firmId": 12345,
                    "firmName": "Test firm name",
                    "firmType": "Legal Services Provider",
                }
            )
        )
        office = pda.create_provider_office(Office(**{}), firm_id=firm.firm_id)
        bank_accounts = pda.get_provider_firm_bank_details(firm.firm_id)
        assert len(bank_accounts) == 0

        view = SearchBankAccountFormView(form_class=BankAccountSearchForm)
        response = view.get(firm, office, context={})
        assert response.location == url_for("main.add_office_bank_account", firm=firm, office=office)
        assert response.status_code == 302

    def test_get_returns_redirect_advocate(self, app, client):
        pda = app.extensions["pda"]
        firm = pda.create_provider_firm(
            Firm(
                **{
                    "firmId": 12345,
                    "firmName": "Test firm name",
                    "firmType": "Advocate",
                }
            )
        )
        office = pda.create_provider_office(Office(**{}), firm_id=firm.firm_id)
        view = SearchBankAccountFormView(form_class=BankAccountSearchForm)
        response = view.get(firm, office, context={})
        assert isinstance(response, str)
