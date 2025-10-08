from flask import get_flashed_messages, url_for

from app.main.update_office.forms import BankAccountSearchForm
from app.main.update_office.views import SearchBankAccountFormView
from app.models import Firm, Office


class TestUpdateVATRegistrationNumberFormView:
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
    def test_get_returns_redirect(self, app, client):
        pda = app.extensions["pda"]
        firm = pda.create_provider_firm(
            Firm(
                **{
                    "firmId": 12345,
                    "firmName": "Test firm name",
                }
            )
        )
        office = pda.create_provider_office(Office(**{}), firm_id=firm.firm_id)
        bank_accounts = pda.get_provider_firm_bank_details(firm.firm_id)
        assert len(bank_accounts) == 0

        view = SearchBankAccountFormView(form_class=BankAccountSearchForm)
        response = view.get(firm, office, context={})
        assert response.location == url_for("main.view_office", firm=firm, office=office)
        assert response.status_code == 302
        assert get_flashed_messages() == ["No bank accounts found"]
