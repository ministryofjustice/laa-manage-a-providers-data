from datetime import datetime, timedelta
from unittest.mock import patch

from app.main.table_builders import get_sorted_office_bank_accounts
from app.models import BankAccount, Firm, Office


@patch("app.pda.mock_api.MockProviderDataApi.get_office_bank_accounts")
def test_get_sorted_bank_accounts(mock_get_office_bank_accounts, app):
    firm = Firm(firmId=1, firmName="Test firm")
    office = Office(firmOfficeId=1, officeName="Test office")
    bank_accounts = [
        # Fourth
        BankAccount(bankAccountId=1001, endDate=(datetime.today() - timedelta(days=4)).date(), primaryFlag="N"),
        # First
        BankAccount(bankAccountId=1002, startDate=(datetime.today() - timedelta(days=1)).date(), primaryFlag="Y"),
        # Third
        BankAccount(bankAccountId=1003, endDate=(datetime.today() - timedelta(days=3)).date(), primaryFlag="N"),
        # Second
        BankAccount(bankAccountId=1004, endDate=(datetime.today() - timedelta(days=1)).date(), primaryFlag="N"),
    ]
    mock_get_office_bank_accounts.return_value = bank_accounts

    expected_sorted_bank_ids = [1002, 1004, 1003, 1001]
    result_bank_account_ids = [
        bank_account.bank_account_id for bank_account in get_sorted_office_bank_accounts(firm, office)
    ]
    assert result_bank_account_ids == expected_sorted_bank_ids
