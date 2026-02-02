# Intégration Dataset Kaggle - Guide d'Utilisation

## Vue d'ensemble

Ce guide explique comment intégrer le dataset Kaggle cocktails dans L'IA Pero, permettant à l'IA de déduire automatiquement les profils de saveurs d'ingrédients inconnus (ex: "framboise = sucré + acide").

## Système d'Inférence de Profils de Saveurs

Le système utilise une approche **hybride à 4 niveaux** pour déterminer les profils de saveurs :

### Niveau 1: Base Connue (0 coût API)
- 60 ingrédients hardcodés avec profils prédéfinis
- Inclut les spiritueux, mixers et modificateurs courants
- Mappings EN→FR pour compatibilité avec le dataset Kaggle

### Niveau 2: Similarité Sémantique (0 coût API)
- Utilise SBERT (all-MiniLM-L6-v2) pour trouver des ingrédients similaires
- Seuil: similarité cosine > 0.75
- Ex: "Blackberry" → similaire à "Puree de framboise" → copie le profil

### Niveau 3: Inférence LLM (coût minimal)
- Appelle Gemini pour inférer le profil d'ingrédients vraiment nouveaux
- ~20-40 appels API pour le dataset Kaggle complet
- Cache persistant pour éviter les appels redondants

### Niveau 4: Fallback par Catégorie (0 coût API)
- Profil par défaut selon le type détecté (juice, syrup, liqueur, etc.)
- Assure qu'un profil est toujours disponible

## Étapes d'Installation

### 1. Télécharger le Dataset Kaggle

#### Option A: Téléchargement Manuel (Recommandé)

1. Visitez: https://www.kaggle.com/datasets/aadyasingh55/cocktails
2. Cliquez sur "Download" (nécessite un compte Kaggle gratuit)
3. Extrayez le fichier ZIP téléchargé
4. Copiez le fichier CSV principal vers: `data/kaggle_raw.csv`

#### Option B: API Kaggle (Optionnel)

```bash
# Installer l'API Kaggle
pip install kaggle

# Configurer les credentials (voir https://www.kaggle.com/docs/api)
# Placer kaggle.json dans ~/.kaggle/

# Télécharger automatiquement
python scripts/download_kaggle.py
```

### 2. Générer la Base de Connaissance

Exécutez le script pour extraire les 60 ingrédients connus :

```bash
python scripts/export_known_ingredients.py
```

**Sortie attendue:**
- Fichier créé: `data/known_ingredients.json`
- 60 ingrédients avec profils complets

### 3. Enrichir le Dataset Kaggle

Lancez le pipeline d'enrichissement complet :

```bash
python scripts/enrich_kaggle.py
```

**Ce que ce script fait:**
1. Parse le dataset Kaggle brut
2. Extrait les ingrédients uniques (~200)
3. Infère les profils via le système 4 niveaux
4. Calcule les profils de saveurs pour chaque cocktail
5. Génère les colonnes manquantes (description_semantique, difficulty, prep_time)
6. Sauvegarde le dataset enrichi dans `data/kaggle_cocktails_enriched.csv`

**Durée estimée:** 10-15 minutes

**Statistiques attendues:**
- Cocktails enrichis: ~1000-1200
- Ingrédients profilés: ~200
- Appels API Gemini: 20-40 (gratuit tier)

### 4. Lancer l'Application

```bash
streamlit run src/app.py
```

