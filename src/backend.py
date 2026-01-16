"""
L'IA Pero - Backend RAG & Guardrail
Moteur de verification semantique pour requetes cocktails
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json

import numpy as np
from sentence_transformers import SentenceTransformer, util


# =============================================================================
# CONFIGURATION
# =============================================================================
MODEL_NAME = "all-MiniLM-L6-v2"
COCKTAIL_KEYWORDS = ["cocktail", "alcool", "boisson", "mojito", "whisky", "rhum", "vodka", "gin", "bière", "vin", "apéritif", "digestif", "bar", "barman", "shaker"]
RELEVANCE_THRESHOLD = 0.35
CACHE_FILE = Path("data/recipe_cache.json")


# =============================================================================
# SBERT MODEL (CACHED)
# =============================================================================
@lru_cache(maxsize=1)
def get_sbert_model() -> SentenceTransformer:
    """Load SBERT model with memory cache (loaded once)."""
    return SentenceTransformer(MODEL_NAME)


# =============================================================================
# GUARDRAIL: RELEVANCE CHECK
# =============================================================================
def check_relevance(text: str) -> dict:
    """
    Check if user text is relevant to cocktails/beverages domain.

    Compares input text against cocktail-related keywords using
    semantic similarity. If the maximum similarity score is below
    the threshold, the request is rejected.

    Args:
        text: User input text to validate

    Returns:
        dict with status:
        - {"status": "ok", "similarity": float} if relevant to cocktails
        - {"status": "error", "message": "..."} if off-topic
    """
    model = get_sbert_model()

    # Encode user text and keywords
    text_embedding = model.encode(text, convert_to_numpy=True)
    keywords_embeddings = model.encode(COCKTAIL_KEYWORDS, convert_to_numpy=True)

    # Compute max similarity with any keyword
    similarities = util.cos_sim(text_embedding, keywords_embeddings).numpy().flatten()
    max_similarity = float(np.max(similarities))

    if max_similarity < RELEVANCE_THRESHOLD:
        return {
            "status": "error",
            "message": "🚫 Désolé, le barman ne comprend que les commandes de boissons !"
        }

    return {"status": "ok", "similarity": max_similarity}


# =============================================================================
# RECIPE GENERATION WITH JSON CACHE
# =============================================================================
def _get_cache_key(query: str) -> str:
    """Generate MD5 hash key for cache lookup."""
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


def _load_cache() -> dict:
    """Load recipe cache from JSON file."""
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_cache(cache: dict) -> None:
    """Save recipe cache to JSON file."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def generate_recipe(query: str) -> dict:
    """
    Generate or retrieve a cocktail recipe.

    First validates the query using the relevance guardrail,
    then checks the JSON cache for existing recipes.
    If not cached, generates a placeholder recipe and stores it.

    Args:
        query: User query for cocktail recipe

    Returns:
        dict with recipe information:
        - {"status": "ok", "recipe": {...}, "cached": bool} on success
        - {"status": "error", "message": "..."} if off-topic
    """
    # First check relevance (guardrail)
    relevance = check_relevance(query)
    if relevance["status"] == "error":
        return relevance

    # Check cache
    cache_key = _get_cache_key(query)
    cache = _load_cache()

    if cache_key in cache:
        return {"status": "ok", "recipe": cache[cache_key], "cached": True}

    # Generate recipe (placeholder - to be replaced with actual generation)
    recipe = {
        "name": f"Cocktail pour: {query}",
        "ingredients": ["À définir"],
        "instructions": "Recette à générer",
        "query": query
    }

    # Save to cache
    cache[cache_key] = recipe
    _save_cache(cache)

    return {"status": "ok", "recipe": recipe, "cached": False}
