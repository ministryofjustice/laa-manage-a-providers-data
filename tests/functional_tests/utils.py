from flask import url_for
from playwright.sync_api import Page, expect


def table_to_dict(page: Page, table_selector: str) -> dict:
    """Convert a two-column table (<th> + <td>) into a Python dict."""
    table_dict = {}
    rows = page.locator(f"{table_selector} tr")

    for i in range(rows.count()):
        row = rows.nth(i)
        header = row.locator("th").inner_text().strip()
        cell = row.locator("td").inner_text().strip()
        table_dict[header] = cell

    return table_dict


def definition_list_to_dict(page: Page, dl_selector: str) -> dict:
    """Convert a definition list (<dt> + <dd>) into a Python dict with dt as key and dd as value"""
    dl_dict = {}
    rows = page.locator(f"{dl_selector} div")
    for i in range(rows.count()):
        row = rows.nth(i)
        try:
            term = row.locator("dt").inner_text().strip()
            # Change links are added as an additional 'dd' element, so choose the first for the value
            value = row.locator("dd").first.inner_text().strip()
            dl_dict[term] = value
        except Exception as e:
            print(f"Failed to convert row {i} {row.all_inner_texts()}: {e}")
    return dl_dict


def navigate_to_provider_page(page: Page, provider_name: str, office_code: str | None = None):
    """Helper function to navigate to a given provider page."""
    # Navigate to the providers list
    page.goto(url_for("main.providers", _external=True))

    page.get_by_role("textbox", name="Find a provider").fill(provider_name)
    page.get_by_role("button", name="Search").click()

    # Click on the first provider
    page.get_by_role("link", name=provider_name).click()

    expect(page.get_by_role("heading", name=provider_name, level=1)).to_be_visible()

    if not office_code:
        return

    # Click on the Offices sub-navigation
    page.get_by_role("link", name="Offices").click()

    # Click "A specific office" button
    page.get_by_role("link", name=office_code).click()

    # Verify we're on view office page
    expect(page.get_by_role("heading", name=f"Office: {office_code}")).to_be_visible()
