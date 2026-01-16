#!/usr/bin/env python3
"""
L'IA Pero - Cocktail Data Generator
Generates 600 unique cocktails with semantic descriptions for RAG system.

Author: Adam Beloucif
"""
from __future__ import annotations

import json
import logging
import random
from pathlib import Path
from typing import TypedDict

import pandas as pd
import numpy as np

# =============================================================================
# CONFIGURATION
# =============================================================================
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "cocktails.csv"
TARGET_COUNT = 600
RANDOM_SEED = 42
MIN_DESCRIPTION_LENGTH = 100

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# =============================================================================
# TYPE DEFINITIONS
# =============================================================================
class TasteProfile(TypedDict):
    Douceur: float
    Acidite: float
    Amertume: float
    Force: float
    Fraicheur: float


class Cocktail(TypedDict):
    name: str
    description_semantique: str
    ingredients: str  # JSON string
    instructions: str
    category: str
    difficulty: str
    prep_time: int
    taste_profile: str  # JSON string


# =============================================================================
# BASE DATA - SPIRITS
# =============================================================================
SPIRITS = [
    {"name": "Vodka", "type": "neutral", "strength": 4.5, "notes": ["neutre", "pur"]},
    {"name": "Gin", "type": "botanical", "strength": 4.0, "notes": ["genievre", "herbes", "agrumes"]},
    {"name": "Rhum blanc", "type": "sugar_cane", "strength": 4.0, "notes": ["canne", "leger", "tropical"]},
    {"name": "Rhum ambre", "type": "sugar_cane", "strength": 4.2, "notes": ["caramel", "vanille", "boise"]},
    {"name": "Rhum brun", "type": "sugar_cane", "strength": 4.5, "notes": ["melasse", "epice", "profond"]},
    {"name": "Tequila blanco", "type": "agave", "strength": 4.0, "notes": ["agave", "poivre", "citrus"]},
    {"name": "Tequila reposado", "type": "agave", "strength": 4.2, "notes": ["agave", "vanille", "boise"]},
    {"name": "Whisky bourbon", "type": "grain", "strength": 4.5, "notes": ["vanille", "caramel", "chene"]},
    {"name": "Whisky scotch", "type": "grain", "strength": 4.5, "notes": ["tourbe", "fume", "malt"]},
    {"name": "Whisky irlandais", "type": "grain", "strength": 4.0, "notes": ["doux", "miel", "cereale"]},
    {"name": "Cognac", "type": "grape", "strength": 4.5, "notes": ["raisin", "chene", "fruit sec"]},
    {"name": "Brandy", "type": "grape", "strength": 4.0, "notes": ["fruit", "chaleureux", "rond"]},
    {"name": "Mezcal", "type": "agave", "strength": 4.5, "notes": ["fume", "terreux", "agave"]},
    {"name": "Pisco", "type": "grape", "strength": 4.0, "notes": ["floral", "muscat", "fruite"]},
    {"name": "Cachaca", "type": "sugar_cane", "strength": 4.0, "notes": ["herbe", "vegetal", "frais"]},
]

