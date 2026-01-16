

# L'IA Pero

![Status](https://img.shields.io/badge/status-in%20development-yellow)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.35+-red)

Explorez la similarite semantique entre vos textes grace aux embeddings Sentence-Transformers.

## Features

- [x] Interface Streamlit moderne
- [x] Support de plusieurs modeles SBERT
- [x] Matrice de similarite interactive
- [x] Detection des paires les plus similaires
- [x] **Backend RAG avec Guardrail semantique**
- [x] **Interface Speakeasy** (theme bar clandestin annees 1920)
- [x] **Graphique Radar Plotly** (profil gustatif)
- [ ] Upload de fichiers CSV/TXT
- [ ] Visualisation t-SNE/UMAP

## Installation

```bash
# Clone the repository
git clone https://github.com/Adam-Blf/ia-pero.git
cd ia-pero

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Linux/Mac)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Interface Similarite Semantique
streamlit run app.py

# Interface Speakeasy (Cocktails)
streamlit run src/app.py
```

L'application sera disponible sur http://localhost:8501

## Tech Stack

- **Python** 3.9+
- **Streamlit** >= 1.35 - Interface web interactive
- **Sentence-Transformers** >= 2.2.0 - Embeddings SBERT
- **PyTorch** >= 2.0.0 - Backend ML
- **Transformers** >= 4.34.0 - HuggingFace models
- **Pandas** - Data manipulation
- **NumPy** - Numerical operations
- **Plotly** >= 5.18.0 - Graphiques interactifs (radar chart)

## Models disponibles

| Modele | Dimensions | Description |
|--------|------------|-------------|
| `all-MiniLM-L6-v2` | 384 | Rapide et leger (default) |
| `all-mpnet-base-v2` | 768 | Meilleure qualite |
| `paraphrase-multilingual-MiniLM-L12-v2` | 384 | Support multilingue |

## Backend RAG & Guardrail

Le module `src/backend.py` fournit un systeme de guardrail semantique :

```python
from src.backend import check_relevance, generate_recipe

# Verification de pertinence (guardrail)
result = check_relevance("Je veux un mojito")
# {"status": "ok", "similarity": 0.27}

result = check_relevance("Quelle heure est-il ?")
# {"status": "error", "message": "Desole, le barman ne comprend que les commandes de boissons !"}

# Generation de recette avec cache JSON
recipe = generate_recipe("mojito frais")
# {"status": "ok", "recipe": {...}, "cached": False}
```

**Seuil de pertinence** : 0.35 (similarite cosinus avec les mots-cles cocktail)

## Pour les Professeurs - Preuve de Robustesse

Cette section demontre le fonctionnement du **guardrail semantique** qui rejette les requetes hors-sujet.

### Lancer l'Application

```bash
# Activer l'environnement virtuel
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Lancer l'interface Speakeasy
streamlit run src/app.py
```

L'application sera disponible sur <http://localhost:8501>

### Tester le Guardrail Semantique

#### Requetes REJETEES (hors-sujet)

Essayez ces requetes pour voir le message d'erreur :

| Requete | Resultat |
| ------- | -------- |
| "Comment reparer mon velo ?" | Message d'erreur |
| "Quelle est la capitale de la France ?" | Message d'erreur |
| "Quel temps fait-il ?" | Message d'erreur |
| "Raconte-moi une blague" | Message d'erreur |

**Message affiche** : "Desole, le barman ne comprend que les commandes de boissons !"

#### Requetes ACCEPTEES (domaine cocktail)

| Requete | Resultat |
| ------- | -------- |
| "Je veux un mojito" | Recette + Radar chart |
| "Un cocktail fruite et rafraichissant" | Recette + Radar chart |
| "Whisky sour" | Recette + Radar chart |
| "Quelque chose avec du rhum" | Recette + Radar chart |

### Tests Automatises (E2E)

Des tests Playwright verifient automatiquement le guardrail :

```bash
# Installer Playwright (premiere fois)
playwright install chromium

# Lancer les tests
pytest tests/test_guardrail.py -v
```

**Couverture des tests** :

- `test_off_topic_query_shows_error` : Verifie qu'une requete hors-sujet affiche l'erreur
- `test_cocktail_query_shows_recipe` : Verifie qu'une requete cocktail affiche la recette
- `test_complete_flow` : Scenario complet (erreur puis succes)

## Project Structure

```
ia-pero/
├── app.py                    # Streamlit app (Similarite Semantique)
├── requirements.txt          # Python dependencies
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── app.py               # Streamlit app (Speakeasy Cocktails)
│   ├── embeddings.py        # SBERT logic
│   ├── backend.py           # RAG engine & guardrail
│   └── utils.py             # Utility functions
├── data/
│   ├── .gitkeep
│   └── recipe_cache.json    # Recipe cache (auto-generated)
└── .streamlit/
    └── config.toml          # Theme configuration
```

## Changelog

### 2026-01-16 (Audit Final)

- **Documentation Professeurs** : Section dediee pour tester le guardrail
  - Instructions de lancement detaillees
  - Exemples de requetes rejetees vs acceptees
  - Guide des tests E2E Playwright
- **Correction** : Seuil de pertinence dans README (0.25 → 0.35)

### 2026-01-16

- **Interface Speakeasy** : `src/app.py`
  - Theme bar clandestin annees 1920 (noir/or)
  - CSS custom injecte via `st.markdown(unsafe_allow_html=True)`
  - Graphique radar Plotly (profil gustatif)
  - Gestion des etats (empty, loading, error, success)
  - Affichage conditionnel selon status backend
- **Backend RAG & Guardrail** : `src/backend.py`
  - `check_relevance()` : Guardrail semantique (seuil 0.25)
  - `generate_recipe()` : Generation avec cache JSON
  - Cache LRU pour le modele SBERT
- Initial project setup
- Streamlit interface with SBERT integration
- Similarity matrix visualization
- Multi-model support

## License

MIT
