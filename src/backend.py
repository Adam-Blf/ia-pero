"""
L'IA Pero - Backend RAG & Guardrail
Moteur de verification semantique pour requetes cocktails
Integre Google Gemini pour generation de recettes personnalisees

Author: Adam Beloucif & Amina Medjdoub
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import logging
import os
import re

import numpy as np
from sentence_transformers import SentenceTransformer, util

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# CONFIGURATION
# =============================================================================
MODEL_NAME = "all-MiniLM-L6-v2"
COCKTAIL_KEYWORDS = [
    "cocktail", "alcool", "boisson", "mojito", "whisky", "rhum", "vodka",
    "gin", "biere", "vin", "aperitif", "digestif", "bar", "barman", "shaker",
    "martini", "margarita", "daiquiri", "negroni", "spritz", "punch", "tequila"
]
RELEVANCE_THRESHOLD = 0.35
CACHE_FILE = Path("data/recipe_cache.json")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
            "message": "Desole, le barman ne comprend que les commandes de boissons !"
        }

    return {"status": "ok", "similarity": max_similarity}


# =============================================================================
# GOOGLE GEMINI INTEGRATION
# =============================================================================
SPEAKEASY_PROMPT = """Tu es un barman expert des annees 1920 dans un speakeasy clandestin de Paris.
Tu parles avec elegance et mystere. Tu connais tous les secrets des cocktails classiques et modernes.

L'utilisateur te demande: "{query}"

Cree une recette de cocktail unique et personnalisee basee sur cette demande.

IMPORTANT: Reponds UNIQUEMENT avec un objet JSON valide (pas de texte avant ou apres).
Structure exacte requise:
{{
  "name": "Nom creatif et evocateur du cocktail",
  "ingredients": ["60ml Spiritueux principal", "30ml Mixer ou jus", "15ml Liqueur ou sirop", "Garniture"],
  "instructions": "1. Etape detaillee... 2. Etape detaillee... 3. Servir avec elegance.",
  "taste_profile": {{"Douceur": 3.5, "Acidite": 2.5, "Amertume": 2.0, "Force": 4.0, "Fraicheur": 3.0}}
}}

Les valeurs de taste_profile doivent etre entre 1.5 et 5.0.
Sois creatif avec le nom, inspire-toi de l'epoque des annees folles."""


def _call_gemini_api(query: str) -> dict | None:
    """
    Call Google Gemini API to generate a cocktail recipe.

    Uses gemini-1.5-flash model with Speakeasy persona prompt.
    Validates and parses the JSON response.

    Args:
        query: User's cocktail request

    Returns:
        dict with recipe data or None if API call fails
    """
    if not GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY not configured - using fallback mode")
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=GOOGLE_API_KEY)
        # Try multiple models in order of preference
        model_names = ["gemini-1.5-flash-latest", "gemini-1.5-pro-latest", "gemini-pro"]
        model = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                break
            except Exception:
                continue
        if model is None:
            model = genai.GenerativeModel("gemini-pro")

        prompt = SPEAKEASY_PROMPT.format(query=query)
        response = model.generate_content(prompt)

        if not response or not response.text:
            logger.error("Empty response from Gemini API")
            return None

        # Extract JSON from response (handle markdown code blocks)
        response_text = response.text.strip()
        if response_text.startswith("```"):
            # Remove markdown code block markers
            response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
            response_text = re.sub(r"\s*```$", "", response_text)

        recipe_data = json.loads(response_text)

        # Validate required fields
        required_fields = ["name", "ingredients", "instructions", "taste_profile"]
        if not all(field in recipe_data for field in required_fields):
            logger.error(f"Missing required fields in Gemini response")
            return None

        # Ensure taste_profile has all required dimensions
        taste_required = ["Douceur", "Acidite", "Amertume", "Force", "Fraicheur"]
        taste_profile = recipe_data.get("taste_profile", {})
        for dim in taste_required:
            if dim not in taste_profile:
                taste_profile[dim] = 3.0  # Default value

        recipe_data["taste_profile"] = taste_profile
        recipe_data["query"] = query

        return recipe_data

    except ImportError:
        logger.error("google-generativeai package not installed")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse Gemini response as JSON: {e}")
        return None
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        return None


