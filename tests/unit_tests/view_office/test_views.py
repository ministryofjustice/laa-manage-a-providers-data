from flask import url_for

from app.main.table_builders import get_vat_registration_table
from app.models import Firm, Office


class TestViewOffice:
    def _test_get_vat_registration_table(self, app, firm_type, url_contains_office=False):
        with app.app_context():
            firm = Firm(firmId=1, firmName="Test firm", firmType=firm_type)
            office = Office(
                firmOfficeCode="100AL", addressLine1="102 Petty France", city="London", postCode="SSW1H 9AJ"
            )
            table = get_vat_registration_table(firm, office)
            url = url_for("main.add_office_vat_number", firm=firm, office=office if url_contains_office else None)
            assert url in table.get_rows()[0][-1]["html"]

            if url_contains_office:
                assert "office" in table.get_rows()[0][-1]["html"]
            else:
                assert "office" not in table.get_rows()[0][-1]["html"]

    def test_get_vat_registration_table_lsp(self, app):
        self._test_get_vat_registration_table(app, "Legal Services Provider", url_contains_office=True)

    def test_get_vat_registration_table_barrister(self, app):
        self._test_get_vat_registration_table(app, "Barrister", url_contains_office=False)

    def test_get_vat_registration_table_advocate(self, app):
        self._test_get_vat_registration_table(app, "Advocate", url_contains_office=False)
