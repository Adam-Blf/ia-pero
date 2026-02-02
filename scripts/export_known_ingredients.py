"""
Export Known Ingredients from generate_data.py to JSON

Ce script extrait les 61 ingrédients hardcodés (SPIRITS, MIXERS, MODIFIERS)
depuis generate_data.py et les exporte vers data/known_ingredients.json
avec toutes les dimensions de profil calculées.
"""

import json
import os
import sys
from pathlib import Path
import re
import unicodedata

# Ajouter le répertoire parent au path pour importer depuis src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.generate_data import SPIRITS, MIXERS, MODIFIERS


def normalize_name(name: str) -> str:
    """Normalise un nom d'ingrédient (minuscules, sans accents, nettoyé)."""
    # Supprimer les accents
    name = ''.join(c for c in unicodedata.normalize('NFD', name)
                   if unicodedata.category(c) != 'Mn')
    # Minuscules et strip
    name = name.lower().strip()
    return name


def create_en_mappings():
    """Crée des mappings EN->FR pour ingrédients courants."""
    return {
        # Spirits
        "vodka": "vodka",
        "gin": "gin",
        "white rum": "rhum blanc",
        "light rum": "rhum blanc",
        "amber rum": "rhum ambre",
        "gold rum": "rhum ambre",
        "dark rum": "rhum brun",
        "tequila": "tequila blanco",
        "silver tequila": "tequila blanco",
        "reposado tequila": "tequila reposado",
        "bourbon": "whisky bourbon",
        "bourbon whiskey": "whisky bourbon",
        "scotch": "whisky scotch",
        "scotch whisky": "whisky scotch",
        "irish whiskey": "whisky irlandais",
        "cognac": "cognac",
        "brandy": "brandy",
        "mezcal": "mezcal",
        "pisco": "pisco",
        "cachaca": "cachaca",

        # Mixers
        "lime juice": "jus de citron vert",
        "lemon juice": "jus de citron jaune",
        "orange juice": "jus d'orange",
        "grapefruit juice": "jus de pamplemousse",
        "pineapple juice": "jus d'ananas",
        "cranberry juice": "jus de cranberry",
        "passion fruit juice": "jus de passion",
        "mango juice": "jus de mangue",
        "tonic water": "tonic water",
        "ginger beer": "ginger beer",
        "ginger ale": "ginger ale",
        "soda water": "soda",
        "club soda": "soda",
        "sparkling water": "eau gazeuse",
        "cola": "cola",
        "coconut milk": "lait de coco",
        "cream of coconut": "creme de coco",
        "tomato juice": "jus de tomate",
        "peach nectar": "nectar de peche",
        "raspberry puree": "puree de framboise",
        "strawberry puree": "puree de fraise",
        "apple juice": "jus de pomme",
        "grape juice": "jus de raisin",
        "rose water": "eau de rose",
        "pomegranate juice": "jus de grenade",
        "lychee nectar": "nectar de litchi",

        # Modifiers
        "triple sec": "triple sec",
        "cointreau": "cointreau",
        "grand marnier": "grand marnier",
        "amaretto": "amaretto",
        "kahlua": "kahlua",
        "coffee liqueur": "kahlua",
        "baileys": "baileys",
        "irish cream": "baileys",
        "chambord": "chambord",
        "raspberry liqueur": "chambord",
        "creme de menthe": "creme de menthe",
        "peppermint liqueur": "creme de menthe",
        "blue curacao": "blue curacao",
        "midori": "midori",
        "melon liqueur": "midori",
        "malibu": "malibu",
        "coconut rum": "malibu",
        "campari": "campari",
        "aperol": "aperol",
        "green chartreuse": "chartreuse verte",
        "chartreuse": "chartreuse verte",
        "benedictine": "benedictine",
        "simple syrup": "sirop simple",
        "sugar syrup": "sirop simple",
        "grenadine": "sirop de grenadine",
        "grenadine syrup": "sirop de grenadine",
        "orgeat": "sirop d'orgeat",
        "almond syrup": "sirop d'orgeat",
        "ginger syrup": "sirop de gingembre",
        "honey": "miel liquide",
        "liquid honey": "miel liquide",
    }


def export_spirits(spirits_list: list) -> dict:
    """Exporte les spiritueux avec profil complet."""
    spirits = {}

    for spirit in spirits_list:
        name_fr = spirit["name"]
        name_key = normalize_name(name_fr)

        # Calculer dimensions manquantes
        # Spirits sont typiquement forts, peu sucrés, peu acides
        profile = {
            "name_fr": name_fr,
            "name_en": None,  # Sera rempli plus tard si besoin
            "strength": spirit["strength"],
            "sweetness": 1.5,  # Spirits peu sucrés par défaut
            "acidity": 1.0,    # Spirits peu acides par défaut
            "bitterness": 2.0,  # Neutre
            "freshness": 2.0,   # Neutre
            "type": spirit["type"],
            "notes": spirit.get("notes", []),
            "category": "spirit"
        }

        # Ajustements selon le type
        if spirit["type"] == "grape":  # Cognac, Brandy
            profile["sweetness"] = 2.0
            profile["bitterness"] = 1.5
        elif spirit["type"] == "sugar_cane":  # Rhum
            profile["sweetness"] = 2.5
            if "ambre" in name_fr.lower() or "brun" in name_fr.lower():
                profile["sweetness"] = 3.0

        spirits[name_key] = profile

    return spirits


