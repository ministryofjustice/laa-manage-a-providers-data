from datetime import date
from unittest.mock import Mock

from app.components.tag import Tag
from app.main.utils import get_office_tags


class TestGetOfficeTags:
    def test_office_with_inactive_date_returns_inactive_tag(self):
        office = Mock()
        office.inactive_date = date(2024, 9, 12)

        tags = get_office_tags(office)

        assert len(tags) == 1
        assert isinstance(tags[0], Tag)
        assert tags[0].to_gov_params()["text"] == "Inactive"
        assert tags[0].to_gov_params()["classes"] == "govuk-tag--grey"

    def test_office_without_inactive_date_returns_empty_list(self):
        office = Mock()
        office.inactive_date = None

        tags = get_office_tags(office)

        assert len(tags) == 0
        assert tags == []

    def test_office_with_falsy_inactive_date_returns_empty_list(self):
        office = Mock()
        office.inactive_date = ""

        tags = get_office_tags(office)

        assert len(tags) == 0
        assert tags == []
