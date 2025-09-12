import pytest
from flask import url_for
from playwright.sync_api import Page, expect


def navigate_to_chambers_contact_details(page: Page):
    """Helper function to navigate to Chambers Contact Details form via UI flow."""
    page.get_by_role("button", name="Start now").click()
   
    # Start with add parent provider
    page.goto(url_for("main.add_parent_provider", _external=True))

    # Fill provider details form (Chambers flow is simpler - goes directly to contact details)
    page.get_by_role("textbox", name="Provider name").fill("Test Chambers")
    page.get_by_role("radio", name="Chambers").click()
    page.get_by_role("button", name="Continue").click()

    # Fill all required fields
    page.get_by_role("textbox", name="Address line 1").fill("123 Chambers Street")
    page.get_by_role("textbox", name="Town or city").fill("Chambers City")
    page.get_by_role("textbox", name="Postcode").fill("CH1 2MB")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("textbox", name="Email address").fill("contact@testchambers.com")
    page.get_by_role("textbox", name="DX number").fill("DX789123")
    page.get_by_role("textbox", name="DX centre").fill("Chambers Centre")
    page.get_by_role("button", name="Submit").click()

    # Add liaison manager information
    page.get_by_role("textbox", name="First name").fill("Bob")
    page.get_by_role("textbox", name="Last name").fill("Jones")
    page.get_by_role("textbox", name="Email address").fill("bob.jones@testlsp.com")
    page.get_by_role("textbox", name="Telephone number").fill("01234567890")
    page.get_by_role("button", name="Submit").click()