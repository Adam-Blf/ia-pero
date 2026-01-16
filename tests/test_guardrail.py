"""
L'IA Pero - Guardrail E2E Tests with Playwright
Tests the semantic relevance filter for cocktail queries
"""
import pytest
from playwright.sync_api import Page, expect


# =============================================================================
# CONFIGURATION
# =============================================================================
STREAMLIT_URL = "http://localhost:8501"
INPUT_PLACEHOLDER = "Un cocktail fruite et rafraichissant..."
BUTTON_TEXT = "Invoquer le Barman"
ERROR_TEXT = "Désolé"  # Part of the guardrail error message


# =============================================================================
# TEST CASES
# =============================================================================
class TestGuardrail:
    """Test suite for semantic guardrail validation."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page):
        """Navigate to app before each test."""
        page.goto(STREAMLIT_URL)
        # Wait for Streamlit to fully load
        page.wait_for_load_state("networkidle")
        # Give Streamlit time to initialize
        page.wait_for_timeout(2000)
        yield

    def test_off_topic_query_shows_error(self, page: Page):
        """
        SCENARIO: User asks an off-topic question (bike repair)
        EXPECTED: Guardrail rejects with "Désolé..." message
        """
        # Find the text input by placeholder
        input_field = page.get_by_placeholder(INPUT_PLACEHOLDER)
        input_field.fill("Comment réparer mon vélo ?")

        # Click the submit button
        submit_button = page.get_by_role("button", name=BUTTON_TEXT)
        submit_button.click()

        # Wait for and verify error message appears
        page.wait_for_timeout(5000)  # Wait for SBERT model loading + processing
        error_element = page.locator("text=Désolé")
        expect(error_element).to_be_visible(timeout=15000)

    def test_cocktail_query_shows_recipe(self, page: Page):
        """
        SCENARIO: User asks for a Mojito
        EXPECTED: Guardrail accepts and shows recipe card
        """
        # Find the text input by placeholder
        input_field = page.get_by_placeholder(INPUT_PLACEHOLDER)
        input_field.fill("Je veux un Mojito")

        # Click the submit button
        submit_button = page.get_by_role("button", name=BUTTON_TEXT)
        submit_button.click()

        # Wait for recipe to be generated
        page.wait_for_timeout(5000)  # Wait for SBERT model loading + processing

        # Verify recipe card appears (contains "Ingredients" section)
        # or the cocktail name appears
        recipe_section = page.locator("text=Ingredients")
        expect(recipe_section).to_be_visible(timeout=15000)


class TestGuardrailFlow:
    """Test complete user flow: off-topic → error → valid → success."""

    def test_complete_flow(self, page: Page):
        """
        SCENARIO: Full user journey testing guardrail behavior
        1. Ask off-topic question → see error
        2. Ask cocktail question → see recipe
        """
        # Navigate to app
        page.goto(STREAMLIT_URL)
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        # STEP 1: Off-topic query
        input_field = page.get_by_placeholder(INPUT_PLACEHOLDER)
        input_field.fill("Comment réparer mon vélo ?")

        submit_button = page.get_by_role("button", name=BUTTON_TEXT)
        submit_button.click()

        # Wait and verify error
        page.wait_for_timeout(5000)
        error_element = page.locator("text=Désolé")
        expect(error_element).to_be_visible(timeout=15000)

        # STEP 2: Clear and submit valid query
        # Reload page to reset state (Streamlit quirk)
        page.reload()
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(2000)

        input_field = page.get_by_placeholder(INPUT_PLACEHOLDER)
        input_field.fill("Je veux un Mojito")

        submit_button = page.get_by_role("button", name=BUTTON_TEXT)
        submit_button.click()

        # Wait and verify recipe
        page.wait_for_timeout(5000)
        recipe_section = page.locator("text=Ingredients")
        expect(recipe_section).to_be_visible(timeout=15000)


# =============================================================================
# RUN TESTS
# =============================================================================
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--headed"])
