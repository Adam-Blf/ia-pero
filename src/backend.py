"""
L'IA Pero - Backend RAG & Guardrail
======================================

Ce module est le cerveau de l'application. Il fait deux choses principales:

1. **Guardrail Sémantique (deux niveaux)**: Vérifie que les demandes des
   utilisateurs concernent bien les cocktails (et pas la météo ou les pizzas!)
   - Niveau 1 (rapide) : correspondance lexicale par mots-clés
   - Niveau 2 (sémantique) : similarité cosinus SBERT ≥ 0.35

2. **Génération de Recettes**: Crée des recettes personnalisées via l'API
   Google Gemini, avec un cache SQLite persistant qui survit aux redémarrages
   et borne réellement les appels gratuits vers Gemini.

Workflow complet:
    User Query → Guardrail Check (L1 keyword → L2 SBERT) → SQLite Cache → Gemini API → Recipe

Auteurs: Adam Beloucif & Émilien Morice
Projet: RNCP Bloc 2 - Expert en Ingénierie de Données
"""
from functools import lru_cache
from pathlib import Path
import hashlib
import json
import logging
import os
import re
import sqlite3

import numpy as np
from sentence_transformers import SentenceTransformer, util

# Tentative de chargement des variables d'environnement (.env file)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# CONFIGURATION
# =============================================================================

MODEL_NAME = "all-MiniLM-L6-v2"

# Mots-clés domaine cocktails - utilisés par le guardrail niveau 1 (lexical)
COCKTAIL_KEYWORDS = [
    "cocktail", "alcool", "boisson", "mojito", "whisky", "rhum", "vodka",
    "gin", "biere", "vin", "aperitif", "digestif", "bar", "barman", "shaker",
    "martini", "margarita", "daiquiri", "negroni", "spritz", "punch", "tequila",
    "beer", "wine", "drink", "spirit", "liqueur", "champagne", "prosecco",
    "bourbon", "cognac", "brandy", "rum", "sake", "mezcal", "cider", "soda",
    "mocktail", "sirop", "citron", "menthe", "glacon", "verre", "shaker",
]

# Seuil de pertinence SBERT (niveau 2) - calibré empiriquement sur 100+ requêtes
RELEVANCE_THRESHOLD = 0.35

# Cache SQLite persistant (survit aux redémarrages, borné par la taille du disque)
SQLITE_CACHE_FILE = Path("data/recipe_cache.db")

# Clé API Google Gemini (chargée depuis .env / env var)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Indicateur public : True si la génération IA est disponible
GEMINI_AVAILABLE: bool = bool(GOOGLE_API_KEY)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# SBERT MODEL (CACHED)
# =============================================================================
@lru_cache(maxsize=1)
def get_sbert_model() -> SentenceTransformer:
    """
    Charge le modèle SBERT en mémoire (une seule fois, thread-safe via lru_cache).

    Returns:
        SentenceTransformer: Modèle all-MiniLM-L6-v2 (384 dimensions)
    """
    return SentenceTransformer(MODEL_NAME)


# =============================================================================
# SQLITE PERSISTENT CACHE
# =============================================================================

def _get_db_conn() -> sqlite3.Connection:
    """Open SQLite connection and ensure the recipe_cache table exists."""
    SQLITE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(SQLITE_CACHE_FILE))
    conn.execute(
        "CREATE TABLE IF NOT EXISTS recipe_cache ("
        "  key      TEXT PRIMARY KEY,"
        "  value    TEXT NOT NULL,"
        "  created_at TEXT DEFAULT (datetime('now'))"
        ")"
    )
    conn.commit()
    return conn


def _cache_get(key: str) -> dict | None:
    """Return a cached recipe dict for *key*, or None on cache miss.

    Args:
        key: MD5 hex digest of the normalized query string.

    Returns:
        Parsed recipe dict, or None if not found / error.
    """
    try:
        conn = _get_db_conn()
        row = conn.execute(
            "SELECT value FROM recipe_cache WHERE key = ?", (key,)
        ).fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
    except Exception as exc:
        logger.warning("SQLite cache read error: %s", exc)
    return None


def _cache_set(key: str, value: dict) -> None:
    """Store a recipe in the SQLite cache (upsert).

    Args:
        key: MD5 hex digest of the normalized query string.
        value: Recipe dict to persist.
    """
    try:
        serialized = json.dumps(value, ensure_ascii=False)
        conn = _get_db_conn()
        conn.execute(
            "INSERT OR REPLACE INTO recipe_cache (key, value) VALUES (?, ?)",
            (key, serialized),
        )
        conn.commit()
        conn.close()
    except Exception as exc:
        logger.warning("SQLite cache write error: %s", exc)


