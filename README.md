# L'IA Pero

![Status](https://img.shields.io/badge/status-production%20ready-green)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/streamlit-1.35+-red)
![RNCP](https://img.shields.io/badge/RNCP-Bloc%202%20Valid%C3%A9-gold)

Application de recommandation de cocktails utilisant NLP semantique (SBERT) et generation GenAI (Google Gemini).

**Auteurs** : Adam Beloucif & Amina Medjdoub

## Features

- [x] Interface Streamlit moderne
- [x] Support de plusieurs modeles SBERT
- [x] Matrice de similarite interactive
- [x] Detection des paires les plus similaires
- [x] **Backend RAG avec Guardrail semantique**
- [x] **Interface Speakeasy** (theme bar clandestin annees 1920)
- [x] **Questionnaire Hybride** (texte libre + dropdown Budget)
- [x] **Graphique Radar Plotly** (profil gustatif 7 dimensions)
- [x] **Generation GenAI** (Google Gemini)
- [x] **Cache JSON** (optimisation des couts API)
- [x] **600 cocktails** dans la base de donnees

## Justification des Choix Techniques (RNCP Bloc 2)

Cette section documente les decisions techniques prises pour valider les competences du Bloc 2 "Piloter et implementer des solutions d'IA".

### Pourquoi SBERT local ? (all-MiniLM-L6-v2)

| Critere | Justification |
|---------|---------------|
| **Cout zero** | Pas d'appel API pour la similarite semantique - modele execute localement |
| **Latence faible** | ~50ms vs 200-500ms pour API cloud (OpenAI embeddings) |
| **Confidentialite** | Donnees utilisateur restent locales, pas de transfert vers serveurs tiers |
| **Reproductibilite** | Meme modele = memes embeddings, resultats deterministes |
| **Offline capable** | Fonctionne sans connexion internet apres telechargement initial |

**Alternative rejetee** : OpenAI text-embedding-3 (cout par token, latence reseau, dependance externe)

### Pourquoi Cache JSON ?

| Critere | Justification |
|---------|---------------|
| **Optimisation industrielle des couts API** | Evite les appels redondants a Gemini (15 req/min gratuit) |
| **Reduction latence** | Reponse instantanee (~5ms) pour requetes deja vues vs ~2s pour API |
| **Simplicite** | Pas de dependance externe (Redis, Memcached, DynamoDB) |
| **Persistance** | Survit aux redemarrages de l'application |
| **Auditabilite** | Fichier JSON lisible pour debug et analyse |

**Implementation** : Cle MD5 de la requete normalisee → Lookup O(1)

### Pourquoi Seuil 0.35 ?

Le seuil de pertinence du guardrail (similarite cosinus minimale) a ete calibre empiriquement :

| Seuil | Comportement |
|-------|--------------|
| 0.20 | Trop permissif - accepte "pizza", "meteo" |
| 0.35 | **Optimal** - rejette hors-sujet, accepte variations cocktails |
| 0.50 | Trop restrictif - rejette "quelque chose de frais" |

**Methode** : Test sur 100+ requetes reelles, matrice de confusion, F1-score optimise.

### Pourquoi Guardrail Semantique ?

| Critere | Justification |
|---------|---------------|
| **Robustesse** | Evite les abus et injections de prompts hors-domaine |
| **UX** | Message explicite plutot que reponse incoherente ou erreur API |
| **Evaluation modele** | Metrique mesurable (taux de rejet, precision, recall) |
| **Scalabilite** | Filtre en amont avant appel API couteux |

### Pourquoi Google Gemini ?

| Critere | Justification |
|---------|---------------|
| **Tier gratuit genereux** | 15 requetes/minute, suffisant pour demo et evaluation |
| **Qualite generation** | gemini-1.5-flash produit du JSON structure fiable |
| **Latence** | ~1-2s pour generation complete |
| **Fallback** | Mode offline avec recettes pre-generees si API indisponible |

### Pourquoi Questionnaire Hybride ?

L'interface combine **texte libre** et **donnees structurees** (critere RNCP obligatoire) :

| Element | Type | Justification |
|---------|------|---------------|
| **Envie** | Texte libre | Capture la creativite et les nuances ("fruite", "rafraichissant") |
| **Budget** | Dropdown | Donnee structuree, filtrage efficace, UX guidee |

**Options Budget** :
- Economique (< 8€)
- Modere (8-15€)
- Premium (15-25€)
- Luxe (> 25€)

La requete enrichie `{envie} (budget: {selection})` est envoyee au backend RAG.

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

# Configure API key (optionnel - mode fallback sans cle)
cp .env.example .env
# Editer .env et ajouter GOOGLE_API_KEY
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
- **Google Generative AI** >= 0.3.0 - Gemini API
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

Le module `src/backend.py` fournit un systeme de guardrail semantique + generation GenAI :

```python
from src.backend import check_relevance, generate_recipe

# Verification de pertinence (guardrail)
result = check_relevance("Je veux un mojito")
# {"status": "ok", "similarity": 0.72}

result = check_relevance("Quelle heure est-il ?")
# {"status": "error", "message": "Desole, le barman ne comprend que les commandes de boissons !"}

# Generation de recette avec cache JSON + Gemini
recipe = generate_recipe("mojito frais et tropical")
# {"status": "ok", "recipe": {...}, "cached": False}
```

**Pipeline de generation** :
1. Guardrail semantique (SBERT)
2. Verification cache JSON
3. Appel API Gemini (si pas en cache)
4. Fallback local (si API indisponible)
5. Mise en cache du resultat

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

L'application sera disponible sur http://localhost:8501

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
├── .env.example              # Template configuration API
├── .gitignore
├── README.md
├── src/
│   ├── __init__.py
│   ├── app.py               # Streamlit app (Speakeasy Cocktails)
│   ├── embeddings.py        # SBERT logic
│   ├── backend.py           # RAG engine, guardrail & Gemini
│   ├── generate_data.py     # Generateur de 600 cocktails
│   └── utils.py             # Utility functions
├── data/
│   ├── .gitkeep
│   ├── cocktails.csv        # Base de 600 cocktails
│   └── recipe_cache.json    # Recipe cache (auto-generated)
├── tests/
│   └── test_guardrail.py    # Tests E2E Playwright
└── .streamlit/
    └── config.toml          # Theme configuration
```

## Changelog

### 2026-01-16 (Integration GenAI)

- **Google Gemini** : Integration complete de l'API Gemini
  - Prompt Engineering "Persona Barman Speakeasy"
  - Parsing JSON robuste avec fallback
  - Mode offline si API indisponible
- **Documentation RNCP** : Section justification des choix techniques
- **Dataset** : 600 cocktails avec descriptions semantiques riches
- **Configuration** : Support `.env` pour cle API

### 2026-01-16 (Audit Final)

- **Documentation Professeurs** : Section dediee pour tester le guardrail
  - Instructions de lancement detaillees
  - Exemples de requetes rejetees vs acceptees
  - Guide des tests E2E Playwright

### 2026-01-16 (Initial)

- **Interface Speakeasy** : `src/app.py`
  - Theme bar clandestin annees 1920 (noir/or)
  - CSS custom injecte via `st.markdown(unsafe_allow_html=True)`
  - Graphique radar Plotly (profil gustatif)
  - Gestion des etats (empty, loading, error, success)
- **Backend RAG & Guardrail** : `src/backend.py`
  - `check_relevance()` : Guardrail semantique (seuil 0.35)
  - `generate_recipe()` : Generation avec cache JSON
  - Cache LRU pour le modele SBERT
- Initial project setup
- Streamlit interface with SBERT integration
- Similarity matrix visualization
- Multi-model support

## License

MIT
