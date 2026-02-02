"""
Enrich Kaggle Dataset - Pipeline Orchestrateur

Ce script orchestre l'enrichissement complet du dataset Kaggle:
1. Charge et parse le dataset Kaggle
2. Extrait les ingrédients uniques
3. Obtient les profils via IngredientProfiler (système 4 niveaux)
4. Calcule les profils de saveurs pour chaque cocktail
5. Ajoute colonnes manquantes (description_semantique, difficulty, prep_time)
6. Sauvegarde le dataset enrichi

Usage:
    python scripts/enrich_kaggle.py

Pré-requis:
    - data/kaggle_raw.csv doit exister (téléchargé depuis Kaggle)
    - data/known_ingredients.json doit exister (généré par export_known_ingredients.py)
"""

import sys
import json
import re
from pathlib import Path
from typing import List, Dict
import pandas as pd
import logging

# Ajouter src/ au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingredient_profiler import IngredientProfiler
from kaggle_integration import parse_kaggle_dataset

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def parse_ingredient_text(ingredient_text: str) -> tuple[float, str]:
    """
    Parse un ingrédient avec quantité.

    Args:
        ingredient_text: Ex: "60ml Vodka"

    Returns:
        Tuple (quantity_ml, ingredient_name)
    """
    # Extraire quantité
    quantity = 1.0  # Défaut

    # Patterns pour quantités
    patterns = [
        (r'^(\d+(?:\.\d+)?)\s*ml', 1.0),      # 60ml
        (r'^(\d+(?:\.\d+)?)\s*cl', 10.0),     # 6cl = 60ml
        (r'^(\d+(?:\.\d+)?)\s*oz', 30.0),     # 2oz ≈ 60ml
        (r'^(\d+)/(\d+)\s*oz', 30.0),         # 1/2oz ≈ 15ml
        (r'^(\d+(?:\.\d+)?)\s*cup', 240.0),   # 1 cup ≈ 240ml
        (r'^(\d+(?:\.\d+)?)\s*tsp', 5.0),     # 1 tsp ≈ 5ml
        (r'^(\d+(?:\.\d+)?)\s*tbsp', 15.0),   # 1 tbsp ≈ 15ml
    ]

    for pattern, multiplier in patterns:
        match = re.search(pattern, ingredient_text, re.IGNORECASE)
        if match:
            if '/' in pattern:
                # Fraction
                num, denom = match.groups()
                quantity = (float(num) / float(denom)) * multiplier
            else:
                quantity = float(match.group(1)) * multiplier
            break

    # Extraire nom de l'ingrédient
    name = re.sub(r'^\d+(\.\d+)?\s*(ml|oz|cl|cup|tsp|tbsp|dash|splash)?\s*', '', ingredient_text, flags=re.IGNORECASE)
    name = re.sub(r'^\d+/\d+\s*(ml|oz|cl|cup|tsp|tbsp)?\s*', '', name, flags=re.IGNORECASE)
    name = name.strip()

    return quantity, name