# =============================================================================
# BASE DATA - MIXERS
# =============================================================================
MIXERS = [
    {"name": "Jus de citron vert", "type": "citrus", "acidity": 4.5, "sweetness": 1.5},
    {"name": "Jus de citron jaune", "type": "citrus", "acidity": 4.0, "sweetness": 1.5},
    {"name": "Jus d'orange", "type": "citrus", "acidity": 2.5, "sweetness": 3.5},
    {"name": "Jus de pamplemousse", "type": "citrus", "acidity": 3.5, "sweetness": 2.5},
    {"name": "Jus d'ananas", "type": "tropical", "acidity": 2.0, "sweetness": 4.0},
    {"name": "Jus de cranberry", "type": "berry", "acidity": 3.5, "sweetness": 2.5},
    {"name": "Jus de passion", "type": "tropical", "acidity": 3.0, "sweetness": 3.5},
    {"name": "Jus de mangue", "type": "tropical", "acidity": 1.5, "sweetness": 4.5},
    {"name": "Tonic water", "type": "carbonated", "acidity": 1.5, "sweetness": 2.0},
    {"name": "Ginger beer", "type": "carbonated", "acidity": 2.0, "sweetness": 3.0},
    {"name": "Ginger ale", "type": "carbonated", "acidity": 1.5, "sweetness": 3.5},
    {"name": "Soda", "type": "carbonated", "acidity": 1.0, "sweetness": 1.0},
    {"name": "Eau gazeuse", "type": "carbonated", "acidity": 1.0, "sweetness": 1.0},
    {"name": "Cola", "type": "carbonated", "acidity": 2.5, "sweetness": 4.5},
    {"name": "Lait de coco", "type": "creamy", "acidity": 1.0, "sweetness": 2.5},
    {"name": "Creme de coco", "type": "creamy", "acidity": 1.0, "sweetness": 4.0},
    {"name": "Jus de tomate", "type": "savory", "acidity": 3.0, "sweetness": 2.0},
    {"name": "Nectar de peche", "type": "fruit", "acidity": 1.5, "sweetness": 4.0},
    {"name": "Puree de framboise", "type": "berry", "acidity": 2.5, "sweetness": 3.5},
    {"name": "Puree de fraise", "type": "berry", "acidity": 2.0, "sweetness": 4.0},
    {"name": "Jus de pomme", "type": "fruit", "acidity": 2.5, "sweetness": 3.5},
    {"name": "Jus de raisin", "type": "fruit", "acidity": 2.0, "sweetness": 4.0},
    {"name": "Eau de rose", "type": "floral", "acidity": 1.0, "sweetness": 1.5},
    {"name": "Jus de grenade", "type": "fruit", "acidity": 3.0, "sweetness": 3.5},
    {"name": "Nectar de litchi", "type": "tropical", "acidity": 1.5, "sweetness": 4.5},
]

# =============================================================================
# BASE DATA - MODIFIERS (LIQUEURS, SYRUPS)
# =============================================================================
MODIFIERS = [
    {"name": "Triple Sec", "type": "liqueur", "sweetness": 4.0, "flavor": "orange"},
    {"name": "Cointreau", "type": "liqueur", "sweetness": 3.5, "flavor": "orange noble"},
    {"name": "Grand Marnier", "type": "liqueur", "sweetness": 4.0, "flavor": "orange cognac"},
    {"name": "Amaretto", "type": "liqueur", "sweetness": 4.5, "flavor": "amande"},
    {"name": "Kahlua", "type": "liqueur", "sweetness": 4.5, "flavor": "cafe"},
    {"name": "Baileys", "type": "cream", "sweetness": 4.5, "flavor": "creme cafe"},
    {"name": "Chambord", "type": "liqueur", "sweetness": 4.0, "flavor": "framboise"},
    {"name": "Creme de menthe", "type": "liqueur", "sweetness": 4.0, "flavor": "menthe"},
    {"name": "Blue Curacao", "type": "liqueur", "sweetness": 4.0, "flavor": "orange bleue"},
    {"name": "Midori", "type": "liqueur", "sweetness": 4.5, "flavor": "melon"},
    {"name": "Malibu", "type": "liqueur", "sweetness": 4.0, "flavor": "coco"},
    {"name": "Campari", "type": "bitter", "sweetness": 2.0, "flavor": "amer herbes"},
    {"name": "Aperol", "type": "bitter", "sweetness": 3.0, "flavor": "orange amere"},
    {"name": "Chartreuse verte", "type": "herbal", "sweetness": 3.0, "flavor": "herbes complexes"},
    {"name": "Benedictine", "type": "herbal", "sweetness": 3.5, "flavor": "miel herbes"},
    {"name": "Sirop simple", "type": "syrup", "sweetness": 5.0, "flavor": "sucre"},
    {"name": "Sirop de grenadine", "type": "syrup", "sweetness": 5.0, "flavor": "grenade"},
    {"name": "Sirop d'orgeat", "type": "syrup", "sweetness": 4.5, "flavor": "amande fleur"},
    {"name": "Sirop de gingembre", "type": "syrup", "sweetness": 4.0, "flavor": "gingembre"},
    {"name": "Miel liquide", "type": "syrup", "sweetness": 5.0, "flavor": "miel floral"},
]