def export_mixers(mixers_list: list) -> dict:
    """Exporte les mixers avec profil complet."""
    mixers = {}

    for mixer in mixers_list:
        name_fr = mixer["name"]
        name_key = normalize_name(name_fr)

        # Mixers ont déjà acidity et sweetness
        profile = {
            "name_fr": name_fr,
            "name_en": None,
            "strength": 1.5,  # Non-alcoolisés
            "sweetness": mixer["sweetness"],
            "acidity": mixer["acidity"],
            "bitterness": 1.5,  # Peu amer par défaut
            "freshness": 2.5,   # Plutôt frais
            "type": mixer["type"],
            "category": "mixer"
        }

        # Ajustements selon le type
        if mixer["type"] in ["citrus", "carbonated"]:
            profile["freshness"] = 4.0  # Très frais
        elif mixer["type"] == "berry":
            profile["bitterness"] = 1.8
            profile["freshness"] = 3.5
        elif mixer["type"] == "tropical":
            profile["sweetness"] = min(5.0, profile["sweetness"] + 0.5)
            profile["freshness"] = 3.5
        elif mixer["type"] == "creamy":
            profile["freshness"] = 1.5

        mixers[name_key] = profile

    return mixers


def export_modifiers(modifiers_list: list) -> dict:
    """Exporte les modificateurs avec profil complet."""
    modifiers = {}

    for modifier in modifiers_list:
        name_fr = modifier["name"]
        name_key = normalize_name(name_fr)

        # Modifiers ont sweetness, flavor, type
        profile = {
            "name_fr": name_fr,
            "name_en": None,
            "strength": 2.5,  # Alcool moyen pour liqueurs
            "sweetness": modifier["sweetness"],
            "acidity": 1.5,   # Peu acide par défaut
            "bitterness": 2.0,
            "freshness": 2.0,
            "type": modifier["type"],
            "flavor": modifier.get("flavor", ""),
            "category": "modifier"
        }

        # Ajustements selon le type
        if modifier["type"] == "bitter":
            profile["bitterness"] = 4.5
            profile["sweetness"] = min(3.0, modifier["sweetness"])
        elif modifier["type"] == "syrup":
            profile["strength"] = 1.5  # Non-alcoolisé
            profile["sweetness"] = 5.0
        elif modifier["type"] == "cream":
            profile["strength"] = 2.0
            profile["freshness"] = 1.5
        elif modifier["type"] == "herbal":
            profile["bitterness"] = 3.0
            profile["strength"] = 3.5

        # Ajustements selon la saveur
        if "menthe" in modifier.get("flavor", "").lower():
            profile["freshness"] = 4.5
        elif "orange" in modifier.get("flavor", "").lower():
            profile["acidity"] = 2.5
            profile["freshness"] = 3.0

        modifiers[name_key] = profile

    return modifiers


def add_english_mappings(known_ingredients: dict, en_mappings: dict):
    """Ajoute les mappings EN->FR dans les profils."""
    # Inverser le mapping pour avoir FR->EN
    fr_to_en = {}
    for en_name, fr_name in en_mappings.items():
        fr_key = normalize_name(fr_name)
        if fr_key not in fr_to_en:
            fr_to_en[fr_key] = []
        fr_to_en[fr_key].append(en_name)

    # Ajouter dans les profils
    for category in ["spirits", "mixers", "modifiers"]:
        for key, profile in known_ingredients[category].items():
            if key in fr_to_en:
                profile["name_en"] = fr_to_en[key]


def main():
    """Fonction principale d'export."""
    print("Export des ingredients connus depuis generate_data.py...")

    # Exporter chaque catégorie
    spirits = export_spirits(SPIRITS)
    mixers = export_mixers(MIXERS)
    modifiers = export_modifiers(MODIFIERS)

    print(f"[OK] Exporte {len(spirits)} spiritueux")
    print(f"[OK] Exporte {len(mixers)} mixers")
    print(f"[OK] Exporte {len(modifiers)} modificateurs")
    print(f"Total: {len(spirits) + len(mixers) + len(modifiers)} ingredients")

    # Construire structure finale
    known_ingredients = {
        "spirits": spirits,
        "mixers": mixers,
        "modifiers": modifiers,
        "metadata": {
            "version": "1.0",
            "source": "generate_data.py",
            "total_ingredients": len(spirits) + len(mixers) + len(modifiers),
            "exported_at": "2026-02-02"
        }
    }

    # Ajouter mappings EN->FR
    en_mappings = create_en_mappings()
    add_english_mappings(known_ingredients, en_mappings)
    print(f"[OK] Ajouté {len(en_mappings)} mappings EN->FR")

    # Sauvegarder JSON
    output_path = Path(__file__).parent.parent / "data" / "known_ingredients.json"
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(known_ingredients, f, indent=2, ensure_ascii=False)

    print(f"[SAVE] Sauvegardé: {output_path}")
    print("[DONE] Export terminé avec succès!")

    # Statistiques finales
    print("\n[STATS] Statistiques:")
    print(f"   - Spiritueux: {len(spirits)}")
    print(f"   - Mixers: {len(mixers)}")
    print(f"   - Modificateurs: {len(modifiers)}")
    print(f"   - TOTAL: {len(spirits) + len(mixers) + len(modifiers)} ingrédients")

    # Exemples
    print("\n[EXAMPLES] Exemples de profils exportés:")
    print(f"\n  Vodka: {json.dumps(spirits['vodka'], indent=4, ensure_ascii=False)}")
    print(f"\n  Jus d'orange: {json.dumps(mixers[normalize_name('Jus d orange')], indent=4, ensure_ascii=False)}")


if __name__ == "__main__":
    main()