def compute_cocktail_profile(ingredients_list: List[str], profiler: IngredientProfiler) -> Dict:
    """
    Calcule le profil de saveurs d'un cocktail par moyenne pondérée.

    Args:
        ingredients_list: Liste d'ingrédients (ex: ["60ml Vodka", "30ml Jus d'orange"])
        profiler: Instance de IngredientProfiler

    Returns:
        dict: Profil {Douceur, Acidite, Amertume, Force, Fraicheur}
    """
    if not ingredients_list:
        # Profil par défaut si pas d'ingrédients
        return {
            "Douceur": 2.5,
            "Acidite": 2.5,
            "Amertume": 2.5,
            "Force": 2.5,
            "Fraicheur": 2.5
        }

    profiles = []
    weights = []

    for ing_text in ingredients_list:
        try:
            quantity, name = parse_ingredient_text(ing_text)
            profile = profiler.get_profile(name)

            profiles.append(profile)
            weights.append(quantity)

        except Exception as e:
            logger.warning(f"[WARN] Failed to parse ingredient {ing_text}: {e}")
            continue

    if not profiles:
        # Fallback si aucun profil obtenu
        return {
            "Douceur": 2.5,
            "Acidite": 2.5,
            "Amertume": 2.5,
            "Force": 2.5,
            "Fraicheur": 2.5
        }

    # Normaliser poids
    total_weight = sum(weights)
    if total_weight == 0:
        weights = [1.0] * len(weights)
        total_weight = len(weights)

    normalized_weights = [w / total_weight for w in weights]

    # Calculer moyennes pondérées
    profile = {
        "Douceur": round(sum(p['sweetness'] * w for p, w in zip(profiles, normalized_weights)), 1),
        "Acidite": round(sum(p['acidity'] * w for p, w in zip(profiles, normalized_weights)), 1),
        "Amertume": round(sum(p['bitterness'] * w for p, w in zip(profiles, normalized_weights)), 1),
        "Force": round(sum(p['strength'] * w for p, w in zip(profiles, normalized_weights)), 1),
        "Fraicheur": round(sum(p['freshness'] * w for p, w in zip(profiles, normalized_weights)), 1),
    }

    # Validation ranges
    for key in profile:
        profile[key] = max(1.5, min(5.0, profile[key]))

    return profile


def generate_semantic_desc(row: Dict) -> str:
    """
    Génère une description sémantique riche pour SBERT.

    Args:
        row: Ligne du DataFrame

    Returns:
        str: Description riche
    """
    name = row.get('name', 'Cocktail')
    category = row.get('category', 'Classic')
    alcoholic = row.get('alcoholic', 'Alcoholic')
    instructions = row.get('instructions', '')[:100]

    # Parser ingrédients
    try:
        ingredients = json.loads(row.get('ingredients', '[]'))
        ing_names = [parse_ingredient_text(ing)[1] for ing in ingredients[:3]]
        ing_str = ', '.join(ing_names)
    except:
        ing_str = "ingredients varies"

    desc = f"{name} est un cocktail {category} {'alcoolise' if alcoholic == 'Alcoholic' else 'sans alcool'}. Ingredients principaux: {ing_str}. {instructions}"

    return desc


def infer_difficulty(ingredients_list: List[str]) -> str:
    """
    Estime la difficulté selon le nombre d'ingrédients.

    Args:
        ingredients_list: Liste d'ingrédients

    Returns:
        str: "Facile", "Moyen", ou "Difficile"
    """
    count = len(ingredients_list)

    if count <= 3:
        return "Facile"
    elif count <= 6:
        return "Moyen"
    else:
        return "Difficile"


def estimate_prep_time(instructions: str) -> int:
    """
    Estime le temps de préparation selon la longueur des instructions.

    Args:
        instructions: Instructions de préparation

    Returns:
        int: Temps estimé en minutes
    """
    if not instructions:
        return 3

    length = len(instructions)

    if length < 100:
        return 3
    elif length < 200:
        return 4
    elif length < 300:
        return 5
    else:
        return 6


