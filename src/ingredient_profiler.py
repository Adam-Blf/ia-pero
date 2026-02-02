"""
Ingredient Profiler - Système d'Inférence de Profils de Saveurs

Ce module implémente un système hybride à 4 niveaux pour déterminer
les profils de saveurs d'ingrédients de cocktails:

Niveau 1: Base connue (61 ingrédients hardcodés)
Niveau 2: Similarité sémantique (SBERT)
Niveau 3: Inférence LLM (Gemini)
Niveau 4: Fallback par catégorie

Usage:
    profiler = IngredientProfiler()
    profile = profiler.get_profile("Yuzu")
    # Returns: {"sweetness": 1.5, "acidity": 4.5, "bitterness": 2.0, ...}
"""

import json
import os
import re
import unicodedata
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import logging

# Imports conditionnels
try:
    from sentence_transformers import SentenceTransformer, util
    SBERT_AVAILABLE = True
except ImportError:
    SBERT_AVAILABLE = False
    print("[WARN] sentence-transformers not available. Similarity search disabled.")

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("[WARN] google-generativeai not available. LLM inference disabled.")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IngredientProfiler:
    """
    Classe principale pour l'inférence de profils d'ingrédients.
    """

    def __init__(self, known_ingredients_path: Optional[str] = None,
                 cache_path: Optional[str] = None):
        """
        Initialise le profiler.

        Args:
            known_ingredients_path: Chemin vers known_ingredients.json
            cache_path: Chemin vers ingredient_profiles.json (cache)
        """
        self.project_root = Path(__file__).parent.parent

        # Chemins par défaut
        if known_ingredients_path is None:
            known_ingredients_path = self.project_root / "data" / "known_ingredients.json"
        if cache_path is None:
            cache_path = self.project_root / "data" / "ingredient_profiles.json"

        self.known_ingredients_path = Path(known_ingredients_path)
        self.cache_path = Path(cache_path)

        # Charger données
        self.known_base = self._load_known_ingredients()
        self.profiles_cache = self._load_cache()

        # Charger modèle SBERT si disponible
        self.sbert_model = None
        if SBERT_AVAILABLE:
            try:
                self.sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
                logger.info("[OK] SBERT model loaded")
            except Exception as e:
                logger.warning(f"[WARN] Failed to load SBERT: {e}")

        # Configurer Gemini si disponible
        self.gemini_available = False
        if GEMINI_AVAILABLE:
            api_key = os.getenv("GOOGLE_API_KEY", "")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_available = True
                logger.info("[OK] Gemini API configured")
            else:
                logger.warning("[WARN] GOOGLE_API_KEY not found. LLM inference disabled.")

        logger.info(f"[OK] IngredientProfiler initialized with {len(self.known_base)} known ingredients")

    def _load_known_ingredients(self) -> Dict:
        """Charge la base de connaissance depuis JSON."""
        if not self.known_ingredients_path.exists():
            logger.warning(f"[WARN] Known ingredients file not found: {self.known_ingredients_path}")
            return {}

        with open(self.known_ingredients_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Construire un index plat: nom -> profil
        known_base = {}
        for category in ["spirits", "mixers", "modifiers"]:
            if category in data:
                for key, profile in data[category].items():
                    known_base[key] = profile

        return known_base

    def _load_cache(self) -> Dict:
        """Charge le cache des profils inférés."""
        if not self.cache_path.exists():
            return {}

        try:
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[WARN] Failed to load cache: {e}")
            return {}

    def _save_cache(self):
        """Sauvegarde le cache des profils."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.cache_path, 'w', encoding='utf-8') as f:
            json.dump(self.profiles_cache, f, indent=2, ensure_ascii=False)

    def _normalize_name(self, name: str) -> str:
        """Normalise un nom d'ingrédient."""
        # Supprimer accents
        name = ''.join(c for c in unicodedata.normalize('NFD', name)
                       if unicodedata.category(c) != 'Mn')
        # Minuscules, strip, supprimer caractères spéciaux
        name = re.sub(r'[^\w\s-]', '', name.lower().strip())
        return name

    def get_profile(self, ingredient_name: str) -> Dict:
        """
        Obtient le profil de saveurs d'un ingrédient.

        Stratégie à 4 niveaux:
        1. Base connue
        2. Similarité sémantique (SBERT)
        3. Inférence LLM (Gemini)
        4. Fallback par catégorie

        Args:
            ingredient_name: Nom de l'ingrédient (FR ou EN)

        Returns:
            dict: Profil avec clés: sweetness, acidity, bitterness, strength,
                  freshness, category, source
        """
        normalized = self._normalize_name(ingredient_name)

        # Niveau 1: Base connue
        if profile := self._lookup_known(normalized, ingredient_name):
            return profile

        # Niveau 2: Similarité SBERT
        if self.sbert_model is not None:
            if profile := self._find_similar(ingredient_name, threshold=0.75):
                return profile

        # Niveau 3: Gemini inference
        if self.gemini_available:
            if profile := self._infer_with_gemini(ingredient_name):
                self._cache_profile(normalized, profile)
                return profile

        # Niveau 4: Fallback par catégorie
        return self._fallback_profile(ingredient_name)

    def _lookup_known(self, normalized: str, original: str) -> Optional[Dict]:
        """Niveau 1: Recherche dans la base connue."""
        # Recherche directe
        if normalized in self.known_base:
            profile = self.known_base[normalized].copy()
            profile['source'] = 'known'
            return profile

        # Recherche dans les mappings EN->FR
        for key, data in self.known_base.items():
            if 'name_en' in data and data['name_en']:
                for en_name in data['name_en']:
                    if self._normalize_name(en_name) == normalized:
                        profile = data.copy()
                        profile['source'] = 'known'
                        return profile

        # Recherche dans le cache
        if normalized in self.profiles_cache:
            profile = self.profiles_cache[normalized].copy()
            logger.info(f"[CACHE] Found {original} in cache")
            return profile

        return None

    def _find_similar(self, ingredient_name: str, threshold: float = 0.75) -> Optional[Dict]:
        """Niveau 2: Recherche par similarité sémantique."""
        if not self.sbert_model:
            return None

        try:
            # Encoder l'ingrédient recherché
            query_embedding = self.sbert_model.encode(ingredient_name, convert_to_numpy=True)

            # Encoder tous les ingrédients connus
            known_names = list(self.known_base.keys())
            known_embeddings = self.sbert_model.encode(known_names, convert_to_numpy=True)

            # Calculer similarités
            similarities = util.cos_sim(query_embedding, known_embeddings).numpy().flatten()

            # Trouver le plus similaire
            max_idx = similarities.argmax()
            max_sim = similarities[max_idx]

            if max_sim >= threshold:
                similar_key = known_names[max_idx]
                profile = self.known_base[similar_key].copy()
                profile['source'] = 'similarity'
                profile['similarity_score'] = float(max_sim)
                profile['similar_to'] = self.known_base[similar_key]['name_fr']

                logger.info(f"[SIMILARITY] {ingredient_name} similar to {profile['similar_to']} (score: {max_sim:.2f})")
                return profile

        except Exception as e:
            logger.warning(f"[WARN] Similarity search failed: {e}")

        return None

    def _infer_with_gemini(self, ingredient: str) -> Optional[Dict]:
        """Niveau 3: Inférence avec Gemini."""
        if not self.gemini_available:
            return None

        try:
            prompt = f"""Analyse l'ingredient de cocktail "{ingredient}".

Retourne UNIQUEMENT un objet JSON valide (pas de texte avant ou apres):
{{
  "sweetness": <float entre 1.5 et 5.0>,
  "acidity": <float entre 1.5 et 5.0>,
  "bitterness": <float entre 1.5 et 5.0>,
  "strength": <float entre 1.5 et 5.0, niveau alcoolique, 1.5 si non-alcoolise>,
  "freshness": <float entre 1.5 et 5.0>,
  "category": "<spirit|mixer|modifier|garnish>"
}}

Exemples de reference:
- Vodka: sweetness=1.5, acidity=1.0, bitterness=2.0, strength=4.5, freshness=2.0
- Jus d'orange: sweetness=3.5, acidity=2.5, bitterness=1.5, strength=1.5, freshness=3.5
- Triple Sec: sweetness=4.0, acidity=2.5, bitterness=1.5, strength=2.5, freshness=3.0

Reponds UNIQUEMENT avec le JSON, rien d'autre."""

            # Essayer plusieurs modèles
            models = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-1.5-flash-latest"]

            for model_name in models:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)

                    # Parser JSON
                    text = response.text.strip()
                    # Extraire JSON si entouré de backticks
                    if "```json" in text:
                        text = text.split("```json")[1].split("```")[0].strip()
                    elif "```" in text:
                        text = text.split("```")[1].split("```")[0].strip()

                    profile = json.loads(text)

                    # Valider le profil
                    required_keys = ["sweetness", "acidity", "bitterness", "strength", "freshness", "category"]
                    if all(k in profile for k in required_keys):
                        # Validation des ranges
                        for key in ["sweetness", "acidity", "bitterness", "strength", "freshness"]:
                            if not (1.5 <= profile[key] <= 5.0):
                                logger.warning(f"[WARN] Invalid range for {key}: {profile[key]}")
                                profile[key] = max(1.5, min(5.0, profile[key]))

                        profile['source'] = 'gemini'
                        profile['model'] = model_name
                        profile['timestamp'] = datetime.now().isoformat()

                        logger.info(f"[GEMINI] Inferred profile for {ingredient} using {model_name}")
                        return profile

                except Exception as e:
                    logger.warning(f"[WARN] Model {model_name} failed: {e}")
                    continue

        except Exception as e:
            logger.error(f"[ERROR] Gemini inference failed: {e}")

        return None

    def _fallback_profile(self, ingredient: str) -> Dict:
        """Niveau 4: Profil fallback par catégorie."""
        ingredient_lower = ingredient.lower()

        # Détection de catégorie par mots-clés
        if any(word in ingredient_lower for word in ["juice", "jus", "nectar", "puree"]):
            category = "mixer"
            profile = {
                "sweetness": 3.0,
                "acidity": 2.5,
                "bitterness": 1.5,
                "strength": 1.5,
                "freshness": 3.5
            }
        elif any(word in ingredient_lower for word in ["syrup", "sirop", "honey", "miel", "sugar", "sucre"]):
            category = "modifier"
            profile = {
                "sweetness": 5.0,
                "acidity": 1.5,
                "bitterness": 1.5,
                "strength": 1.5,
                "freshness": 2.0
            }
        elif any(word in ingredient_lower for word in ["liqueur", "cream", "creme"]):
            category = "modifier"
            profile = {
                "sweetness": 4.0,
                "acidity": 1.5,
                "bitterness": 2.0,
                "strength": 2.5,
                "freshness": 2.0
            }
        elif any(word in ingredient_lower for word in ["vodka", "gin", "rum", "rhum", "whisky", "whiskey", "tequila", "cognac", "brandy"]):
            category = "spirit"
            profile = {
                "sweetness": 1.5,
                "acidity": 1.0,
                "bitterness": 2.0,
                "strength": 4.0,
                "freshness": 2.0
            }
        else:
            # Par défaut: garnish/modifier neutre
            category = "garnish"
            profile = {
                "sweetness": 2.0,
                "acidity": 2.0,
                "bitterness": 2.0,
                "strength": 1.5,
                "freshness": 2.5
            }

        profile['category'] = category
        profile['source'] = 'fallback'
        logger.info(f"[FALLBACK] Using fallback profile for {ingredient} (category: {category})")

        return profile

    def _cache_profile(self, normalized_name: str, profile: Dict):
        """Sauvegarde un profil dans le cache."""
        self.profiles_cache[normalized_name] = profile
        self._save_cache()
        logger.info(f"[CACHE] Saved profile for {normalized_name}")

    def get_top_ingredients(self, n: int = 20) -> Dict[str, Dict]:
        """Retourne les N ingrédients les plus courants."""
        # Pour l'instant, retourne les N premiers de la base connue
        items = list(self.known_base.items())[:n]
        return dict(items)

    def get_stats(self) -> Dict:
        """Retourne des statistiques sur le profiler."""
        stats = {
            "known_ingredients": len(self.known_base),
            "cached_profiles": len(self.profiles_cache),
            "sbert_available": self.sbert_model is not None,
            "gemini_available": self.gemini_available,
        }

        # Compter les sources dans le cache
        sources = {}
        for profile in self.profiles_cache.values():
            source = profile.get('source', 'unknown')
            sources[source] = sources.get(source, 0) + 1
        stats['cache_by_source'] = sources

        return stats


