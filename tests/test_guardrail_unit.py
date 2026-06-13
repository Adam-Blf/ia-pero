"""
Unit tests for the three-level semantic guardrail in src/backend.py.

Does NOT require Streamlit or a running app - imports backend directly.
Covers:
  - Level 1  : cocktail keyword → immediate accept
  - Level 2a : gray-zone SBERT score + rescue keyword → accept
  - Level 2b : SBERT score >= threshold + out-of-domain keyword → reject
  - Level 2  : plain below-threshold → reject
  - Reason field is always present and matches expected value
"""
from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Level 1 – cocktail keyword match
# ---------------------------------------------------------------------------

class TestLevel1KeywordMatch:
    """Requests containing explicit cocktail keywords pass immediately."""

    def test_mojito_accepted(self):
        from src.backend import check_relevance
        result = check_relevance("Je veux un mojito")
        assert result["status"] == "ok"
        assert result["reason"] == "keyword_match"

    def test_gin_tonic_accepted(self):
        from src.backend import check_relevance
        result = check_relevance("Un gin tonic bien frais")
        assert result["status"] == "ok"
        assert result["reason"] == "keyword_match"

    def test_rhum_accepted(self):
        from src.backend import check_relevance
        result = check_relevance("Quelque chose avec du rhum")
        assert result["status"] == "ok"
        assert result["reason"] == "keyword_match"

    def test_bourbon_accepted(self):
        from src.backend import check_relevance
        result = check_relevance("Whisky sour au bourbon")
        assert result["status"] == "ok"
        assert result["reason"] == "keyword_match"


# ---------------------------------------------------------------------------
# Level 2 – clearly off-topic → below threshold
# ---------------------------------------------------------------------------

class TestLevel2BelowThreshold:
    """Clearly off-topic queries with no cocktail keyword must be rejected."""

    def test_capital_city_rejected(self):
        from src.backend import check_relevance
        result = check_relevance("Quelle est la capitale de la France ?")
        assert result["status"] == "error"
        assert result["reason"] in ("below_threshold", "out_of_domain_filtered")

    def test_math_homework_rejected(self):
        from src.backend import check_relevance
        result = check_relevance("Aide-moi à faire mes devoirs de mathématiques")
        assert result["status"] == "error"

    def test_weather_rejected(self):
        from src.backend import check_relevance
        result = check_relevance("Quel temps fait-il demain à Paris ?")
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Level 2b – out-of-domain keyword detected (false-positive filter)
# ---------------------------------------------------------------------------

class TestLevel2bOutOfDomainFilter:
    """Queries containing out-of-domain terms must be rejected even if
    SBERT scores them above the base threshold."""

    def test_bicycle_repair_rejected(self):
        from src.backend import check_relevance
        result = check_relevance("Comment réparer mon vélo ?")
        assert result["status"] == "error", (
            f"Expected rejection for bicycle query, got status={result['status']} "
            f"reason={result.get('reason')}"
        )

    def test_pizza_order_rejected(self):
        from src.backend import check_relevance
        result = check_relevance("Je veux commander une pizza 4 fromages")
        assert result["status"] == "error", (
            f"Expected rejection for pizza query, got status={result['status']} "
            f"reason={result.get('reason')}"
        )


# ---------------------------------------------------------------------------
# Reason field is always present
# ---------------------------------------------------------------------------

class TestReasonFieldAlwaysPresent:
    """The 'reason' key must always be present in the response."""

    @pytest.mark.parametrize("query", [
        "Je veux un mojito",
        "Comment réparer mon vélo ?",
        "Quelle heure est-il ?",
        "Quelque chose de fruité et frais",
        "Un negroni bien amer",
    ])
    def test_reason_field_present(self, query: str):
        from src.backend import check_relevance
        result = check_relevance(query)
        assert "reason" in result, f"'reason' missing for query: {query!r}"
        assert isinstance(result["reason"], str)
        assert len(result["reason"]) > 0

    @pytest.mark.parametrize("query", [
        "Je veux un mojito",
        "Comment réparer mon vélo ?",
        "Quelle heure est-il ?",
    ])
    def test_similarity_field_present(self, query: str):
        from src.backend import check_relevance
        result = check_relevance(query)
        assert "similarity" in result, f"'similarity' missing for query: {query!r}"
        assert isinstance(result["similarity"], float)
