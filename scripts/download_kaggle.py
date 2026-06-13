"""
Download Kaggle Cocktails Dataset

Ce script télécharge le dataset Kaggle cocktails.
Il est gaté derrière `has_kaggle_credentials()` pour ne jamais échouer
silencieusement quand les credentials sont absents.

Nécessite soit :
1. Variables d'environnement KAGGLE_USERNAME + KAGGLE_KEY
2. OU fichier ~/.kaggle/kaggle.json (Kaggle CLI standard)
3. OU téléchargement manuel depuis le navigateur (fallback documenté)

Dataset: https://www.kaggle.com/datasets/aadyasingh55/cocktails
"""

import sys
from pathlib import Path

# Ajouter la racine du projet au path pour accéder à src/
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.kaggle_integration import has_kaggle_credentials  # noqa: E402


def check_kaggle_api() -> bool:
    """Vérifie si l'API Kaggle est disponible (credentials + package)."""
    if not has_kaggle_credentials():
        return False
    try:
        import kaggle  # noqa: F401
        return True
    except ImportError:
        return False


def download_with_kaggle_api():
    """Télécharge avec l'API Kaggle."""
    try:
        import kaggle

        dataset_slug = "aadyasingh55/cocktails"
        output_path = Path(__file__).parent.parent / "data"
        output_path.mkdir(exist_ok=True)

        print(f"Telechargement du dataset {dataset_slug}...")
        kaggle.api.dataset_download_files(
            dataset_slug,
            path=str(output_path),
            unzip=True
        )

        print("[OK] Dataset telecharge et extrait dans data/")
        return True

    except Exception as e:
        print(f"[ERREUR] Echec avec l'API Kaggle: {e}")
        return False


def manual_download_instructions():
    """Affiche les instructions pour téléchargement manuel."""
    print("\n" + "="*60)
    print("TELECHARGEMENT MANUEL REQUIS")
    print("="*60)
    print("\n1. Visitez: https://www.kaggle.com/datasets/aadyasingh55/cocktails")
    print("\n2. Cliquez sur 'Download' (necessite un compte Kaggle)")
    print("\n3. Extrayez le fichier ZIP telecharge")
    print("\n4. Trouvez le fichier CSV principal (probablement 'cocktails.csv' ou 'drinks.csv')")
    print("\n5. Copiez ce fichier CSV vers:")

    target_path = Path(__file__).parent.parent / "data" / "kaggle_raw.csv"
    print(f"   {target_path}")
    print("\n6. Renommez-le en 'kaggle_raw.csv'")
    print("\n7. Relancez enrich_kaggle.py pour continuer")
    print("\n" + "="*60)


def main():
    """Fonction principale."""
    print("Download Kaggle Cocktails Dataset")
    print("-" * 40)

    # Vérifier si le fichier existe déjà
    target_path = Path(__file__).parent.parent / "data" / "kaggle_raw.csv"
    if target_path.exists():
        print(f"\n[INFO] Le fichier {target_path} existe deja!")
        response = input("Voulez-vous le re-telecharger? (o/N): ")
        if response.lower() != 'o':
            print("[SKIP] Telechargement annule.")
            return

    # Essayer avec l'API Kaggle
    if check_kaggle_api():
        print("[INFO] API Kaggle detectee")
        if download_with_kaggle_api():
            print("\n[OK] Telechargement termine avec succes!")

            # Trouver le CSV téléchargé et le renommer
            data_dir = Path(__file__).parent.parent / "data"
            csv_files = list(data_dir.glob("*.csv"))
            csv_files = [f for f in csv_files if "kaggle" in f.stem.lower() or "cocktail" in f.stem.lower() or "drink" in f.stem.lower()]

            if csv_files:
                source = csv_files[0]
                if source.name != "kaggle_raw.csv":
                    print(f"[INFO] Renommage {source.name} -> kaggle_raw.csv")
                    source.rename(target_path)
                print(f"[OK] Dataset pret: {target_path}")
            else:
                print("[WARN] Fichier CSV non trouve. Verifiez data/ manuellement.")
            return

    # Sinon, instructions manuelles
    print("[INFO] API Kaggle non disponible")
    print("[INFO] Pour installer: pip install kaggle")
    print("[INFO] Puis configurez ~/.kaggle/kaggle.json")
    manual_download_instructions()


if __name__ == "__main__":
    main()
