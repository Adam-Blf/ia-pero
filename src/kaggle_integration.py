"""
Kaggle Integration - Parser et Nettoyeur de Dataset

Ce module parse le dataset Kaggle cocktails et le nettoie
pour être compatible avec le format de l'application.

Dataset Kaggle: https://www.kaggle.com/datasets/aadyasingh55/cocktails
Colonnes attendues: id, name, alcoholic, category, glassType, instructions,
                    drinkThumbnail, ingredients, ingredientMeasures
"""

import pandas as pd
import json
import re
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class KaggleDatasetParser:
    """Parser pour le dataset Kaggle cocktails."""

    # Mapping EN->FR pour catégories
    CATEGORY_MAPPING = {
        "Ordinary Drink": "Classic",
        "Cocktail": "Classic",
        "Shot": "Digestif",
        "Shake": "Tropical",
        "Coffee / Tea": "Digestif",
        "Homemade Liqueur": "Modern",
        "Punch / Party Drink": "Tiki",
        "Beer": "Classic",
        "Soft Drink": "Sans alcool",
    }

    # Mapping EN->FR pour ingrédients courants
    INGREDIENT_MAPPING = {
        "vodka": "Vodka",
        "gin": "Gin",
        "white rum": "Rhum blanc",
        "light rum": "Rhum blanc",
        "dark rum": "Rhum brun",
        "amber rum": "Rhum ambre",
        "gold rum": "Rhum ambre",
        "tequila": "Tequila blanco",
        "silver tequila": "Tequila blanco",
        "bourbon": "Whisky bourbon",
        "bourbon whiskey": "Whisky bourbon",
        "scotch": "Whisky scotch",
        "scotch whisky": "Whisky scotch",
        "irish whiskey": "Whisky irlandais",
        "cognac": "Cognac",
        "brandy": "Brandy",

        "lime juice": "Jus de citron vert",
        "lemon juice": "Jus de citron jaune",
        "orange juice": "Jus d'orange",
        "grapefruit juice": "Jus de pamplemousse",
        "pineapple juice": "Jus d'ananas",
        "cranberry juice": "Jus de cranberry",
        "apple juice": "Jus de pomme",
        "tomato juice": "Jus de tomate",

        "triple sec": "Triple Sec",
        "cointreau": "Cointreau",
        "grand marnier": "Grand Marnier",
        "campari": "Campari",
        "aperol": "Aperol",
        "amaretto": "Amaretto",
        "kahlua": "Kahlua",
        "coffee liqueur": "Kahlua",
        "baileys": "Baileys",
        "irish cream": "Baileys",

        "simple syrup": "Sirop simple",
        "sugar syrup": "Sirop simple",
        "grenadine": "Sirop de grenadine",
        "grenadine syrup": "Sirop de grenadine",

        "tonic water": "Tonic water",
        "ginger beer": "Ginger beer",
        "ginger ale": "Ginger ale",
        "soda water": "Soda",
        "club soda": "Soda",
        "cola": "Cola",
        "sprite": "Soda",

        "lime": "Citron vert",
        "lemon": "Citron jaune",
        "orange": "Orange",
        "mint": "Menthe",
        "sugar": "Sucre",
        "salt": "Sel",
        "ice": "Glace",
    }

    def __init__(self, csv_path: str):
        """
        Initialise le parser.

        Args:
            csv_path: Chemin vers le CSV Kaggle (data/kaggle_raw.csv)
        """
        self.csv_path = Path(csv_path)
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Kaggle CSV not found: {csv_path}")

        self.df = None
        logger.info(f"[OK] KaggleDatasetParser initialized with {csv_path}")

    def load(self) -> pd.DataFrame:
        """Charge le CSV Kaggle."""
        self.df = pd.read_csv(self.csv_path)
        logger.info(f"[OK] Loaded {len(self.df)} cocktails from Kaggle dataset")
        return self.df

    def parse_ingredients_column(self, ingredients_str: str) -> List[str]:
        """
        Parse la colonne 'ingredients' (peut être JSON, CSV, ou autre).

        Args:
            ingredients_str: String contenant les ingrédients

        Returns:
            Liste d'ingrédients nettoyés
        """
        if pd.isna(ingredients_str):
            return []

        ingredients = []

        try:
            # Essayer JSON
            if ingredients_str.startswith('[') or ingredients_str.startswith('{'):
                parsed = json.loads(ingredients_str)
                if isinstance(parsed, list):
                    ingredients = [str(item).strip() for item in parsed if item]
                elif isinstance(parsed, dict):
                    ingredients = [str(v).strip() for v in parsed.values() if v]
            else:
                # Sinon, split par virgule
                ingredients = [ing.strip() for ing in ingredients_str.split(',') if ing.strip()]

        except Exception as e:
            logger.warning(f"[WARN] Failed to parse ingredients: {e}")
            # Fallback: split par virgule
            ingredients = [ing.strip() for ing in str(ingredients_str).split(',') if ing.strip()]

        # Filtrer valeurs vides et "null"
        ingredients = [ing for ing in ingredients if ing and ing.lower() != 'null' and ing.lower() != 'none']

        return ingredients

    def parse_measures_column(self, measures_str: str) -> List[str]:
        """Parse la colonne 'ingredientMeasures'."""
        return self.parse_ingredients_column(measures_str)

    def translate_ingredient(self, ingredient: str) -> str:
        """
        Traduit un ingrédient EN vers FR si possible.

        Args:
            ingredient: Nom de l'ingrédient en anglais

        Returns:
            Nom traduit ou original
        """
        ing_lower = ingredient.lower().strip()

        # Recherche directe
        if ing_lower in self.INGREDIENT_MAPPING:
            return self.INGREDIENT_MAPPING[ing_lower]

        # Recherche partielle (ex: "fresh lime juice" -> "lime juice")
        for en_key, fr_value in self.INGREDIENT_MAPPING.items():
            if en_key in ing_lower:
                return fr_value

        # Retourner original capitalisé
        return ingredient.strip().capitalize()

    def extract_ingredient_name(self, ingredient_text: str) -> str:
        """
        Extrait le nom de l'ingrédient sans la quantité.

        Args:
            ingredient_text: Ex: "60ml Vodka" ou "Vodka"

        Returns:
            Nom de l'ingrédient: "Vodka"
        """
        # Supprimer les quantités (ex: "60ml", "1 oz", "1/2 cup")
        text = re.sub(r'^\d+(\.\d+)?\s*(ml|oz|cl|cup|tsp|tbsp|dash|splash)?\s*', '', ingredient_text, flags=re.IGNORECASE)
        text = re.sub(r'^\d+/\d+\s*(ml|oz|cl|cup|tsp|tbsp)?\s*', '', text, flags=re.IGNORECASE)

        # Strip et retour
        return text.strip()

    def format_ingredient_with_measure(self, ingredient: str, measure: str) -> str:
        """
        Formate un ingrédient avec sa mesure.

        Args:
            ingredient: Nom de l'ingrédient
            measure: Quantité

        Returns:
            String formaté: "60ml Vodka"
        """
        if not measure or measure.lower() in ['null', 'none', '']:
            return ingredient

        # Nettoyer la mesure
        measure = measure.strip()

        # Si la mesure ne contient pas d'unité, ajouter "ml" par défaut
        if re.match(r'^\d+(\.\d+)?$', measure):
            measure = f"{measure}ml"

        return f"{measure} {ingredient}"

    def map_category(self, category: str) -> str:
        """Mappe une catégorie EN vers FR."""
        if pd.isna(category):
            return "Classic"

        return self.CATEGORY_MAPPING.get(category, "Modern")

    def clean_and_parse(self) -> pd.DataFrame:
        """
        Nettoie et parse le dataset Kaggle.

        Returns:
            DataFrame nettoyé avec colonnes standardisées
        """
        if self.df is None:
            raise ValueError("Dataset not loaded. Call load() first.")

        logger.info("[PROCESS] Cleaning and parsing Kaggle dataset...")

        cleaned_rows = []

        for idx, row in self.df.iterrows():
            try:
                # Parser ingrédients et mesures
                ingredients_raw = self.parse_ingredients_column(row.get('ingredients', ''))
                measures_raw = self.parse_measures_column(row.get('ingredientMeasures', ''))

                # Aligner mesures avec ingrédients
                if len(measures_raw) < len(ingredients_raw):
                    measures_raw.extend([''] * (len(ingredients_raw) - len(measures_raw)))

                # Traduire et formater ingrédients
                ingredients_formatted = []
                ingredients_names = []

                for ing, measure in zip(ingredients_raw, measures_raw):
                    # Extraire nom sans quantité
                    ing_name = self.extract_ingredient_name(ing)
                    if not ing_name:
                        continue

                    # Traduire
                    ing_translated = self.translate_ingredient(ing_name)

                    # Formater avec mesure
                    ing_formatted = self.format_ingredient_with_measure(ing_translated, measure)

                    ingredients_formatted.append(ing_formatted)
                    ingredients_names.append(ing_translated)

                # Filtrer cocktails sans ingrédients
                if not ingredients_formatted:
                    logger.debug(f"[SKIP] No ingredients for {row.get('name', 'unknown')}")
                    continue

                # Construire row nettoyée
                cleaned_row = {
                    'name': row.get('name', 'Unknown Cocktail').strip(),
                    'ingredients': json.dumps(ingredients_formatted, ensure_ascii=False),
                    'instructions': row.get('instructions', 'Mix ingredients and serve.').strip(),
                    'category': self.map_category(row.get('category', '')),
                    'alcoholic': row.get('alcoholic', 'Alcoholic'),
                    'glassType': row.get('glassType', 'Highball glass'),
                    'drinkThumbnail': row.get('drinkThumbnail', ''),

                    # Informations pour traitement ultérieur
                    '_ingredients_names': ingredients_names,
                }

                cleaned_rows.append(cleaned_row)

            except Exception as e:
                logger.warning(f"[ERROR] Failed to parse row {idx}: {e}")
                continue

        cleaned_df = pd.DataFrame(cleaned_rows)

        logger.info(f"[OK] Cleaned {len(cleaned_df)} cocktails (filtered {len(self.df) - len(cleaned_df)} invalid)")

        return cleaned_df

    def deduplicate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Déduplique les cocktails par nom."""
        initial_count = len(df)
        df_dedup = df.drop_duplicates(subset=['name'], keep='first')
        removed = initial_count - len(df_dedup)

        if removed > 0:
            logger.info(f"[DEDUP] Removed {removed} duplicate cocktails")

        return df_dedup

    def extract_unique_ingredients(self, df: pd.DataFrame) -> set:
        """
        Extrait tous les ingrédients uniques du dataset.

        Args:
            df: DataFrame nettoyé

        Returns:
            Set d'ingrédients uniques
        """
        all_ingredients = set()

        for ingredients_names in df['_ingredients_names']:
            all_ingredients.update(ingredients_names)

        logger.info(f"[OK] Extracted {len(all_ingredients)} unique ingredients")

        return all_ingredients


def parse_kaggle_dataset(csv_path: str) -> Tuple[pd.DataFrame, set]:
    """
    Fonction utilitaire pour parser le dataset Kaggle.

    Args:
        csv_path: Chemin vers kaggle_raw.csv

    Returns:
        Tuple (DataFrame nettoyé, Set d'ingrédients uniques)
    """
    parser = KaggleDatasetParser(csv_path)
    parser.load()
    cleaned_df = parser.clean_and_parse()
    cleaned_df = parser.deduplicate(cleaned_df)
    unique_ingredients = parser.extract_unique_ingredients(cleaned_df)

    return cleaned_df, unique_ingredients


if __name__ == "__main__":
    # Test du module
    print("Testing KaggleDatasetParser...")
    print("-" * 40)

    # Créer une instance sans vérifier le fichier (pour tests unitaires)
    class TestParser(KaggleDatasetParser):
        def __init__(self):
            self.csv_path = Path("dummy.csv")
            self.df = None

    parser = TestParser()

    # Test 1: Parse JSON list
    ing_str = '["Vodka", "Lime juice", "Sugar syrup"]'
    ingredients = parser.parse_ingredients_column(ing_str)
    print(f"Test 1: {ingredients}")
    assert len(ingredients) == 3

    # Test 2: Translate ingredient
    translated = parser.translate_ingredient("lime juice")
    print(f"Test 2: lime juice -> {translated}")
    assert translated == "Jus de citron vert"

    # Test 3: Extract name
    name = parser.extract_ingredient_name("60ml Vodka")
    print(f"Test 3: 60ml Vodka -> {name}")
    assert name == "Vodka"

    # Test 4: Format with measure
    formatted = parser.format_ingredient_with_measure("Vodka", "60ml")
    print(f"Test 4: {formatted}")
    assert formatted == "60ml Vodka"

    print("\n[OK] All tests passed!")