L'application chargera automatiquement les deux datasets:
- 600 cocktails générés (L'IA Pero)
- 1000+ cocktails Kaggle enrichis

**Total: ~1800 cocktails disponibles!**

## Utilisation de l'Interface

### Filtre par Source

Dans l'onglet **"Filtres"** de la sidebar, vous trouverez un nouveau filtre "Source des cocktails" avec 3 options:

1. **Tous** - Affiche tous les cocktails (générés + Kaggle)
2. **Générés par IA** - Uniquement les cocktails créés par L'IA Pero
3. **Base Kaggle** - Uniquement les cocktails réels du dataset Kaggle

### Badge de Source

Les cocktails Kaggle affichent un badge bleu "Kaggle" à côté du nom pour les identifier visuellement.

### Recherche Sémantique

La recherche sémantique fonctionne sur les deux sources et respecte le filtre de source sélectionné.

Exemple:
```
Requête: "Margarita"
Filtre: "Base Kaggle"
→ Retourne uniquement les Margaritas du dataset Kaggle
```

## Architecture des Fichiers

```
ia-pero/
├── src/
│   ├── app.py                       # [MODIFIÉ] Fusion datasets + filtre source
│   ├── backend.py                   # Backend RAG & Guardrail (inchangé)
│   ├── ingredient_profiler.py       # [NOUVEAU] Système d'inférence 4 niveaux
│   ├── kaggle_integration.py        # [NOUVEAU] Parser dataset Kaggle
│   ├── generate_data.py             # Générateur de cocktails (inchangé)
│   └── ...
├── scripts/
│   ├── export_known_ingredients.py  # [NOUVEAU] Extracteur base de connaissance
│   ├── enrich_kaggle.py             # [NOUVEAU] Pipeline d'enrichissement
│   └── download_kaggle.py           # [NOUVEAU] Téléchargeur Kaggle
├── data/
│   ├── cocktails.csv                # 600 cocktails générés (existant)
│   ├── known_ingredients.json       # [NOUVEAU] Base de 60 ingrédients
│   ├── ingredient_profiles.json     # [NOUVEAU] Cache profils inférés
│   ├── kaggle_raw.csv               # [NOUVEAU] Dataset Kaggle brut
│   └── kaggle_cocktails_enriched.csv # [NOUVEAU] Dataset Kaggle enrichi
└── KAGGLE_INTEGRATION.md            # [NOUVEAU] Ce fichier
```

## Vérification et Tests

### Test 1: Vérifier Base de Connaissance

```bash
python -c "
import json
with open('data/known_ingredients.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
print(f'Spiritueux: {len(data[\"spirits\"])}')
print(f'Mixers: {len(data[\"mixers\"])}')
print(f'Modificateurs: {len(data[\"modifiers\"])}')
"
```

**Attendu:**
```
Spiritueux: 15
Mixers: 25
Modificateurs: 20
```

### Test 2: Tester Profiler

```bash
python src/ingredient_profiler.py
```

**Attendu:**
```
[OK] IngredientProfiler initialized with 60 known ingredients
Test 1: Ingredient connu (Vodka)
  Source: known
  [PASS]
Test 2: Ingredient similaire (Blackberry)
  Source: similarity
  [PASS]
Test 3: Fallback (XYZ Unknown Ingredient)
  Source: fallback
  [PASS]
[OK] All tests passed!
```

### Test 3: Vérifier Enrichissement

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/kaggle_cocktails_enriched.csv')
print(f'Cocktails enrichis: {len(df)}')
print(f'Colonnes: {list(df.columns)}')
print(f'Exemple de profil: {df.iloc[0][\"taste_profile\"][:100]}...')
"
```

**Attendu:**
```
Cocktails enrichis: 1000+
Colonnes: ['name', 'description_semantique', 'ingredients', 'instructions', 'category', 'difficulty', 'prep_time', 'taste_profile']
Exemple de profil: {"Douceur": 3.5, "Acidite": 2.5, "Amertume": 2.0, "Force": 4.0, "Fraicheur": 3.0}...
```

### Test 4: Vérifier Application

1. Lancez l'application: `streamlit run src/app.py`
2. Ouvrez la sidebar → Onglet "Filtres"
3. Vérifiez que le filtre "Source des cocktails" est présent
4. Sélectionnez "Base Kaggle"
5. Faites une recherche sémantique (ex: "Margarita")
6. Vérifiez que les résultats ont un badge bleu "Kaggle"

## Audit et Maintenance

### Compter les Appels API

```bash
python -c "
import json
with open('data/ingredient_profiles.json', 'r', encoding='utf-8') as f:
    profiles = json.load(f)
gemini_calls = sum(1 for p in profiles.values() if p.get('source') == 'gemini')
print(f'Appels API Gemini: {gemini_calls}')
print(f'Coût estimé: 0€ (tier free Gemini)')
"
```

### Réinitialiser le Cache

Si vous voulez réinférer tous les profils:

```bash
# Sauvegarder l'ancien cache
mv data/ingredient_profiles.json data/ingredient_profiles_backup.json

# Relancer l'enrichissement
python scripts/enrich_kaggle.py
```

### Ajouter de Nouveaux Ingrédients

Pour ajouter manuellement des profils d'ingrédients dans `data/known_ingredients.json`:

```json
{
  "mixers": {
    "nouveau_ingredient": {
      "name_fr": "Nouveau Ingredient",
      "name_en": ["new ingredient"],
      "strength": 1.5,
      "sweetness": 3.0,
      "acidity": 2.5,
      "bitterness": 1.5,
      "freshness": 3.5,
      "type": "fruit",
      "category": "mixer"
    }
  }
}
```

Puis relancez l'enrichissement.

## Réponse à la Question Initiale

**"L'IA peut-elle comprendre que framboise = sucré + acide ?"**

### Avant ce système ✅ OUI (Partiellement)

L'IA pouvait comprendre pour les 60 ingrédients hardcodés:
```python
{"name": "Puree de framboise", "acidity": 2.5, "sweetness": 3.5}
```

Mais **pas** pour des ingrédients inconnus comme "Yuzu", "Blackberry", etc.

### Après ce système ✅ OUI (Complètement)

L'IA peut maintenant déduire automatiquement pour **tout ingrédient**:

```
Ingrédient: "Yuzu"
→ Niveau 2: Similarité avec "Jus de citron vert" = 0.82
→ Résultat: {acidity: 4.5, sweetness: 1.5, ...}

Ingrédient: "Elderflower" (inconnu)
→ Niveau 3: Appel Gemini
→ Résultat: {sweetness: 3.5, acidity: 1.5, freshness: 4.0, ...}
```

## Troubleshooting

### Erreur: "Kaggle CSV not found"

**Solution:** Téléchargez le dataset Kaggle et placez-le dans `data/kaggle_raw.csv`

### Erreur: "SBERT not available"

**Solution:** Installez sentence-transformers:
```bash
pip install sentence-transformers
```

### Erreur: "Gemini API not configured"

**Solution:** Configurez la clé API Gemini:
```bash
# Créer .env
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### Les cocktails Kaggle n'apparaissent pas

**Vérifications:**
1. Le fichier `data/kaggle_cocktails_enriched.csv` existe-t-il ?
2. L'application a-t-elle été relancée après l'enrichissement ?
3. Le cache Streamlit a-t-il été vidé ? (Ctrl+R dans l'app)

### Performances lentes

**Optimisations:**
- Le cache SBERT se régénère au premier lancement (3-5s normal)
- Les appels suivants sont <100ms grâce au cache
- Si toujours lent, vérifiez que `@st.cache_data` fonctionne

## Support

Pour toute question ou problème:
- Vérifiez les logs de l'application
- Consultez les tests unitaires dans chaque module
- Relisez ce guide pour vérifier les étapes

## Prochaines Améliorations Possibles

1. **Interface de gestion des profils** - UI pour visualiser et éditer les profils d'ingrédients
2. **Validation communautaire** - Permettre aux utilisateurs de corriger les profils inférés
3. **Modèle ML custom** - Remplacer Gemini par un modèle fine-tuné sur les profils existants
4. **Intégration d'autres datasets** - Ajouter CocktailDB, IBA, etc.
5. **Analyse des tendances** - Stats sur les profils de saveurs les plus populaires

---

**Bon mixage! 🍸**
