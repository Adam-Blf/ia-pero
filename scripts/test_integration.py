"""
Test d'Intégration Complète

Vérifie que le système d'intégration Kaggle fonctionne correctement.
"""

import sys
import json
from pathlib import Path
import pandas as pd

# Ajouter src/ au path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_known_ingredients():
    """Test 1: Vérifier que la base de connaissance existe."""
    print("\n[TEST 1] Base de connaissance...")

    path = Path(__file__).parent.parent / "data" / "known_ingredients.json"
    assert path.exists(), f"Fichier manquant: {path}"

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert "spirits" in data
    assert "mixers" in data
    assert "modifiers" in data

    total = len(data["spirits"]) + len(data["mixers"]) + len(data["modifiers"])
    print(f"  [OK] {total} ingredients dans la base")
    print(f"    - Spiritueux: {len(data['spirits'])}")
    print(f"    - Mixers: {len(data['mixers'])}")
    print(f"    - Modificateurs: {len(data['modifiers'])}")

    return True


def test_ingredient_profiler():
    """Test 2: Vérifier que le profiler fonctionne."""
    print("\n[TEST 2] IngredientProfiler...")

    from ingredient_profiler import IngredientProfiler

    profiler = IngredientProfiler()

    # Test ingrédient connu
    profile = profiler.get_profile("Vodka")
    assert profile['source'] == 'known'
    assert profile['strength'] == 4.5
    print(f"  [OK] Profil connu: Vodka (strength={profile['strength']})")

    # Test fallback
    profile = profiler.get_profile("Unknown Ingredient")
    assert profile['source'] == 'fallback'
    print(f"  [OK] Fallback: Unknown Ingredient (category={profile['category']})")

    # Stats
    stats = profiler.get_stats()
    print(f"  [OK] Stats: {stats['known_ingredients']} ingredients connus")

    return True


def test_kaggle_dataset():
    """Test 3: Vérifier que le dataset Kaggle enrichi existe."""
    print("\n[TEST 3] Dataset Kaggle enrichi...")

    path = Path(__file__).parent.parent / "data" / "kaggle_cocktails_enriched.csv"
    assert path.exists(), f"Fichier manquant: {path}"

    df = pd.read_csv(path)

    # Vérifier colonnes
    required_cols = ['name', 'description_semantique', 'ingredients',
                     'instructions', 'category', 'difficulty', 'prep_time', 'taste_profile']
    for col in required_cols:
        assert col in df.columns, f"Colonne manquante: {col}"

    print(f"  [OK] {len(df)} cocktails enrichis")
    print(f"  [OK] Toutes les colonnes présentes")

    # Vérifier un profil
    profile = json.loads(df.iloc[0]['taste_profile'])
    required_keys = ['Douceur', 'Acidite', 'Amertume', 'Force', 'Fraicheur']
    for key in required_keys:
        assert key in profile, f"Clé manquante: {key}"
        assert 1.5 <= profile[key] <= 5.0, f"Valeur hors range: {key}={profile[key]}"

    print(f"  [OK] Profils valides (exemple: {df.iloc[0]['name']})")
    print(f"    Douceur={profile['Douceur']}, Acidite={profile['Acidite']}, Force={profile['Force']}")

    return True


def test_app_integration():
    """Test 4: Vérifier que l'app peut charger les deux datasets."""
    print("\n[TEST 4] Intégration dans l'app...")

    # Import depuis app.py
    from app import load_cocktails_csv

    df = load_cocktails_csv()

    # Vérifier que les deux sources sont présentes
    assert 'source' in df.columns, "Colonne 'source' manquante"

    sources = df['source'].value_counts()
    print(f"  [OK] Dataset fusionné: {len(df)} cocktails total")

    if 'generated' in sources:
        print(f"    - Générés: {sources['generated']}")
    if 'kaggle' in sources:
        print(f"    - Kaggle: {sources['kaggle']}")

    # Vérifier qu'il y a au moins des cocktails Kaggle
    assert 'kaggle' in sources.index, "Aucun cocktail Kaggle trouvé"

    return True


def test_search_with_filter():
    """Test 5: Vérifier que la recherche avec filtre fonctionne."""
    print("\n[TEST 5] Recherche avec filtre source...")

    from app import search_cocktails_sbert

    # Test sans filtre
    results_all = search_cocktails_sbert("Margarita", top_k=10, source_filter="Tous")
    print(f"  [OK] Recherche sans filtre: {len(results_all)} résultats")

    # Test avec filtre Kaggle
    results_kaggle = search_cocktails_sbert("Margarita", top_k=10, source_filter="Base Kaggle")
    print(f"  [OK] Recherche filtrée (Kaggle): {len(results_kaggle)} résultats")

    # Vérifier que tous les résultats filtrés sont bien Kaggle
    for result in results_kaggle:
        if 'source' in result:
            assert result['source'] == 'kaggle', f"Résultat non filtré: {result['name']}"

    return True


def main():
    """Exécute tous les tests."""
    print("="*60)
    print(" TEST D'INTEGRATION COMPLETE - SYSTEME KAGGLE")
    print("="*60)

    tests = [
        test_known_ingredients,
        test_ingredient_profiler,
        test_kaggle_dataset,
        test_app_integration,
        test_search_with_filter,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"  [FAIL] ECHEC: {e}")
            failed += 1
        except Exception as e:
            print(f"  [FAIL] ERREUR: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f" RESULTATS: {passed}/{len(tests)} tests passés")
    if failed > 0:
        print(f" ATTENTION: {failed} tests échoués")
    else:
        print(" [OK] TOUS LES TESTS PASSES!")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
