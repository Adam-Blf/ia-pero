# Architecture & Guide du Code - L'IA Pero

Ce document explique ou trouver chaque fonctionnalite dans le code.

## Vue d'Ensemble

```
ia-pero/
├── src/
│   ├── app.py          # Frontend Streamlit (UI)
│   ├── backend.py      # Backend RAG & GenAI
│   ├── embeddings.py   # Utilitaires SBERT
│   └── generate_data.py # Generateur de donnees
├── data/
│   ├── cocktails.csv   # Base de 600 cocktails
│   ├── recipe_cache.json # Cache des recettes (auto-genere)
│   └── analytics.json  # Logs des requetes (auto-genere)
└── tests/
    └── test_guardrail.py # Tests E2E Playwright
```

---

## src/app.py - Frontend Streamlit

### Sections du Fichier

| Lignes | Section | Description |
|--------|---------|-------------|
| 1-27 | **Imports & Config** | Imports Python, logging, constantes |
| 29-44 | **Constantes** | Chemins CSV, fichier analytics, requetes surprise |
| 46-53 | **Page Config** | Configuration Streamlit (titre, icone, layout wide) |
| 56-302 | **CSS Theme** | Styles CSS Speakeasy annees 1920 |
| 308-327 | **Session State** | Initialisation: history, metrics, filters |
| 332-378 | **Analytics** | Logging des requetes, metriques session |
| 383-438 | **Recherche SBERT** | Recherche semantique dans les 600 cocktails |
| 443-484 | **Export PDF** | Generation du fichier texte telechargeable |
| 498-541 | **Radar Chart** | Graphique Plotly profil gustatif |
| 560-661 | **Control Panels** | Filtres, recherche SBERT, historique, metriques |
| 667-765 | **UI Components** | Header, input hybride, cards, empty state |
| 822-940 | **Main App** | Point d'entree, orchestration de l'UI |

### Ou Trouver...

| Fonctionnalite | Fichier | Fonction |
|----------------|---------|----------|
| **Theme CSS Speakeasy** | app.py | `SPEAKEASY_CSS` |
| **Couleurs Or/Noir** | app.py | Commentaire palette dans CSS |
| **Filtres (Alcool/Difficulte/Temps)** | app.py | `render_filters_panel()` |
| **Recherche SBERT** | app.py | `render_search_panel()` |
| **Historique des recettes** | app.py | `render_history_metrics_panel()` |
| **Metriques de session** | app.py | `render_history_metrics_panel()` |
| **Musique jazz** | app.py | `render_filters_panel()` |
| **Champ texte envie** | app.py | `render_cocktail_input()` |
| **Dropdown Budget** | app.py | `render_cocktail_input()` |
| **Bouton Surprise** | app.py | `render_cocktail_input()` |
| **Affichage ingredients** | app.py | `render_cocktail_card()` |
| **Etapes preparation** | app.py | `render_cocktail_card()` |
| **Graphique radar** | app.py | `render_cocktail_card()` |
| **Bouton telecharger** | app.py | `render_cocktail_card()` |
| **Footer auteurs** | app.py | `render_footer()` |

---

## src/backend.py - Backend RAG & GenAI

### Sections du Fichier

| Lignes | Section | Description |
|--------|---------|-------------|
| 1-24 | **Imports** | Imports, chargement .env |
| 26-41 | **Configuration** | Modele SBERT, mots-cles, seuil, chemin cache |
| 44-50 | **SBERT Model** | Chargement modele avec cache LRU |
| 53-88 | **Guardrail** | Verification pertinence (similarite cosinus) |
| 91-113 | **Prompt Gemini** | Persona barman speakeasy + format JSON |
| 116-225 | **API Gemini** | Appel API avec fallback multi-modeles |
| 228-270 | **Fallback Recipe** | Recette de secours si API indisponible |
| 273-297 | **Cache Management** | Gestion cache JSON (cle MD5, load, save) |
| 300-348 | **Generate Recipe** | Pipeline principal de generation |

### Ou Trouver...

