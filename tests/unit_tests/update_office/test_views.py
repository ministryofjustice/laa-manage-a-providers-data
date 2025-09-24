from flask import url_for


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