def _generate_fallback_recipe(query: str) -> dict:
    """
    Generate a fallback recipe when Gemini API is unavailable.

    Creates a basic cocktail suggestion based on keywords in the query.

    Args:
        query: User's cocktail request

    Returns:
        dict with basic recipe data
    """
    query_lower = query.lower()

    # Detect flavor preferences
    if any(w in query_lower for w in ["frais", "fresh", "rafraichissant", "ete"]):
        base_spirit = "Vodka"
        profile = {"Douceur": 3.0, "Acidite": 3.5, "Amertume": 1.5, "Force": 3.0, "Fraicheur": 4.5}
    elif any(w in query_lower for w in ["fort", "strong", "whisky", "bourbon"]):
        base_spirit = "Whisky Bourbon"
        profile = {"Douceur": 2.5, "Acidite": 2.0, "Amertume": 3.0, "Force": 4.5, "Fraicheur": 2.0}
    elif any(w in query_lower for w in ["tropical", "exotique", "fruit"]):
        base_spirit = "Rhum blanc"
        profile = {"Douceur": 4.0, "Acidite": 2.5, "Amertume": 1.5, "Force": 3.0, "Fraicheur": 4.0}
    elif any(w in query_lower for w in ["amer", "bitter", "negroni"]):
        base_spirit = "Gin"
        profile = {"Douceur": 2.0, "Acidite": 2.0, "Amertume": 4.5, "Force": 4.0, "Fraicheur": 2.5}
    else:
        base_spirit = "Gin"
        profile = {"Douceur": 3.0, "Acidite": 3.0, "Amertume": 2.5, "Force": 3.5, "Fraicheur": 3.5}

    return {
        "name": f"Le Secret du Speakeasy",
        "ingredients": [
            f"50ml {base_spirit}",
            "25ml Jus de citron frais",
            "20ml Sirop simple",
            "Zeste de citron"
        ],
        "instructions": "1. Dans un shaker, verser tous les ingredients avec de la glace. 2. Shaker vigoureusement pendant 15 secondes. 3. Filtrer dans un verre coupe refroidi. 4. Garnir avec le zeste de citron.",
        "taste_profile": profile,
        "query": query
    }


# =============================================================================
# RECIPE CACHE MANAGEMENT
# =============================================================================
def _get_cache_key(query: str) -> str:
    """Generate MD5 hash key for cache lookup."""
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


def _load_cache() -> dict:
    """Load recipe cache from JSON file."""
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            logger.warning("Cache file corrupted, starting fresh")
            return {}
    return {}


def _save_cache(cache: dict) -> None:
    """Save recipe cache to JSON file."""
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


# =============================================================================
# MAIN RECIPE GENERATION
# =============================================================================
def generate_recipe(query: str) -> dict:
    """
    Generate or retrieve a cocktail recipe.

    Pipeline:
    1. Validate query using semantic guardrail
    2. Check JSON cache for existing recipe (cost optimization)
    3. Call Gemini API for new generation
    4. Fallback to basic recipe if API unavailable
    5. Cache result for future requests

    Args:
        query: User query for cocktail recipe

    Returns:
        dict with recipe information:
        - {"status": "ok", "recipe": {...}, "cached": bool} on success
        - {"status": "error", "message": "..."} if off-topic
    """
    # Step 1: Guardrail - Check relevance
    relevance = check_relevance(query)
    if relevance["status"] == "error":
        return relevance

    # Step 2: Check cache (cost optimization - avoids redundant API calls)
    cache_key = _get_cache_key(query)
    cache = _load_cache()

    if cache_key in cache:
        logger.info(f"Cache hit for query: {query[:50]}...")
        return {"status": "ok", "recipe": cache[cache_key], "cached": True}

    # Step 3: Generate with Gemini API
    logger.info(f"Generating new recipe for: {query[:50]}...")
    recipe = _call_gemini_api(query)

    # Step 4: Fallback if API fails
    if recipe is None:
        logger.info("Using fallback recipe generation")
        recipe = _generate_fallback_recipe(query)

    # Step 5: Cache the result
    cache[cache_key] = recipe
    _save_cache(cache)

    return {"status": "ok", "recipe": recipe, "cached": False}