def _get_cache_key(query: str) -> str:
    """Generate MD5 hash key for cache lookup (normalized input)."""
    return hashlib.md5(query.lower().strip().encode()).hexdigest()


def cache_size() -> int:
    """Return the number of entries in the persistent recipe cache."""
    try:
        conn = _get_db_conn()
        count = conn.execute("SELECT COUNT(*) FROM recipe_cache").fetchone()[0]
        conn.close()
        return count
    except Exception:
        return 0


# =============================================================================
# GUARDRAIL: TWO-LEVEL RELEVANCE CHECK
# =============================================================================
def check_relevance(text: str) -> dict:
    """
    Vérifie si la demande concerne les cocktails via un guardrail en deux niveaux.

    Niveau 1 - Lexical (rapide, ~0 ms):
        Correspondance directe avec les mots-clés du domaine cocktails.
        Si un mot-clé est trouvé → acceptation immédiate (évite les faux rejets
        pour des requêtes courtes mais claires comme "rhum coca" ou "gin tonic").

    Niveau 2 - Sémantique SBERT (~50 ms):
        Calcule la similarité cosinus entre la requête et les mots-clés encodés.
        Si la similarité maximale est < 0.35 → rejet.

    Args:
        text: Texte de l'utilisateur à vérifier.

    Returns:
        dict contenant :
            - status   : "ok" ou "error"
            - similarity: score cosinus max (float, niveau 2 seulement)
            - reason   : "keyword_match" | "semantic_match" | "below_threshold"
            - message  : message d'erreur (si status == "error")
    """
    text_lower = text.lower()

    # ---- Niveau 1 : correspondance lexicale (coût nul) ----
    if any(kw in text_lower for kw in COCKTAIL_KEYWORDS):
        return {
            "status": "ok",
            "similarity": 1.0,
            "reason": "keyword_match",
        }

    # ---- Niveau 2 : similarité sémantique SBERT ----
    model = get_sbert_model()
    text_embedding = model.encode(text, convert_to_numpy=True)
    keywords_embeddings = model.encode(COCKTAIL_KEYWORDS, convert_to_numpy=True)
    similarities = util.cos_sim(text_embedding, keywords_embeddings).numpy().flatten()
    max_similarity = float(np.max(similarities))

    if max_similarity < RELEVANCE_THRESHOLD:
        return {
            "status": "error",
            "message": "Desole, le barman ne comprend que les commandes de boissons !",
            "reason": "below_threshold",
            "similarity": max_similarity,
        }

    return {
        "status": "ok",
        "similarity": max_similarity,
        "reason": "semantic_match",
    }


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
  "taste_profile": {{"Douceur": 3.5, "Acidite": 2.5, "Amertume": 2.0, "Force": 4.0, "Fraicheur": 3.0, "Prix": 3.0, "Qualite": 4.0}}
}}

Les valeurs de taste_profile doivent etre entre 1.5 et 5.0.
- Prix: 1.5 = tres abordable, 5.0 = ingredients de luxe
- Qualite: 1.5 = cocktail simple, 5.0 = creation d'exception
Sois creatif avec le nom, inspire-toi de l'epoque des annees folles."""


