import datetime

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

        assert len(self.bank_accounts) == 4
        form = BankAccountSearchForm(firm=self.firm, office=self.office)
        assert len(form.bank_accounts_table.data) == 4

    def test_form_search(self, app):
        """Search for a given sort code."""

        assert len(self.bank_accounts) == 4
        form = BankAccountSearchForm(firm=self.firm, office=self.office, search_term="203045")
        assert len(form.bank_accounts_table.data) == 1
        assert form.bank_accounts_table.data[0]["account_number"] == "12345678"

    def test_form_pagination(self, app):
        """Test pagination"""

        assert len(self.bank_accounts) == 4

        BankAccount.ITEMS_PER_PAGE = 1
        form = BankAccountSearchForm(firm=self.firm, office=self.office)
        assert form.num_results == 4
        assert form.page == 1
        assert len(form.bank_accounts_table.data[1])

    def test_form_empty_result(self, app):
        form = BankAccountSearchForm(firm=self.firm, office=self.office, search_term="DOES NOT EXIST")
        assert form.num_results == 0
        assert len(form.bank_accounts_table.data) == 0

    def test_form_bank_accounts_order(self, app):
        """Bank accounts with the latest start date should be at the top"""
        bank_accounts = [
            # Last
            BankAccount(
                bankAccountId=1001, bankAccountName="Test Bank Account 1", accountNumber="10000001", sortCode="203010"
            ),
            # First
            BankAccount(
                bankAccountId=1002,
                bankAccountName="Test Bank Account 2",
                accountNumber="10000002",
                sortCode="203010",
                startDate=datetime.date(2026, 1, 1),
            ),
            # Second
            BankAccount(
                bankAccountId=1003,
                bankAccountName="Test Bank Account 3",
                accountNumber="10000003",
                sortCode="203010",
                startDate=datetime.date(2025, 10, 1),
            ),
            # Third
            BankAccount(
                bankAccountId=1004,
                bankAccountName="Test Bank Account 4",
                accountNumber="10000004",
                sortCode="203010",
                startDate=datetime.date(2024, 10, 1),
            ),
        ]
        expected_sorted_bank_accounts = [
            bank_accounts[1],
            bank_accounts[2],
            bank_accounts[3],
            bank_accounts[0],
        ]
        assert expected_sorted_bank_accounts == BankAccountSearchForm.sort_bank_accounts(bank_accounts)

    def test_no_bank_accounts_lsp(self, app):
        firm = Firm(
            firmName="Test Firm Name",
            firmId=1001,
            firmType="Legal Services Provider",
        )
        office = Office(officeName="Test Office Name", firmOfficeId=2001, firmOfficeCode="T2001")
        with pytest.raises(NoBankAccountsError):
            BankAccountSearchForm(firm=firm, office=office)

    def test_no_bank_accounts_no_default_search(self, app):
        form = BankAccountSearchForm(firm=self.firm, office=self.office, search_term=None)
        assert not hasattr(form, "bank_accounts_table")

    def test_no_bank_accounts_advocate(self, app):
        firm = Firm(
            firmName="Test Firm Name",
            firmId=1001,
            firmType="Advocate",
        )
        office = Office(officeName="Test Office Name", firmOfficeId=2001, firmOfficeCode="T2001")
        form = BankAccountSearchForm(firm=firm, office=office, search_term="")
        assert len(form.bank_accounts_table.data) == len(self.all_bank_accounts)

    def test_no_bank_accounts_barrister(self, app):
        firm = Firm(
            firmName="Test Firm Name",
            firmId=1001,
            firmType="Barrister",
        )
        office = Office(officeName="Test Office Name", firmOfficeId=2001, firmOfficeCode="T2001")
        form = BankAccountSearchForm(firm=firm, office=office, search_term="")
        assert len(form.bank_accounts_table.data) == len(self.all_bank_accounts)
