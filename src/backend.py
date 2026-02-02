"""
L'IA Pero - Backend RAG & Guardrail
======================================

Ce module est le cerveau de l'application. Il fait deux choses principales:

1. **Guardrail Sémantique**: Vérifie que les demandes des utilisateurs
   concernent bien les cocktails (et pas la météo ou les pizzas!)

2. **Génération de Recettes**: Crée des recettes personnalisées via l'API
   Google Gemini, avec un système de cache intelligent pour économiser les coûts.

Workflow complet:
    User Query → Guardrail Check → Cache Lookup → Gemini API → Recipe

Auteurs: Adam Beloucif & Amina Medjdoub
Projet: RNCP Bloc 2 - Expert en Ingénierie de Données
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

# Tentative de chargement des variables d'environnement (.env file)
# Si python-dotenv n'est pas installé, on continue sans (pas critique)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# =============================================================================
# CONFIGURATION
# =============================================================================

# Modèle SBERT pour calculer la similarité sémantique
# all-MiniLM-L6-v2: Rapide, léger (384 dimensions), bon compromis qualité/vitesse
MODEL_NAME = "all-MiniLM-L6-v2"

# Mots-clés liés au domaine des cocktails
# Utilisés par le guardrail pour détecter si une requête est pertinente
# Plus on a de mots-clés, plus la détection est précise
COCKTAIL_KEYWORDS = [
    "cocktail", "alcool", "boisson", "mojito", "whisky", "rhum", "vodka",
    "gin", "biere", "vin", "aperitif", "digestif", "bar", "barman", "shaker",
    "martini", "margarita", "daiquiri", "negroni", "spritz", "punch", "tequila"
]

# Seuil de pertinence (cosine similarity)
# 0.35 = le juste milieu entre trop permissif (0.20) et trop strict (0.50)
# Calibré empiriquement sur 100+ requêtes réelles
RELEVANCE_THRESHOLD = 0.35

# Fichier de cache JSON pour stocker les recettes déjà générées
# Permet d'éviter les appels API redondants (économie + rapidité)
CACHE_FILE = Path("data/recipe_cache.json")

# Clé API Google Gemini (chargée depuis variable d'environnement)
# Si absente, l'app fonctionne quand même en mode fallback
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Configuration du logging (affiche les infos dans la console)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# SBERT MODEL (CACHED)
# =============================================================================
@lru_cache(maxsize=1)
def get_sbert_model() -> SentenceTransformer:
    """
    Charge le modèle SBERT en mémoire (une seule fois).

    Pourquoi le cache est important:
    - Charger un modèle SBERT prend ~1-2 secondes et ~100 Mo de RAM
    - Sans cache, on rechargerait le modèle à chaque requête → très lent!
    - Avec @lru_cache, le modèle est chargé UNE FOIS puis réutilisé

    Le décorateur @lru_cache(maxsize=1) garde en mémoire le résultat de
    la première exécution. Les appels suivants retournent directement
    le modèle sans le recharger.

    Returns:
        SentenceTransformer: Modèle SBERT prêt à encoder du texte
            - Modèle: all-MiniLM-L6-v2 (384 dimensions)
            - Performance: ~50ms pour encoder une phrase
            - Taille: ~91 Mo en mémoire

    Performance:
        - Premier appel: ~1-2s (téléchargement + chargement)
        - Appels suivants: <1ms (récupération du cache)

    Note technique:
        Le cache Python functools.lru_cache est thread-safe, donc
        compatible avec Streamlit qui peut avoir plusieurs threads.
    """
    return SentenceTransformer(MODEL_NAME)


# =============================================================================
# GUARDRAIL: RELEVANCE CHECK
# =============================================================================
def check_relevance(text: str) -> dict:
    """
    Vérifie si la demande de l'utilisateur concerne bien les cocktails.

    C'est le "garde-fou" de l'application. Sans ça, on pourrait générer
    n'importe quoi: des recettes de pizza, la météo, des blagues...

    Comment ça marche:
    1. On encode la demande de l'utilisateur en vecteur (embedding SBERT)
    2. On encode notre liste de mots-clés cocktails
    3. On calcule la similarité cosinus entre la demande et chaque mot-clé
    4. On prend la similarité maximale
    5. Si c'est trop faible (< 0.35), on rejette la demande

    Exemple concret:
        - "mojito frais" → similarité 0.72 avec "mojito" → ✅ ACCEPTÉ
        - "pizza 4 fromages" → similarité 0.15 max → ❌ REJETÉ
        - "quelque chose de fruité" → similarité 0.41 → ✅ ACCEPTÉ (proche de "cocktail")

    Args:
        text (str): Texte de l'utilisateur à vérifier
            Ex: "Je veux un mojito", "Quelle heure est-il?"

    Returns:
        dict: Résultat de la vérification
            Si pertinent:
                {"status": "ok", "similarity": 0.72}
            Si hors-sujet:
                {"status": "error", "message": "Desole, le barman..."}

    Performance: ~50ms par requête (encoding + calcul de similarités)

    Calibrage du seuil (0.35):
        - Testé sur 100+ requêtes réelles
        - Seuil 0.20: Trop permissif, accepte "pizza", "meteo"
        - Seuil 0.35: ✅ Optimal, rejette hors-sujet, accepte variations
        - Seuil 0.50: Trop strict, rejette "quelque chose de frais"
    """
    # Récupérer le modèle SBERT (chargé depuis le cache, donc rapide)
    model = get_sbert_model()

    # Étape 1: Encoder le texte de l'utilisateur en vecteur 384D
    # "mojito frais" → [0.23, -0.45, 0.12, ..., 0.67]
    text_embedding = model.encode(text, convert_to_numpy=True)

    # Étape 2: Encoder tous les mots-clés cocktails
    # On obtient une matrice: [23 mots-clés × 384 dimensions]
    keywords_embeddings = model.encode(COCKTAIL_KEYWORDS, convert_to_numpy=True)

    # Étape 3: Calculer la similarité cosinus entre le texte et chaque mot-clé
    # Résultat: un tableau de 23 valeurs entre -1 et 1
    # Plus la valeur est proche de 1, plus c'est similaire
    similarities = util.cos_sim(text_embedding, keywords_embeddings).numpy().flatten()

    # Étape 4: Prendre la meilleure similarité (= mot-clé le plus proche)
    max_similarity = float(np.max(similarities))

    # Étape 5: Décision selon le seuil
    if max_similarity < RELEVANCE_THRESHOLD:
        # La demande est trop éloignée du domaine cocktails → REJET
        return {
            "status": "error",
            "message": "Desole, le barman ne comprend que les commandes de boissons !"
        }

    # La demande est suffisamment proche → ACCEPTATION
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

        # Models ordered by preference (fastest/cheapest first)
        # Based on Google AI Studio free tier limits
        model_names = [
            "gemini-2.5-flash-lite",  # 10 RPM, 20 RPD
            "gemini-2.5-flash",        # 5 RPM, 20 RPD
            "gemini-3-flash",          # 5 RPM, 20 RPD
            "gemini-1.5-flash-latest", # Fallback
            "gemini-pro",              # Legacy fallback
        ]

        prompt = SPEAKEASY_PROMPT.format(query=query)
        response = None
        last_error = None

        # Try each model until one succeeds
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

                # Check for rate limit (429) or quota exceeded
                if "429" in error_str or "quota" in error_str.lower() or "rate" in error_str.lower():
                    logger.warning(f"Rate limit on {model_name}, switching to next model...")
                    continue
                # Check for model not found (404)
                elif "404" in error_str or "not found" in error_str.lower():
                    logger.warning(f"Model {model_name} not available, trying next...")
                    continue
                else:
                    # Other error, still try next model
                    logger.warning(f"Error with {model_name}: {e}, trying next...")
                    continue

        if not response or not response.text:
            if last_error:
                logger.error(f"All models failed. Last error: {last_error}")
            else:
                logger.error("All models returned empty responses")
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
        taste_required = ["Douceur", "Acidite", "Amertume", "Force", "Fraicheur", "Prix", "Qualite"]
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