# =============================================================================
# BASE DATA - GARNISHES
# =============================================================================
GARNISHES = [
    "Rondelle de citron vert",
    "Zeste de citron",
    "Rondelle d'orange",
    "Quartier de pamplemousse",
    "Feuilles de menthe",
    "Branche de romarin",
    "Cerise au marasquin",
    "Olive verte",
    "Tranche d'ananas",
    "Noix de muscade rapee",
    "Baton de cannelle",
    "Lamelle de gingembre",
    "Fleur comestible",
    "Zeste de pamplemousse",
    "Quartier de fraise",
]

# =============================================================================
# BASE DATA - TECHNIQUES
# =============================================================================
TECHNIQUES = [
    {"name": "shake", "desc": "Shaker avec glace et filtrer", "time": 3},
    {"name": "stir", "desc": "Melanger delicatement a la cuillere", "time": 2},
    {"name": "build", "desc": "Construire directement dans le verre", "time": 1},
    {"name": "muddle", "desc": "Piler les ingredients frais", "time": 2},
    {"name": "blend", "desc": "Mixer au blender avec glace", "time": 2},
    {"name": "layer", "desc": "Superposer les couches delicatement", "time": 3},
    {"name": "dry_shake", "desc": "Shaker sans glace puis avec glace", "time": 4},
    {"name": "throw", "desc": "Verser en cascade entre deux verres", "time": 2},
]

# =============================================================================
# BASE DATA - CATEGORIES
# =============================================================================
CATEGORIES = [
    {"name": "Classic", "desc": "cocktails intemporels", "formality": "elegant"},
    {"name": "Tropical", "desc": "saveurs exotiques et fruitees", "formality": "decontracte"},
    {"name": "Tiki", "desc": "escapade polynesienne", "formality": "festif"},
    {"name": "Modern", "desc": "creations contemporaines", "formality": "tendance"},
    {"name": "Digestif", "desc": "fins de repas sophistiques", "formality": "raffine"},
    {"name": "Aperitif", "desc": "ouverture d'appetit", "formality": "convivial"},
    {"name": "Refreshing", "desc": "frais et desalterant", "formality": "decontracte"},
    {"name": "Strong", "desc": "puissant et caractere", "formality": "audacieux"},
]

DIFFICULTIES = ["Facile", "Moyen", "Difficile"]

# =============================================================================
# NAME GENERATION PATTERNS
# =============================================================================
ADJECTIVES = [
    "Golden", "Silver", "Midnight", "Sunset", "Sunrise", "Velvet", "Smoky",
    "Spicy", "Tropical", "Frozen", "Royal", "Secret", "Wild", "Dark", "Bright",
    "Electric", "Mystic", "Sweet", "Bitter", "French", "Cuban", "Italian",
    "Brazilian", "Caribbean", "Pacific", "Atlantic", "Nordic", "Aztec", "Persian",
    "Oriental", "Coastal", "Urban", "Rustic", "Elegant", "Fiery", "Silky",
    "Crisp", "Mellow", "Bold", "Smooth", "Twisted", "Classic", "Modern",
    "Vintage", "Exotic", "Fresh", "Tangy", "Creamy", "Zesty", "Aromatic",
]

