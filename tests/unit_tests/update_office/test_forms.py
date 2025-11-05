import pytest

from app.main.forms import NoBankAccountsError
from app.main.update_office.forms import BankAccountSearchForm
from app.models import BankAccount, Firm, Office


@pytest.fixture
def setup_fixture(request, app):
    pda = app.extensions["pda"]
    firm = pda.get_all_provider_firms()[0]
    office = pda.get_provider_offices(firm.firm_id)[0]
    bank_accounts = pda.get_provider_firm_bank_details(firm.firm_id)
    all_bank_accounts = pda.get_all_bank_accounts()

    # Add properties to class being decorated
    request.cls.firm = firm
    request.cls.office = office
    request.cls.bank_accounts = bank_accounts
    request.cls.all_bank_accounts = all_bank_accounts


@pytest.mark.usefixtures("setup_fixture")
class TestSearchBankAccountForm:
    def test_form_no_search(self, app):
        """Should show all bank accounts belonging to the firm if no search term is provided."""

        assert len(self.bank_accounts) == 3
        form = BankAccountSearchForm(firm=self.firm, office=self.office)
        assert len(form.bank_accounts_table.data) == 3

    def test_form_search(self, app):
        """Search for a given sort code."""

        assert len(self.bank_accounts) == 3
        form = BankAccountSearchForm(firm=self.firm, office=self.office, search_term="203045")
        assert len(form.bank_accounts_table.data) == 1
        assert form.bank_accounts_table.data[0]["account_number"] == "12345678"

    def test_form_pagination(self, app):
        """Test pagination"""

        assert len(self.bank_accounts) == 3

        BankAccount.ITEMS_PER_PAGE = 1
        form = BankAccountSearchForm(firm=self.firm, office=self.office)
        assert form.num_results == 3
        assert form.page == 1
        assert len(form.bank_accounts_table.data[1])

    def test_form_empty_result(self, app):
        form = BankAccountSearchForm(firm=self.firm, office=self.office, search_term="DOES NOT EXIST")
        assert form.num_results == 0
        assert len(form.bank_accounts_table.data) == 0

    def test_no_bank_accounts_lsp(self, app):
        firm = Firm(
            firmName="Test Firm Name",
            firmId=1001,
            firmType="Legal Services Provider",
        )
        office = Office(officeName="Test Office Name", firmOfficeId=2001, firmOfficeCode="T2001")
        with pytest.raises(NoBankAccountsError):
            BankAccountSearchForm(firm=firm, office=office)

    def test_no_bank_accounts_advocate(self, app):
        firm = Firm(
            firmName="Test Firm Name",
            firmId=1001,
            firmType="Advocate",
        )
        office = Office(officeName="Test Office Name", firmOfficeId=2001, firmOfficeCode="T2001")
        form = BankAccountSearchForm(firm=firm, office=office)
        assert len(form.bank_accounts_table.data) == len(self.all_bank_accounts)

    def test_no_bank_accounts_barrister(self, app):
        firm = Firm(
            firmName="Test Firm Name",
            firmId=1001,
            firmType="Barrister",
        )
        office = Office(officeName="Test Office Name", firmOfficeId=2001, firmOfficeCode="T2001")
        form = BankAccountSearchForm(firm=firm, office=office)
        assert len(form.bank_accounts_table.data) == len(self.all_bank_accounts)