| Fonctionnalite | Fichier | Ligne | Fonction |
|----------------|---------|-------|----------|
| **Modele SBERT utilise** | backend.py | 29 | `MODEL_NAME = "all-MiniLM-L6-v2"` |
| **Mots-cles cocktail** | backend.py | 30-34 | `COCKTAIL_KEYWORDS` |
| **Seuil de pertinence** | backend.py | 35 | `RELEVANCE_THRESHOLD = 0.35` |
| **Chemin du cache** | backend.py | 36 | `CACHE_FILE` |
| **Chargement SBERT** | backend.py | 47-50 | `get_sbert_model()` |
| **Calcul similarite** | backend.py | 72-80 | Dans `check_relevance()` |
| **Message erreur hors-sujet** | backend.py | 83-86 | Dans `check_relevance()` |
| **Prompt du barman** | backend.py | 94-113 | `SPEAKEASY_PROMPT` |
| **Liste modeles Gemini** | backend.py | 140-146 | Dans `_call_gemini_api()` |
| **Gestion rate limit 429** | backend.py | 171-173 | Dans `_call_gemini_api()` |
| **Parsing JSON reponse** | backend.py | 191-197 | Dans `_call_gemini_api()` |
| **Recette fallback** | backend.py | 228-270 | `_generate_fallback_recipe()` |
| **Cle cache MD5** | backend.py | 276-278 | `_get_cache_key()` |
| **Pipeline generation** | backend.py | 303-348 | `generate_recipe()` |

---

## Flux de Donnees

```
┌─────────────────────────────────────────────────────────────────┐
│                         UTILISATEUR                              │
│                   (texte + budget + filtres)                     │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      src/app.py                                  │
│  render_filters_panel() → Capture filtres (alcool, difficulte)  │
│  render_cocktail_input() → Capture envie + budget + surprise    │
│  main() → Enrichit query avec filtres                           │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     src/backend.py                               │
│  generate_recipe(query)                                          │
│     │                                                            │
│     ├─1→ check_relevance() → Guardrail SBERT (seuil 0.35)       │
│     │    Si hors-sujet → return {"status": "error"}             │
│     │                                                            │
│     ├─2→ _get_cache_key() → MD5 de la query                     │
│     │    _load_cache() → Verifie si deja en cache               │
│     │    Si cache hit → return recipe + cached=True             │
│     │                                                            │
│     ├─3→ _call_gemini_api() → Appel API avec fallback modeles   │
│     │    gemini-2.5-flash-lite → flash → 3-flash → 1.5 → pro    │
│     │                                                            │
│     ├─4→ Si API echoue → _generate_fallback_recipe()            │
│     │                                                            │
│     └─5→ _save_cache() → Sauvegarde pour prochaine fois         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      src/app.py                                  │
│  log_request() → Sauve analytics JSON + met a jour metriques    │
│  add_to_history() → Ajoute a l'historique session               │
│  render_cocktail_card() → Affiche recette + radar + export      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Fichiers de Configuration

| Fichier | Contenu |
|---------|---------|
| `.env` | `GOOGLE_API_KEY=...` |
| `.streamlit/config.toml` | Theme Streamlit |
| `requirements.txt` | Dependances Python |
| `.gitignore` | Fichiers exclus de Git |

---

## Points d'Extension

### Ajouter un nouveau filtre
1. Ajouter le selectbox dans `render_filters_panel()` (app.py)
2. Stocker dans `st.session_state.filters`
3. Ajouter la logique dans `main()` (section filter_context)

### Modifier le prompt Gemini
1. Editer `SPEAKEASY_PROMPT` (backend.py:94-113)
2. Ajuster le format JSON attendu si necessaire

### Ajouter une dimension au radar
1. Ajouter dans `generate_cocktail_characteristics()` (app.py)
2. Ajouter dans `taste_required` (backend.py:206)
3. Ajouter dans `SPEAKEASY_PROMPT` (backend.py:107)

### Modifier le seuil du guardrail
1. Editer `RELEVANCE_THRESHOLD` (backend.py:35)
2. Valeurs recommandees: 0.20 (permissif) → 0.50 (restrictif)

---

## Tests

### Lancer les tests E2E
```bash
# Installer Playwright
playwright install chromium

# Lancer les tests
pytest tests/test_guardrail.py -v
```

### Tests manuels du guardrail
- Requete rejetee: "Comment reparer mon velo ?"
- Requete acceptee: "Un mojito frais et tropical"

---

## Auteurs

**Adam Beloucif & Amina Medjdoub**
RNCP Bloc 2 - Expert en Ingenierie de Donnees