NOUNS = [
    "Dream", "Kiss", "Breeze", "Storm", "Wave", "Flame", "Shadow", "Star",
    "Moon", "Sun", "Rose", "Garden", "Paradise", "Heaven", "Oasis", "Mirage",
    "Spirit", "Soul", "Heart", "Mind", "Passion", "Desire", "Temptation",
    "Delight", "Bliss", "Escape", "Journey", "Adventure", "Mystery", "Legend",
    "Tale", "Story", "Night", "Day", "Evening", "Morning", "Twilight", "Dawn",
    "Dusk", "Horizon", "Mist", "Fog", "Rain", "Thunder", "Lightning", "Frost",
    "Bloom", "Petal", "Leaf", "Root", "Vine", "Berry", "Nectar", "Elixir",
]

LOCATIONS = [
    "Havana", "Rio", "Paris", "Tokyo", "Miami", "Manhattan", "Brooklyn",
    "Venice", "Barcelona", "Marrakech", "Bangkok", "Bali", "Fiji", "Jamaica",
    "Bermuda", "Monaco", "Capri", "Santorini", "Ibiza", "Malibu", "Cancun",
    "Acapulco", "Tahiti", "Maui", "Sydney", "Melbourne", "Cape Town", "Mumbai",
    "Shanghai", "Singapore", "Hong Kong", "Dublin", "Edinburgh", "Vienna",
]

# =============================================================================
# DESCRIPTION TEMPLATES
# =============================================================================
DESCRIPTION_TEMPLATES = [
    "Un cocktail {adj1} a base de {spirit}, melange avec {mixer} et rehausse de {modifier}. {taste_desc}. Parfait pour {occasion}.",
    "Ce {category} {adj2} combine harmonieusement {spirit} et {mixer}, avec une touche de {modifier}. {taste_desc}. Ideal pour {context}.",
    "Decouvrez ce cocktail {adj1} ou le {spirit} rencontre le {mixer} dans une danse de saveurs. {modifier} apporte la touche finale. {taste_desc}.",
    "{spirit} forme la base de ce cocktail {adj2}, enrichi par {mixer} et {modifier}. {taste_desc}. Une experience {sensation} a chaque gorgee.",
    "Un melange {adj1} et {adj2} de {spirit} avec {mixer}. Le {modifier} ajoute une dimension {dimension}. {taste_desc}. Recommande pour {occasion}.",
    "Ce cocktail {category} met en valeur le {spirit} accompagne de {mixer} frais. {modifier} apporte {contribution}. {taste_desc}.",
    "Laissez-vous seduire par ce {adj1} cocktail ou {spirit} s'allie au {mixer}. Une pointe de {modifier} revele {revelation}. {taste_desc}.",
    "Creation {adj2} associant {spirit} et {mixer} avec elegance. {modifier} complete ce tableau gustatif. {taste_desc}. Pour {target_audience}.",
    "Le {spirit} prend vie dans ce cocktail {category}, marie au {mixer} et sublime par {modifier}. {taste_desc}. Une {adj1} decouverte.",
    "Un {adj1} voyage sensoriel avec {spirit} comme guide, {mixer} comme compagnon et {modifier} comme destination. {taste_desc}.",
    "Ce cocktail {adj2} revisite les classiques avec {spirit}, {mixer} et {modifier}. {taste_desc}. Une experience {experience_type}.",
    "Harmonie {adj1} entre {spirit} vigoureux et {mixer} delicat. {modifier} ajoute {addition}. {taste_desc}. Pour les amateurs de {preference}.",
    "Le caractere du {spirit} s'exprime pleinement avec {mixer} et {modifier} dans ce cocktail {category}. {taste_desc}. Moment {moment_type}.",
    "Une creation {adj1} ou le {spirit} dialogue avec {mixer}. {modifier} orchestre cette rencontre. {taste_desc}. Emotion {emotion} garantie.",
    "Cocktail {category} {adj2} celebrant {spirit} dans toute sa splendeur. {mixer} et {modifier} completent l'ensemble. {taste_desc}.",
]

