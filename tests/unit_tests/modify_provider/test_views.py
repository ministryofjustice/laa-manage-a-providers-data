from unittest.mock import patch

from flask import url_for

from app.main.modify_provider.forms import ChangeProviderActiveStatusForm
from app.main.modify_provider.views import ChangeProviderActiveStatusFormView


class TestChangeProviderActiveStatusFormView:
    @patch("app.main.modify_provider.views.render_template")
    def test_get_inactive_firm(self, mock_render_template, app):
        """Test default form for an inactive provider firm."""
        pda = app.extensions["pda"]
        firm = pda.get_all_provider_firms()[0]
        assert firm.inactive_date is not None

        view = ChangeProviderActiveStatusFormView(form_class=ChangeProviderActiveStatusForm)
        view.get(firm, context={})
        call_kwargs = mock_render_template.call_args.kwargs
        assert call_kwargs["form"].status.data == "inactive"

    @patch("app.main.modify_provider.views.render_template")
    def test_get_active_firm(self, mock_render_template, app):
        """Test default form for an active provider firm."""
        pda = app.extensions["pda"]
        firm = pda.get_all_provider_firms()[1]
        assert firm.inactive_date is None

        view = ChangeProviderActiveStatusFormView(form_class=ChangeProviderActiveStatusForm)
        view.get(firm, context={})
        call_kwargs = mock_render_template.call_args.kwargs
        assert call_kwargs["form"].status.data == "active"

    def test_post_change_active_to_inactive(self, app, client):
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

    def test_post_change_inactive_to_active(self, app, client):
        """Test changing provider from inactive to active"""
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
