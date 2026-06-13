"""
Tests for the persistent SQLite recipe cache in src/backend.py.

Validates that:
- Cache misses return None
- Cache hits return the stored value
- MD5 keying is consistent across restarts (deterministic)
- The cache survives a connection close/reopen cycle
- cache_size() reflects the number of stored entries
"""
import json
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _md5(query: str) -> str:
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


SAMPLE_RECIPE = {
    "name": "Test Cocktail",
    "ingredients": ["50ml Gin", "20ml Citron"],
    "instructions": "Mélanger et servir.",
    "taste_profile": {"Douceur": 3.0, "Acidite": 3.5, "Amertume": 2.0,
                      "Force": 3.5, "Fraicheur": 4.0, "Prix": 2.5, "Qualite": 3.0},
    "query": "un gin citronné",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_cache(tmp_path, monkeypatch):
    """Redirect SQLITE_CACHE_FILE to a temp directory for isolation."""
    db_path = tmp_path / "recipe_cache.db"
    monkeypatch.setattr("src.backend.SQLITE_CACHE_FILE", db_path)
    return db_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_cache_miss_returns_none(tmp_cache):
    """_cache_get returns None when the key is absent."""
    from src.backend import _cache_get
    result = _cache_get(_md5("nonexistent query"))
    assert result is None


def test_cache_set_then_get_roundtrip(tmp_cache):
    """A recipe stored with _cache_set is retrievable with _cache_get."""
    from src.backend import _cache_get, _cache_set

    key = _md5("un gin citronné")
    _cache_set(key, SAMPLE_RECIPE)
    retrieved = _cache_get(key)

    assert retrieved is not None
    assert retrieved["name"] == SAMPLE_RECIPE["name"]
    assert retrieved["ingredients"] == SAMPLE_RECIPE["ingredients"]


def test_cache_key_deterministic():
    """MD5 key for the same query is always identical (case-insensitive, stripped)."""
    from src.backend import _get_cache_key
    k1 = _get_cache_key("  Mojito Tropical  ")
    k2 = _get_cache_key("mojito tropical")
    assert k1 == k2


def test_cache_upsert_overwrites(tmp_cache):
    """Re-inserting the same key replaces the old value."""
    from src.backend import _cache_get, _cache_set

    key = _md5("test query")
    _cache_set(key, {"name": "v1"})
    _cache_set(key, {"name": "v2"})
    assert _cache_get(key)["name"] == "v2"


def test_cache_persists_across_connections(tmp_cache):
    """Data written in one connection is readable in a new connection."""
    from src.backend import _cache_get, _cache_set

    key = _md5("persistent test")
    _cache_set(key, SAMPLE_RECIPE)

    # Simulate a restart by importing a fresh connection
    import importlib
    import src.backend as backend_module
    importlib.reload(backend_module)

    # After reload SQLITE_CACHE_FILE is reset to default; re-patch and retrieve
    with patch.object(backend_module, "SQLITE_CACHE_FILE", tmp_cache):
        retrieved = backend_module._cache_get(key)

    assert retrieved is not None
    assert retrieved["name"] == SAMPLE_RECIPE["name"]


def test_cache_size(tmp_cache):
    """cache_size() returns the correct count of stored entries."""
    from src.backend import _cache_set, cache_size

    assert cache_size() == 0
    _cache_set(_md5("first"), {"name": "A"})
    _cache_set(_md5("second"), {"name": "B"})
    assert cache_size() == 2


def test_generate_recipe_uses_sqlite_cache(tmp_cache, monkeypatch):
    """generate_recipe() returns cached=True on second call (SQLite hit)."""
    from src.backend import generate_recipe

    # Prevent Gemini API calls
    monkeypatch.setattr("src.backend.GOOGLE_API_KEY", "")

    query = "un mojito classique"
    result1 = generate_recipe(query)
    assert result1["status"] == "ok"
    assert result1["cached"] is False

    result2 = generate_recipe(query)
    assert result2["status"] == "ok"
    assert result2["cached"] is True
    assert result2["recipe"]["name"] == result1["recipe"]["name"]