TASTE_DESCRIPTORS = [
    "Notes dominantes de {note1} avec une finale {finale}",
    "Equilibre parfait entre {note1} et {note2}",
    "Attaque {attaque} suivie de notes de {note1}",
    "Palette aromatique riche en {note1} et {note2}",
    "Profil gustatif marque par {note1} et une touche de {note2}",
    "Sensation {sensation} avec des accents de {note1}",
    "Bouquet de {note1} evoluant vers {note2}",
    "Complexite gustative revelant {note1} puis {note2}",
]

OCCASIONS = [
    "les soirees d'ete", "les moments de detente", "les celebrations",
    "les aperitifs entre amis", "les diners romantiques", "les fetes",
    "les brunchs du weekend", "les afterworks", "les moments festifs",
    "les retrouvailles", "les occasions speciales", "les soirees elegantes",
]

CONTEXTS = [
    "une soiree entre amis", "un moment de relaxation", "une celebration",
    "un aperitif convivial", "une fin de journee", "une escapade gustative",
    "un instant de plaisir", "une pause rafraichissante", "un voyage sensoriel",
]


# =============================================================================
# GENERATION FUNCTIONS
# =============================================================================
def generate_unique_name(used_names: set[str]) -> str:
    """Generate a unique cocktail name."""
    max_attempts = 100

    for _ in range(max_attempts):
        pattern = random.choice([1, 2, 3, 4, 5])

        if pattern == 1:
            # Adjective + Noun
            name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
        elif pattern == 2:
            # Location + Style
            name = f"{random.choice(LOCATIONS)} {random.choice(['Sour', 'Fizz', 'Punch', 'Cooler', 'Collins', 'Spritz', 'Mule', 'Smash'])}"
        elif pattern == 3:
            # The + Adjective + Noun
            name = f"The {random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
        elif pattern == 4:
            # Location + Adjective
            name = f"{random.choice(LOCATIONS)} {random.choice(ADJECTIVES)}"
        elif pattern == 5:
            # Noun + de + Location
            name = f"{random.choice(NOUNS)} de {random.choice(LOCATIONS)}"

        if name not in used_names:
            return name

    # Fallback with number suffix
    base = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
    counter = 1
    while f"{base} {counter}" in used_names:
        counter += 1
    return f"{base} {counter}"


def generate_ingredients(spirit: dict, mixer: dict, modifier: dict) -> list[str]:
    """Generate a realistic ingredients list."""
    base_amount = random.choice([45, 50, 60])
    mixer_amount = random.choice([30, 45, 60, 90])
    modifier_amount = random.choice([15, 20, 25, 30])

    ingredients = [
        f"{base_amount}ml {spirit['name']}",
        f"{mixer_amount}ml {mixer['name']}",
        f"{modifier_amount}ml {modifier['name']}",
    ]

    # Add garnish
    garnish = random.choice(GARNISHES)
    ingredients.append(garnish)

    # Maybe add ice
    if random.random() > 0.3:
        ingredients.append("Glacons")

    # Maybe add extra ingredient
    if random.random() > 0.6:
        extras = ["Angostura bitters", "Sel de celeri", "Poivre noir", "Sucre de canne", "Eau petillante"]
        ingredients.append(random.choice(extras))

    return ingredients