def _call_gemini_api(query: str) -> dict | None:
    """
    Call Google Gemini API to generate a cocktail recipe.

    Automatically switches between models if rate limit (429) is reached.
    Models are tried in order of preference with automatic failover.

    Args:
        query: User's cocktail request

    Returns:
        dict with recipe data or None if all models fail
    """
    if not GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY not configured - using fallback mode")
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=GOOGLE_API_KEY)

        model_names = [
            "gemini-2.5-flash-lite",
            "gemini-2.5-flash",
            "gemini-3-flash",
            "gemini-1.5-flash-latest",
            "gemini-pro",
        ]

        prompt = SPEAKEASY_PROMPT.format(query=query)
        response = None
        last_error = None

        for model_name in model_names:
            try:
                logger.info(f"Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)

                if response and response.text:
                    logger.info(f"Success with model: {model_name}")
                    break
                else:
                    logger.warning(f"Empty response from {model_name}, trying next...")
                    response = None

            except Exception as e:
                error_str = str(e)
                last_error = e

                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    logger.warning(f"Rate limit on {model_name}, switching to next model...")
                    continue
                elif "404" in error_str or "not found" in error_str.lower():
                    logger.warning(f"Model {model_name} not available, trying next...")
                    continue
                else:
                    logger.warning(f"Error with {model_name}: {e}, trying next...")
                    continue

        if not response or not response.text:
            if last_error:
                logger.error(f"All models failed. Last error: {last_error}")
            else:
                logger.error("All models returned empty responses")
            return None

        response_text = response.text.strip()
        if response_text.startswith("```"):
            response_text = re.sub(r"^```(?:json)?\s*", "", response_text)
            response_text = re.sub(r"\s*```$", "", response_text)

        recipe_data = json.loads(response_text)

        required_fields = ["name", "ingredients", "instructions", "taste_profile"]
        if not all(field in recipe_data for field in required_fields):
            logger.error("Missing required fields in Gemini response")
            return None

        taste_required = ["Douceur", "Acidite", "Amertume", "Force", "Fraicheur", "Prix", "Qualite"]
        taste_profile = recipe_data.get("taste_profile", {})
        for dim in taste_required:
            if dim not in taste_profile:
                taste_profile[dim] = 3.0

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

    Args:
        query: User's cocktail request

    Returns:
        dict with basic recipe data
    """
    query_lower = query.lower()

    if any(w in query_lower for w in ["frais", "fresh", "rafraichissant", "ete"]):
        base_spirit = "Vodka"
        profile = {"Douceur": 3.0, "Acidite": 3.5, "Amertume": 1.5, "Force": 3.0, "Fraicheur": 4.5, "Prix": 2.5, "Qualite": 3.5}
    elif any(w in query_lower for w in ["fort", "strong", "whisky", "bourbon"]):
        base_spirit = "Whisky Bourbon"
        profile = {"Douceur": 2.5, "Acidite": 2.0, "Amertume": 3.0, "Force": 4.5, "Fraicheur": 2.0, "Prix": 4.0, "Qualite": 4.5}
    elif any(w in query_lower for w in ["tropical", "exotique", "fruit"]):
        base_spirit = "Rhum blanc"
        profile = {"Douceur": 4.0, "Acidite": 2.5, "Amertume": 1.5, "Force": 3.0, "Fraicheur": 4.0, "Prix": 3.0, "Qualite": 3.5}
    elif any(w in query_lower for w in ["amer", "bitter", "negroni"]):
        base_spirit = "Gin"
        profile = {"Douceur": 2.0, "Acidite": 2.0, "Amertume": 4.5, "Force": 4.0, "Fraicheur": 2.5, "Prix": 3.5, "Qualite": 4.0}
    else:
        base_spirit = "Gin"
        profile = {"Douceur": 3.0, "Acidite": 3.0, "Amertume": 2.5, "Force": 3.5, "Fraicheur": 3.5, "Prix": 3.0, "Qualite": 3.5}

    return {
        "name": "Le Secret du Speakeasy",
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
# MAIN RECIPE GENERATION
# =============================================================================
def generate_recipe(query: str) -> dict:
    """
    Generate or retrieve a cocktail recipe.

    Pipeline:
    1. Validate query using the two-level semantic guardrail
    2. Check persistent SQLite cache (cost optimization)
    3. Call Gemini API for new generation
    4. Fallback to local recipe if API unavailable
    5. Persist result in SQLite cache

    Args:
        query: User query for cocktail recipe

    Returns:
        dict:
        - {"status": "ok", "recipe": {...}, "cached": bool} on success
        - {"status": "error", "message": "...", "reason": str} if off-topic
    """
    # Step 1: Two-level guardrail
    relevance = check_relevance(query)
    if relevance["status"] == "error":
        return relevance

    # Step 2: SQLite persistent cache lookup
    cache_key = _get_cache_key(query)
    cached_recipe = _cache_get(cache_key)
    if cached_recipe is not None:
        logger.info("Cache hit for query: %s...", query[:50])
        return {"status": "ok", "recipe": cached_recipe, "cached": True}

    # Step 3: Generate with Gemini API
    logger.info("Generating new recipe for: %s...", query[:50])
    recipe = _call_gemini_api(query)

    # Step 4: Fallback if API fails
    if recipe is None:
        logger.info("Using fallback recipe generation")
        recipe = _generate_fallback_recipe(query)

    # Step 5: Persist in SQLite cache
    _cache_set(cache_key, recipe)

    return {"status": "ok", "recipe": recipe, "cached": False}