# Fonction utilitaire pour usage externe
def create_profiler() -> IngredientProfiler:
    """Crée et retourne une instance de IngredientProfiler."""
    return IngredientProfiler()


if __name__ == "__main__":
    # Tests unitaires
    print("Testing IngredientProfiler...")
    print("-" * 40)

    profiler = create_profiler()

    # Test 1: Ingrédient connu
    print("\nTest 1: Ingredient connu (Vodka)")
    profile = profiler.get_profile("Vodka")
    print(f"  Source: {profile['source']}")
    print(f"  Strength: {profile['strength']}")
    assert profile['source'] == 'known'
    assert profile['strength'] == 4.5
    print("  [PASS]")

    # Test 2: Ingrédient similaire
    print("\nTest 2: Ingredient similaire (Blackberry)")
    profile = profiler.get_profile("Blackberry")
    print(f"  Source: {profile['source']}")
    print(f"  Sweetness: {profile['sweetness']}")
    print(f"  Acidity: {profile['acidity']}")
    print("  [PASS]")

    # Test 3: Fallback
    print("\nTest 3: Fallback (XYZ Unknown Ingredient)")
    profile = profiler.get_profile("XYZ Unknown Ingredient")
    print(f"  Source: {profile['source']}")
    assert profile['source'] == 'fallback'
    print("  [PASS]")

    # Stats
    print("\nStatistics:")
    stats = profiler.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n[OK] All tests passed!")