def generate_instructions(ingredients: list[str], technique: dict) -> str:
    """Generate preparation instructions."""
    steps = []

    if technique["name"] == "muddle":
        steps.append("1. Dans un shaker, piler delicatement les ingredients frais")
        steps.append("2. Ajouter les alcools et la glace")
        steps.append("3. Shaker vigoureusement pendant 10 secondes")
        steps.append("4. Filtrer dans un verre refroidi")
    elif technique["name"] == "shake":
        steps.append("1. Ajouter tous les ingredients dans un shaker avec de la glace")
        steps.append("2. Shaker energiquement pendant 15 secondes")
        steps.append("3. Filtrer dans le verre de service")
    elif technique["name"] == "stir":
        steps.append("1. Placer les ingredients dans un verre a melange avec glace")
        steps.append("2. Remuer delicatement a la cuillere pendant 30 secondes")
        steps.append("3. Filtrer dans un verre refroidi")
    elif technique["name"] == "build":
        steps.append("1. Remplir le verre de glacons")
        steps.append("2. Verser les ingredients directement dans le verre")
        steps.append("3. Melanger doucement")
    elif technique["name"] == "blend":
        steps.append("1. Placer tous les ingredients dans un blender")
        steps.append("2. Ajouter une tasse de glace pilee")
        steps.append("3. Mixer jusqu'a obtenir une consistance lisse")
        steps.append("4. Verser dans un verre hurricane")
    elif technique["name"] == "layer":
        steps.append("1. Verser le premier ingredient au fond du verre")
        steps.append("2. Utiliser le dos d'une cuillere pour superposer chaque couche")
        steps.append("3. Proceder lentement pour preserver les couches distinctes")
    elif technique["name"] == "dry_shake":
        steps.append("1. Shaker tous les ingredients sans glace pendant 10 secondes")
        steps.append("2. Ajouter la glace et shaker a nouveau 15 secondes")
        steps.append("3. Double filtrer dans le verre")
    else:
        steps.append("1. Combiner les ingredients dans le verre")
        steps.append("2. Melanger et servir")

    # Add garnish step
    for ing in ingredients:
        if any(g in ing for g in ["Rondelle", "Zeste", "Feuilles", "Branche", "Cerise", "Tranche"]):
            steps.append(f"5. Garnir avec {ing.lower()}")
            break
    else:
        steps.append("5. Garnir selon votre preference")

    return " ".join(steps)


def generate_taste_profile(spirit: dict, mixer: dict, modifier: dict, category: dict) -> TasteProfile:
    """Generate taste profile values (scale 1.5-5 for frontend compatibility)."""
    # Base values influenced by ingredients
    base_strength = spirit["strength"]
    base_acidity = mixer["acidity"] * 0.8
    base_sweetness = (mixer["sweetness"] + modifier["sweetness"]) / 2

    # Calculate each dimension
    douceur = round(min(5.0, max(1.5, base_sweetness * random.uniform(0.8, 1.2))), 1)
    acidite = round(min(5.0, max(1.5, base_acidity * random.uniform(0.9, 1.1))), 1)
    amertume = round(random.uniform(1.5, 3.5) if modifier["type"] != "bitter" else random.uniform(3.0, 5.0), 1)
    force = round(min(5.0, max(1.5, base_strength * random.uniform(0.85, 1.15))), 1)
    fraicheur = round(random.uniform(2.0, 4.5) if mixer["type"] in ["citrus", "carbonated"] else random.uniform(1.5, 3.5), 1)

    return {
        "Douceur": douceur,
        "Acidite": acidite,
        "Amertume": amertume,
        "Force": force,
        "Fraicheur": fraicheur,
    }


