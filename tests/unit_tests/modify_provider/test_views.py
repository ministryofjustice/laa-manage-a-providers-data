from unittest.mock import patch

from flask import url_for

from app.constants import (
    DEFAULT_CONTRACT_MANAGER_NAME,
    STATUS_CONTRACT_MANAGER_DEBT_RECOVERY,
    STATUS_CONTRACT_MANAGER_FALSE_BALANCE,
    STATUS_CONTRACT_MANAGER_INACTIVE,
)
from app.main.modify_provider.forms import ChangeProviderActiveStatusForm
from app.main.modify_provider.views import ChangeProviderActiveStatusFormView
from tests.unit_tests.utils import get_firm_by_name, get_firm_office_by_office_code


class TestChangeProviderActiveStatusFormView:
    @patch("app.views.render_template")
    def test_get_inactive_firm(self, mock_render_template, app):
        """Test default form for an inactive provider firm."""
        pda = app.extensions["pda"]
        firm = pda.get_all_provider_firms()[0]
        assert firm.inactive_date is not None

        view = ChangeProviderActiveStatusFormView(form_class=ChangeProviderActiveStatusForm)
        view.get(firm, context={})
        call_kwargs = mock_render_template.call_args.kwargs
        assert call_kwargs["form"].status.data == "inactive"

    @patch("app.views.render_template")
    def test_get_active_firm(self, mock_render_template, app):
        """Test default form for an active provider firm."""
        pda = app.extensions["pda"]
        firm = pda.get_all_provider_firms()[1]
        assert firm.inactive_date is None

        view = ChangeProviderActiveStatusFormView(form_class=ChangeProviderActiveStatusForm)
        view.get(firm, context={})
        call_kwargs = mock_render_template.call_args.kwargs
        assert call_kwargs["form"].status.data == "active"

    def test_post_change_inactive_to_active(self, app, client):
        """Test changing provider from inactive to active"""
        pda = app.extensions["pda"]
        firm = pda.get_all_provider_firms()[0]
        assert firm.inactive_date is not None

        url = url_for("main.change_provider_active_status", firm=firm)
        expected_redirect_url = url_for("main.view_provider", firm=firm)
        payload = {"status": "active"}

        response = client.post(url, data=payload)
        assert response.status_code == 302
        assert response.headers["Location"] == expected_redirect_url

        assert pda.get_provider_firm(firm.firm_id).inactive_date is None

    def test_post_change_active_to_inactive(self, app, client):
        """Test changing provider from active to inactive"""
        pda = app.extensions["pda"]
        firm = pda.get_all_provider_firms()[1]
        assert firm.inactive_date is None

        url = url_for("main.change_provider_active_status", firm=firm)
        expected_redirect_url = url_for("main.view_provider", firm=firm)
        payload = {"status": "inactive"}

        response = client.post(url, data=payload)
        assert response.status_code == 302
        assert response.headers["Location"] == expected_redirect_url

        assert pda.get_provider_firm(firm.firm_id).inactive_date is not None


class TestChangeOfficeFalseBalanceFormView:
    def test_false_balance_set_to_yes(self, app, client):
        """Test that setting False balance to yes changes the contract manager to Mr False Balance"""
        firm = get_firm_by_name(app, "Smith & Partners Solicitors")
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_INACTIVE

        url = url_for("main.change_office_false_balance", firm=firm, office=office)
        payload = {"status": "Yes"}
        client.post(url, data=payload)

        # reload the office
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_FALSE_BALANCE

    def test_false_balance_set_to_no(self, app, client):
        """Test that changing False balance from yes to no, should set the contract manager to Mr Inactive"""

        firm = get_firm_by_name(app, "Smith & Partners Solicitors")
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_INACTIVE

        url = url_for("main.change_office_false_balance", firm=firm, office=office)
        payload = {"status": "Yes"}
        client.post(url, data=payload)

        # reload the office
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_FALSE_BALANCE

        # Change False balance to No
        payload = {"status": "No"}
        client.post(url, data=payload)
        # reload the office
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_INACTIVE


class TestChangeOfficeDebtRecoveryFormView:
    def test_debt_recovery_set_to_yes(self, app, client):
        """Test that setting Debt recovery to yes changes the contract manager to Mr Debt Recovery"""
        firm = get_firm_by_name(app, "Smith & Partners Solicitors")
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_INACTIVE

        url = url_for("main.change_office_debt_recovery", firm=firm, office=office)
        payload = {"status": "Yes"}
        client.post(url, data=payload)

        # reload the office
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_DEBT_RECOVERY

    def test_debt_recovery_set_to_no(self, app, client):
        """Test that changing Debt recovery from yes to no, should set the contract manager to Mr ISD Default"""

        firm = get_firm_by_name(app, "Smith & Partners Solicitors")
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_INACTIVE

        url = url_for("main.change_office_debt_recovery", firm=firm, office=office)
        payload = {"status": "Yes"}
        client.post(url, data=payload)

        # reload the office
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == STATUS_CONTRACT_MANAGER_DEBT_RECOVERY

        # Change Debt recovery to No
        payload = {"status": "No"}
        client.post(url, data=payload)
        # reload the office
        office = get_firm_office_by_office_code(app, "1A001L")
        assert office.contract_manager == DEFAULT_CONTRACT_MANAGER_NAME
