from flask import url_for


class TestUpdateVATRegistrationNumberFormView:
    def test_post(self, app, client):
        with app.app_context():
            pda = app.extensions["pda"]
            firm = pda.get_all_provider_firms()[0]
            office = pda.get_provider_offices(firm.firm_id)[1]

        assert office.vat_registration_number is None
        url = url_for("main.add_office_vat_number", firm=firm, office=office)
        data = dict(vat_registration_number="GB123456789")
        response = client.post(url, data=data)

        office = pda.get_provider_offices(firm.firm_id)[1]
        assert office.vat_registration_number == "GB123456789"

        assert response.status_code == 302
        expected_redirect_url = url_for("main.view_office_bank_payment_details", firm=firm, office=office)
        assert response.location == expected_redirect_url