def generate_description_semantique(
    name: str,
    spirit: dict,
    mixer: dict,
    modifier: dict,
    category: dict,
    taste_profile: TasteProfile
) -> str:
    """Generate a rich semantic description for RAG search."""
    template = random.choice(DESCRIPTION_TEMPLATES)
    taste_template = random.choice(TASTE_DESCRIPTORS)

    # Determine taste notes based on ingredients
    all_notes = spirit["notes"] + [mixer["type"], modifier["flavor"]]
    note1 = random.choice(all_notes[:3]) if all_notes else "fruit"
    note2 = random.choice(all_notes[1:]) if len(all_notes) > 1 else "epice"

    # Generate taste description
    taste_desc = taste_template.format(
        note1=note1,
        note2=note2,
        finale=random.choice(["persistante", "fraiche", "douce", "epicee", "veloutee"]),
        attaque=random.choice(["vive", "douce", "franche", "subtile"]),
        sensation=random.choice(["rafraichissante", "chaleureuse", "complexe", "elegante"]),
    )

    # Build description
    adj1 = random.choice(["rafraichissant", "elegant", "audacieux", "sophistique", "convivial", "exotique"])
    adj2 = random.choice(["harmonieux", "equilibre", "subtil", "intense", "delicat", "complexe"])

    description = template.format(
        adj1=adj1,
        adj2=adj2,
        spirit=spirit["name"],
        mixer=mixer["name"],
        modifier=modifier["name"],
        category=category["name"].lower(),
        taste_desc=taste_desc,
        occasion=random.choice(OCCASIONS),
        context=random.choice(CONTEXTS),
        sensation=random.choice(["unique", "memorable", "delicieuse", "exceptionnelle"]),
        dimension=random.choice(["aromatique", "gustative", "olfactive", "sensorielle"]),
        contribution=random.choice(["une profondeur remarquable", "une touche d'originalite", "un equilibre parfait"]),
        revelation=random.choice(["des notes cachees", "une complexite insoupconnee", "des saveurs subtiles"]),
        target_audience=random.choice(["les connaisseurs", "les amateurs de nouveaute", "ceux qui aiment surprendre"]),
        experience_type=random.choice(["inoubliable", "sensorielle", "gustative"]),
        addition=random.choice(["une touche finale", "la note parfaite", "l'accord ideal"]),
        preference=random.choice(["cocktails complexes", "saveurs authentiques", "experiences uniques"]),
        moment_type=random.choice(["de partage", "d'exception", "de decouverte"]),
        emotion=random.choice(["pure", "intense", "subtile"]),
    )

    return description


def validate_cocktail(cocktail: dict) -> bool:
    """
    Validate that a cocktail has all required fields.
    Logs warning if invalid.
    """
    required_fields = [
        "name",
        "description_semantique",
        "ingredients",
        "instructions",
        "category",
        "difficulty",
        "prep_time",
        "taste_profile",
    ]

    for field in required_fields:
        if field not in cocktail:
            print("⚠️ Cocktail incomplet genere, ignore.")
            logger.warning(f"Missing field: {field}")
            return False

        value = cocktail[field]
        if value is None or (isinstance(value, str) and not value.strip()):
            print("⚠️ Cocktail incomplet genere, ignore.")
            logger.warning(f"Empty value for field: {field}")
            return False

    # Validate description length
    desc = cocktail.get("description_semantique", "")
    if len(desc) < MIN_DESCRIPTION_LENGTH:
        print("⚠️ Cocktail incomplet genere, ignore.")
        logger.warning(f"Description too short: {len(desc)} chars (min: {MIN_DESCRIPTION_LENGTH})")
        return False

    return True


def generate_cocktail(index: int, used_names: set[str]) -> Cocktail | None:
    """Generate a single valid cocktail."""
    try:
        # Select random components
        spirit = random.choice(SPIRITS)
        mixer = random.choice(MIXERS)
        modifier = random.choice(MODIFIERS)
        category = random.choice(CATEGORIES)
        technique = random.choice(TECHNIQUES)
        difficulty = random.choice(DIFFICULTIES)

        # Generate name
        name = generate_unique_name(used_names)

        # Generate components
        ingredients = generate_ingredients(spirit, mixer, modifier)
        instructions = generate_instructions(ingredients, technique)
        taste_profile = generate_taste_profile(spirit, mixer, modifier, category)

        # Generate semantic description
        description = generate_description_semantique(
            name, spirit, mixer, modifier, category, taste_profile
        )

        # Calculate prep time
        base_time = technique["time"]
        prep_time = base_time + random.randint(2, 5)

        cocktail: Cocktail = {
            "name": name,
            "description_semantique": description,
            "ingredients": json.dumps(ingredients, ensure_ascii=False),
            "instructions": instructions,
            "category": category["name"],
            "difficulty": difficulty,
            "prep_time": prep_time,
            "taste_profile": json.dumps(taste_profile, ensure_ascii=False),
        }

        if validate_cocktail(cocktail):
            return cocktail
        return None

    except Exception as e:
        print("⚠️ Cocktail incomplet genere, ignore.")
        logger.error(f"Error generating cocktail: {e}")
        return None


