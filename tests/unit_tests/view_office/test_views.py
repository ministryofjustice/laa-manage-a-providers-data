from flask import url_for

from app.main.views import get_vat_registration_table
from app.models import Firm, Office


class TestViewOffice:
    def test_get_vat_registration_table(self, app):
        with app.app_context():
            firm = Firm(firmId=1, firmName="Test firm")
            office = Office(
                firmOfficeCode="100AL", addressLine1="102 Petty France", city="London", postCode="SSW1H 9AJ"
            )
            table = get_vat_registration_table(firm, office)
            url = url_for("main.add_office_vat_number", firm=firm, office=office)
            assert url in table.get_rows()[0][-1]["html"]
