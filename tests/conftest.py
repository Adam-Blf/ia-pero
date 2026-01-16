"""
Playwright fixtures configuration for L'IA Pero tests.
"""
import pytest
from playwright.sync_api import Browser


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context for tests."""
    return {
        **browser_context_args,
        "viewport": {"width": 1280, "height": 720},
        "locale": "fr-FR",
    }