# =============================================================================
# DATASET GENERATION & VERIFICATION
# =============================================================================
def generate_dataset(target_count: int = TARGET_COUNT) -> pd.DataFrame:
    """Generate the full cocktail dataset."""
    cocktails: list[Cocktail] = []
    used_names: set[str] = set()
    attempts = 0
    max_attempts = target_count * 2  # Allow some failures

    while len(cocktails) < target_count and attempts < max_attempts:
        attempts += 1
        cocktail = generate_cocktail(len(cocktails), used_names)

        if cocktail:
            used_names.add(cocktail["name"])
            cocktails.append(cocktail)

            if len(cocktails) % 100 == 0:
                logger.info(f"Generated {len(cocktails)}/{target_count} cocktails...")

    logger.info(f"Generation complete: {len(cocktails)} valid cocktails from {attempts} attempts")

    return pd.DataFrame(cocktails)


def verify_dataset(df: pd.DataFrame) -> dict:
    """Verify the integrity of the generated dataset."""
    results = {
        "total_count": len(df),
        "unique_names": df["name"].nunique(),
        "has_duplicates": df["name"].duplicated().any(),
        "null_counts": df.isnull().sum().to_dict(),
        "description_min_length": int(df["description_semantique"].str.len().min()),
        "description_avg_length": round(df["description_semantique"].str.len().mean(), 1),
        "description_max_length": int(df["description_semantique"].str.len().max()),
        "categories_distribution": df["category"].value_counts().to_dict(),
        "difficulty_distribution": df["difficulty"].value_counts().to_dict(),
        "prep_time_stats": {
            "min": int(df["prep_time"].min()),
            "max": int(df["prep_time"].max()),
            "mean": round(df["prep_time"].mean(), 1),
        },
        "valid": True,
        "errors": [],
    }

    # Validations
    if results["total_count"] < TARGET_COUNT:
        results["valid"] = False
        results["errors"].append(f"Only {results['total_count']} cocktails generated (target: {TARGET_COUNT})")

    if results["has_duplicates"]:
        results["valid"] = False
        results["errors"].append("Duplicate cocktail names detected")

    if results["description_min_length"] < MIN_DESCRIPTION_LENGTH:
        results["valid"] = False
        results["errors"].append(f"Some descriptions too short (min: {results['description_min_length']})")

    return results


# =============================================================================
# MAIN
# =============================================================================
def main() -> None:
    """Main entry point."""
    logger.info(f"Starting generation of {TARGET_COUNT} cocktails...")
    logger.info(f"Output path: {OUTPUT_PATH}")

    # Set seed for reproducibility
    random.seed(RANDOM_SEED)
    np.random.seed(RANDOM_SEED)

    # Generate dataset
    df = generate_dataset(TARGET_COUNT)

    # Verify
    verification = verify_dataset(df)

    if not verification["valid"]:
        logger.error(f"Dataset validation failed!")
        for error in verification["errors"]:
            logger.error(f"  - {error}")
        return

    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Export to CSV
    df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")

    logger.info(f"Dataset exported to {OUTPUT_PATH}")
    logger.info(f"Total cocktails: {verification['total_count']}")
    logger.info(f"Unique names: {verification['unique_names']}")
    logger.info(f"Description length: {verification['description_min_length']}-{verification['description_max_length']} chars (avg: {verification['description_avg_length']})")
    logger.info(f"Categories: {verification['categories_distribution']}")
    logger.info(f"Difficulties: {verification['difficulty_distribution']}")
    logger.info(f"Prep time: {verification['prep_time_stats']['min']}-{verification['prep_time_stats']['max']} min (avg: {verification['prep_time_stats']['mean']})")


if __name__ == "__main__":
    main()