def main():
    """Pipeline principal d'enrichissement."""
    logger.info("="*60)
    logger.info(" Enrichissement Dataset Kaggle Cocktails")
    logger.info("="*60)

    # Chemins
    project_root = Path(__file__).parent.parent
    kaggle_raw_path = project_root / "data" / "kaggle_raw.csv"
    output_path = project_root / "data" / "kaggle_cocktails_enriched.csv"

    # Vérifications
    if not kaggle_raw_path.exists():
        logger.error(f"[ERROR] Dataset Kaggle introuvable: {kaggle_raw_path}")
        logger.error("Telechargez le dataset depuis: https://www.kaggle.com/datasets/aadyasingh55/cocktails")
        logger.error("Et placez-le dans: data/kaggle_raw.csv")
        return

    # Étape 1: Parser dataset Kaggle
    logger.info("\n[STEP 1] Parsing Kaggle dataset...")
    try:
        kaggle_df, unique_ingredients = parse_kaggle_dataset(str(kaggle_raw_path))
        logger.info(f"[OK] Parse {len(kaggle_df)} cocktails")
        logger.info(f"[OK] Trouve {len(unique_ingredients)} ingredients uniques")
    except Exception as e:
        logger.error(f"[ERROR] Failed to parse Kaggle dataset: {e}")
        return

    # Étape 2: Initialiser profiler
    logger.info("\n[STEP 2] Initializing IngredientProfiler...")
    try:
        profiler = IngredientProfiler()
        logger.info("[OK] Profiler initialized")
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize profiler: {e}")
        return

    # Étape 3: Obtenir profils pour tous les ingrédients uniques
    logger.info("\n[STEP 3] Inferring ingredient profiles...")
    api_calls = 0
    similarity_hits = 0
    known_hits = 0
    fallback_hits = 0

    for idx, ingredient in enumerate(unique_ingredients, 1):
        profile = profiler.get_profile(ingredient)
        source = profile.get('source', 'unknown')

        if source == 'gemini':
            api_calls += 1
        elif source == 'similarity':
            similarity_hits += 1
        elif source == 'known':
            known_hits += 1
        elif source == 'fallback':
            fallback_hits += 1

        # Afficher progression tous les 10 ingrédients
        if idx % 10 == 0:
            logger.info(f"  Progress: {idx}/{len(unique_ingredients)} ingredients processed...")

    logger.info(f"\n[STATS] Profiling statistics:")
    logger.info(f"  - Known base: {known_hits}")
    logger.info(f"  - Similarity: {similarity_hits}")
    logger.info(f"  - Gemini API: {api_calls}")
    logger.info(f"  - Fallback: {fallback_hits}")

    # Étape 4: Calculer profils de cocktails
    logger.info("\n[STEP 4] Computing cocktail taste profiles...")

    enriched_rows = []

    for idx, row in kaggle_df.iterrows():
        try:
            # Parser ingrédients
            ingredients_list = json.loads(row['ingredients'])

            # Calculer profil
            taste_profile = compute_cocktail_profile(ingredients_list, profiler)

            # Générer colonnes manquantes
            description_semantique = generate_semantic_desc(row)
            difficulty = infer_difficulty(ingredients_list)
            prep_time = estimate_prep_time(row['instructions'])

            # Construire row enrichie
            enriched_row = {
                'name': row['name'],
                'description_semantique': description_semantique,
                'ingredients': row['ingredients'],
                'instructions': row['instructions'],
                'category': row['category'],
                'difficulty': difficulty,
                'prep_time': prep_time,
                'taste_profile': json.dumps(taste_profile, ensure_ascii=False),
            }

            enriched_rows.append(enriched_row)

            # Progression
            if (idx + 1) % 50 == 0:
                logger.info(f"  Progress: {idx + 1}/{len(kaggle_df)} cocktails enriched...")

        except Exception as e:
            logger.warning(f"[WARN] Failed to enrich cocktail {row.get('name', 'unknown')}: {e}")
            continue

    enriched_df = pd.DataFrame(enriched_rows)
    logger.info(f"[OK] Enriched {len(enriched_df)} cocktails")

    # Étape 5: Sauvegarder
    logger.info("\n[STEP 5] Saving enriched dataset...")
    enriched_df.to_csv(output_path, index=False)
    logger.info(f"[OK] Saved: {output_path}")

    # Résumé final
    logger.info("\n" + "="*60)
    logger.info(" ENRICHISSEMENT TERMINE")
    logger.info("="*60)
    logger.info(f"Cocktails enrichis: {len(enriched_df)}")
    logger.info(f"Ingredients profiles: {len(unique_ingredients)}")
    logger.info(f"Appels API Gemini: {api_calls}")
    logger.info(f"Fichier de sortie: {output_path}")
    logger.info("\nProchaine etape: Modifiez app.py pour fusionner les datasets")
    logger.info("="*60)


if __name__ == "__main__":
    main()
