from datetime import date

import pytest
from playwright.sync_api import Page, expect

from tests.functional_tests.utils import definition_list_to_dict, navigate_to_provider_page


def change_and_confirm_intervened(
    page: Page, intervened_date: str | None, provider_name: str, fail_on_purpose: bool = False
):
    """
    Helper function to change and confirm and intervention change of an office
    Args:
        page: Page element
        intervened_date: The date of the intervention or None if removing an intervention
        provider_name: The name of the provider
        fail_on_purpose: Set true if when clicking the submit button will fail with the no changes made error
    """

    status = "Yes" if intervened_date else "No"
    page.get_by_role("link", name="Change intervened").click()
    page.get_by_role("radio", name=status).click()

    expect(page.get_by_text("Date intervened")).to_be_visible(visible=status == "Yes")
    expect(page.get_by_role("textbox", name="Day")).to_be_visible(visible=status == "Yes")
    expect(page.get_by_role("textbox", name="Month")).to_be_visible(visible=status == "Yes")
    expect(page.get_by_role("textbox", name="Year")).to_be_visible(visible=status == "Yes")

    if intervened_date:
        day, month, year = intervened_date.split("/")
        page.get_by_role("textbox", name="Day").fill(day)
        page.get_by_role("textbox", name="Month").fill(month)
        page.get_by_role("textbox", name="Year").fill(year)

    page.get_by_role("button", name="Submit").click()

    if fail_on_purpose:
        expect(page.get_by_text("There is a problem")).to_be_visible()
    else:
        message = (
            f"{provider_name} marked as intervened."
            if intervened_date
            else f"{provider_name} marked as not intervened."
        )
        expect(page.get_by_text(message)).to_be_visible()

        data = definition_list_to_dict(page, dl_selector=".status-table")
        assert data["Intervened"] == f"Yes on {intervened_date}" if status == "Yes" else "No"


class TestAdvocateIntervened:
    provider_name = "Finn O'Connor"

    @pytest.mark.usefixtures("live_server")
    def test_change_firm_intervened_default_value(self, page: Page):
        """Test the default display value is No"""

        # Advocate
        navigate_to_provider_page(page, provider_name=self.provider_name)
        data = definition_list_to_dict(page, dl_selector=".status-table")
        assert data["Intervened"] == "No"

    @pytest.mark.usefixtures("live_server")
    def test_change_firm_intervened_yes(self, page: Page):
        """Test changing firm intervention from no to yes"""

        navigate_to_provider_page(page, provider_name=self.provider_name)
        # Make office intervened
        change_and_confirm_intervened(page, date.today().strftime("%d/%m/%Y"), provider_name=self.provider_name)

    @pytest.mark.usefixtures("live_server")
    def test_change_firm_intervened_no(self, page: Page):
        """Test changing firm intervention from yes to no"""

        navigate_to_provider_page(page, provider_name=self.provider_name)
        change_and_confirm_intervened(page, date.today().strftime("%d/%m/%Y"), provider_name=self.provider_name)

    @pytest.mark.usefixtures("live_server")
    def test_change_firm_intervened_no_changes__no(self, page: Page):
        """Test making no changes displays the correct `No` specific message"""

        navigate_to_provider_page(page, provider_name=self.provider_name)
        change_and_confirm_intervened(
            page, intervened_date=None, provider_name=self.provider_name, fail_on_purpose=True
        )
        expect(page.get_by_text("There is a problem")).to_be_visible()
        expect(
            page.get_by_role(
                "link", name="Select yes if they have been intervened. Cancel if you do not want to change the answer."
            )
        ).to_be_visible()

    @pytest.mark.usefixtures("live_server")
    def test_change_firm_intervened_no_changes__yes(self, page: Page):
        """Test making no changes displays the correct `Yes` specific message"""

        # Set intervened to Yes
        navigate_to_provider_page(page, provider_name=self.provider_name)
        change_and_confirm_intervened(page, "10/12/2025", provider_name=self.provider_name)

        # Submit without making changes
        navigate_to_provider_page(page, provider_name=self.provider_name)
        change_and_confirm_intervened(page, "10/12/2025", provider_name=self.provider_name, fail_on_purpose=True)

        expect(page.get_by_text("There is a problem")).to_be_visible()
        expect(
            page.get_by_role(
                "link",
                name="Select no if they have not been intervened. Cancel if you do not want to change the answer.",
            )
        ).to_be_visible()

    @pytest.mark.usefixtures("live_server")
    def test_change_office_intervened_cancel(self, page: Page):
        """Test cancelling intervention takes you back to the firms view page"""

        navigate_to_provider_page(page, provider_name=self.provider_name)
        url = page.url
        page.get_by_role("link", name="Change intervened").click()
        page.get_by_role("link", name="Cancel").click()
        assert url == page.url


class TestBarristerIntervened(TestAdvocateIntervened):
    provider_name = "Karen Sillen"
