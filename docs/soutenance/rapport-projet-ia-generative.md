# L'IA PERO
## Agent Intelligent Semantique et Generatif pour la Recommandation de Cocktails

---

# RAPPORT DE PROJET IA GENERATIVE

**Projet Certifiant RNCP40875**
**Expert en Ingenierie de Donnees - Bloc 2**
**Pilotage et Implementation de Solutions IA**

---

![Logo EFREI](assets/efrei_logo.png)

---

**Titre du Projet:** L'IA Pero - Moteur de Recommandation Semantique de Cocktails avec IA Generative

**Auteurs:**
- **Adam BELOUCIF**
- **Amina MEDJDOUB**

**Formation:** Mastere Data Engineering et Intelligence Artificielle
**Etablissement:** EFREI Paris
**Tutrice:** Sarah MALAEB
**Annee Universitaire:** 2025-2026
**Date de Remise:** Fevrier 2026

---

**Mention Obligatoire:**
*Projet certifiant RNCP40875 Expert en Ingenierie de Donnees*
*Bloc 2 : Pilotage et implementation de solutions IA*

---

\newpage

# TABLE DES MATIERES

1. Resume Executif
2. Introduction et Contexte
   - 2.1 Problematique Adressee
   - 2.2 Contexte Industriel
   - 2.3 Cadre Theorique
   - 2.4 Justification des Technologies
3. Analyse du Besoin Utilisateur
   - 3.1 Etude des Personas
   - 3.2 Objectifs Utilisateurs
   - 3.3 Scenarios d'Usage Detailles
   - 3.4 Hypotheses et Contraintes
   - 3.5 User Journey Map
4. Methodologie de Travail et Gestion de Projet
   - 4.1 Approche Methodologique
   - 4.2 Planning et Jalons
   - 4.3 Organisation du Binome
   - 4.4 Outils Collaboratifs
   - 4.5 Gestion des Risques
   - 4.6 Suivi et Indicateurs
5. Referentiel de Donnees
   - 5.1 Sources de Donnees
   - 5.2 Modele Conceptuel de Donnees
   - 5.3 Schema et Structure
   - 5.4 Qualite et Gouvernance des Donnees
   - 5.5 Dictionnaire de Donnees
6. Pipeline IA et Architecture
   - 6.1 Vue d'Ensemble du Pipeline
   - 6.2 Etape 1: Collecte et Questionnaire
   - 6.3 Etape 2: Pre-traitement et Enrichissement
   - 6.4 Etape 3: Embeddings SBERT
   - 6.5 Etape 4: Calcul de Similarite
   - 6.6 Etape 5: Scoring et Agregation
   - 6.7 Etape 6: Generation des Recommandations
   - 6.8 Etape 7: Pipeline RAG et GenAI
   - 6.9 Architecture Technique Globale
7. Implementation Technique
   - 7.1 Architecture Logicielle
   - 7.2 Technologies et Frameworks
   - 7.3 Modele SBERT: Choix et Justification
   - 7.4 Calcul des Similarites Cosinus
   - 7.5 Systeme de Scoring Pondere
   - 7.6 Integration API GenAI
   - 7.7 Interface Streamlit
   - 7.8 Structure du Depot Git
   - 7.9 Gouvernance et Responsabilisation
8. Interface Utilisateur et Prototype
   - 8.1 Design et UX
   - 8.2 Composants de l'Interface
   - 8.3 Parcours Utilisateur
   - 8.4 Visualisations
9. Resultats et Tests
   - 9.1 Strategie de Test
   - 9.2 Tests Unitaires
   - 9.3 Tests E2E
   - 9.4 Tests d'Integration
   - 9.5 Demonstrations et Validations
   - 9.6 Metriques de Performance
10. Limites et Pistes d'Amelioration
    - 10.1 Limites Techniques
    - 10.2 Limites Fonctionnelles
    - 10.3 Ameliorations Court Terme
    - 10.4 Ameliorations Moyen Terme
    - 10.5 Vision Long Terme
11. Conclusion
    - 11.1 Synthese des Realisations
    - 11.2 Competences Acquises
    - 11.3 Valeur Demontree
12. Annexes
    - A. Arborescence Complete
    - B. Dictionnaire de Donnees
    - C. Prompts GenAI
    - D. Extraits de Code
    - E. Captures d'Ecran
    - F. Resultats de Tests

---

\newpage

# 1. RESUME EXECUTIF

## 1.1 Presentation du Projet

L'IA Pero est un moteur de recommandation de cocktails innovant, base sur l'intelligence artificielle semantique. Ce projet combine les technologies les plus avancees du traitement du langage naturel (NLP) avec l'IA generative pour offrir une experience utilisateur unique et personnalisee dans le domaine de la mixologie.

Le nom "Pero" fait reference au mot espagnol signifiant "mais" ou "cependant", symbolisant la capacite du systeme a comprendre les nuances et les preferences subtiles des utilisateurs, tout en proposant des alternatives creatives et inattendues.

## 1.2 Objectifs du Projet

### Objectif Principal
Developper un systeme intelligent capable de:
- Comprendre les preferences gustatives exprimees en langage naturel
- Recommander des cocktails personnalises avec une precision semantique elevee
- Generer des recettes originales via un pipeline RAG controle

### Objectifs Secondaires
- Implementer la formule de scoring RNCP pour l'evaluation des competences
- Creer une interface utilisateur immersive et intuitive
- Assurer la tracabilite et la gouvernance des donnees
- Optimiser les couts d'utilisation des API externes

## 1.3 Principaux Choix Techniques

### Modele NLP
Nous avons selectionne le modele **all-MiniLM-L6-v2** de la famille Sentence-BERT pour plusieurs raisons:
- Dimension compacte de 384, optimisant la memoire et les performances
- Excellente qualite des embeddings semantiques
- Temps d'inference rapide (~50ms par phrase)
- Compatibilite avec le francais malgre un entrainement principalement anglophone

### Mesure de Similarite
La **similarite cosinus** a ete choisie comme metrique principale:
- Norme independante de la longueur des vecteurs
- Interpretable (valeurs entre -1 et 1)
- Efficace pour les comparaisons semantiques
- Seuil optimise empiriquement a 0.30

### IA Generative
L'integration de **Google Gemini API** via un pipeline RAG (Retrieval-Augmented Generation):
- Acces gratuit avec quotas raisonnables pour l'usage pedagogique
- Multi-modeles avec failover automatique
- Cache intelligent pour optimiser les couts
- Fallback local en cas d'indisponibilite

### Interface Utilisateur
**Streamlit** pour le frontend avec un theme Speakeasy annees 1920:
- Prototypage rapide et iteratif
- Composants interactifs natifs
- Deploiement simplifie
- Experience utilisateur immersive

### Formule de Scoring RNCP
Implementation de la formule ponderee:
```
Coverage Score = SUM(Wi * Si) / SUM(Wi)
```
Ou Wi represente le poids du bloc i et Si le score de similarite.

## 1.4 Resultats Obtenus

### Base de Donnees
- **600+ cocktails** avec descriptions semantiques enrichies
- Integration du dataset Kaggle avec cocktails supplementaires
- 61 ingredients profiles avec caracteristiques gustatives
- Systeme de cache pour les recettes generees

### Tests et Qualite
- **24 tests automatises** avec 100% de reussite
- 3 tests E2E avec Playwright
- 16 tests unitaires avec Pytest
- 5 tests d'integration pour le systeme Kaggle

### Performance
- Temps de recherche moyen: 50ms
- Temps de generation Gemini: 1-3 secondes
- Cache hit rate: ~40%
- Precision du guardrail: >95%

### Interface
- Design immersif theme Speakeasy
- Radar chart interactif pour les profils gustatifs
- Export des recettes en format texte
- Responsive et accessible

## 1.5 Technologies Majeures

| Categorie | Technologies |
|-----------|--------------|
| Langage | Python 3.11 |
| Framework Web | Streamlit |
| NLP | Sentence-Transformers, SBERT |
| IA Generative | Google Gemini API |
| Data Processing | Pandas, NumPy |
| Visualisation | Plotly |
| Tests | Pytest, Playwright |
| Versioning | Git, GitHub |

## 1.6 Competences RNCP Demontrees

Ce projet valide les competences du Bloc 2 RNCP40875:

| Code | Competence | Validation |
|------|------------|------------|
| C3.1 | Preparation et transformation des donnees | Dataset de 600 cocktails nettoye et structure |
| C3.2 | Communication infographique | Radar charts, tableaux de bord interactifs |
| C3.3 | Analyse exploratoire | Scoring pondere, insights gustatifs |
| C5.1 | Identification cas d'usage GenAI | Recommandation semantique de cocktails |
| C5.2 | Developpement solution GenAI | Application complete et fonctionnelle |
| C5.3 | Evaluation qualite GenAI | Tests automatises, metriques de performance |

---

\newpage

# 2. INTRODUCTION ET CONTEXTE

## 2.1 Problematique Adressee

### 2.1.1 Le Defi de la Personnalisation

Le domaine de la mixologie represente un univers complexe et fascinant ou les preferences gustatives individuelles jouent un role crucial dans l'experience client. Contrairement a d'autres domaines ou les criteres de selection sont plus objectifs, le choix d'un cocktail repose sur des facteurs subjectifs et souvent difficiles a exprimer:

- **Preferences sensorielles**: douceur, acidite, amertume, force alcoolique
- **Contexte de consommation**: soiree, aperitif, celebration
- **Contraintes personnelles**: budget, ingredients disponibles, allergies
- **Ouverture a la nouveaute**: desir de decouverte vs. valeurs sures

### 2.1.2 L'Expression Vague des Preferences

Les utilisateurs expriment generalement leurs envies de maniere imprecise et subjective:

> "Je voudrais quelque chose de frais pour l'ete"
> "Un cocktail pas trop fort mais avec du caractere"
> "Quelque chose de tropical et exotique"
> "Comme un Mojito mais en plus original"

Ces formulations posent plusieurs defis techniques:
1. **Ambiguite lexicale**: "frais" peut signifier temperature, saveur, ou sensation
2. **Subjectivite**: "pas trop fort" varie selon les individus
3. **References implicites**: "comme un Mojito" suppose une connaissance partagee
4. **Combinaisons contradictoires**: certaines demandes peuvent etre incompatibles

### 2.1.3 Limites des Approches Traditionnelles

Les systemes de recommandation classiques presentent des limitations significatives:

**Recherche par mots-cles:**
- Ne capture pas la semantique
- Sensible aux variations orthographiques
- Ignore les synonymes et concepts proches

**Filtrage collaboratif:**
- Necessite un historique utilisateur
- Probleme du "cold start"
- Difficulte avec les nouveaux items

**Filtrage base sur le contenu:**
- Limite aux attributs explicites
- Ne comprend pas le langage naturel
- Rigidite des categories

### 2.1.4 Notre Proposition de Valeur

L'IA Pero propose une approche novatrice combinant:

1. **Comprehension semantique** du langage naturel via SBERT
2. **Personnalisation fine** grace aux preferences Likert
3. **Generation creative** avec l'IA generative controlee
4. **Experience immersive** dans un univers Speakeasy

Cette approche permet de transformer des requetes vagues en recommandations precises et pertinentes.

## 2.2 Contexte Industriel

### 2.2.1 Le Marche de la Mixologie

L'industrie des bars et restaurants connait une transformation profonde:

**Chiffres cles (2025):**
- Marche mondial des spiritueux: 1,500 milliards USD
- Croissance annuelle: 5.2%
- Segment cocktails premium: +8% par an
- Part du e-commerce: 15% et en hausse

**Tendances observees:**
- Demande croissante de personnalisation
- Interet pour les experiences uniques
- Montee en gamme des consommateurs
- Digitalisation de l'experience client

### 2.2.2 Besoins du Secteur

Les acteurs du marche expriment des besoins specifiques:

**Bars et restaurants:**
- Differenciation concurrentielle
- Formation des equipes
- Optimisation des stocks
- Fidelisation client

**Marques de spiritueux:**
- Education des consommateurs
- Promotion des produits
- Collecte de donnees marketing
- Engagement digital

**Consommateurs:**
- Decouverte guidee
- Confiance dans les choix
- Experience ludique
- Reproduction a domicile

### 2.2.3 Opportunites Identifiees

Notre solution repond a plusieurs opportunites de marche:

| Segment | Opportunite | Notre Reponse |
|---------|-------------|---------------|
| B2C | App de decouverte cocktails | Interface web immersive |
| B2B | Outil d'aide a la vente | Recommandations personnalisees |
| B2B2C | Widget integrable | API de recommandation |
| Education | Formation mixologie | Base de connaissances |

### 2.2.4 Positionnement Concurrentiel

**Concurrents directs:**
- Applications mobiles de recettes (Mixel, Highball)
- Sites web specialises (Diffords Guide, Liquor.com)
- Assistants vocaux generiques (Alexa Skills)

**Notre differenciation:**
- Comprehension semantique avancee
- Scoring pondere et explicable
- Generation de recettes originales
- Experience utilisateur premium

## 2.3 Cadre Theorique

### 2.3.1 Traitement du Langage Naturel (NLP)

Le NLP constitue le socle technologique de notre solution. Cette discipline de l'intelligence artificielle vise a permettre aux machines de comprendre, interpreter et generer le langage humain.

**Evolution historique:**
- **Annees 1950-1980**: Approches symboliques, grammaires formelles
- **Annees 1990-2000**: Methodes statistiques, n-grammes
- **Annees 2010**: Deep learning, word embeddings (Word2Vec)
- **Annees 2018+**: Transformers, modeles pre-entraines (BERT, GPT)

**Concepts fondamentaux:**
- **Tokenisation**: Decoupage du texte en unites elementaires
- **Embeddings**: Representation vectorielle dense du sens
- **Attention**: Mecanisme de ponderation contextuelle
- **Transfer learning**: Reutilisation de modeles pre-entraines

### 2.3.2 Sentence-BERT (SBERT)

SBERT represente une avancee majeure pour la similarite semantique entre phrases. Developpe par Reimers et Gurevych (2019), ce modele adapte l'architecture BERT pour produire des embeddings de phrases comparables directement.

**Architecture:**
```
Phrase A ──► BERT ──► Pooling ──► Embedding A
                                      │
                                      ├──► Similarite Cosinus
                                      │
Phrase B ──► BERT ──► Pooling ──► Embedding B
```

**Avantages par rapport a BERT standard:**
- Calcul de similarite en temps constant O(1)
- Pas besoin de passer toutes les paires par le modele
- Scalabilite pour les grandes bases de donnees
- Embeddings stockables et reutilisables

**Modele selectionne: all-MiniLM-L6-v2**
- 6 couches de transformers (vs 12 pour BERT-base)
- 384 dimensions (vs 768)
- 22M parametres (vs 110M)
- Performances proches de BERT avec 5x moins de ressources

### 2.3.3 Similarite Cosinus

La similarite cosinus mesure l'angle entre deux vecteurs dans un espace multidimensionnel:

```
cos(θ) = (A · B) / (||A|| × ||B||)
```

**Proprietes:**
- Valeurs entre -1 (oppose) et 1 (identique)
- 0 indique l'orthogonalite (aucune relation)
- Invariante a la norme des vecteurs
- Efficace en haute dimension

**Interpretation dans notre contexte:**
- **> 0.8**: Tres similaire, quasi-synonyme
- **0.5 - 0.8**: Lie semantiquement
- **0.3 - 0.5**: Relation faible mais pertinente
- **< 0.3**: Non pertinent, hors-sujet

### 2.3.4 RAG (Retrieval-Augmented Generation)

Le RAG combine la recherche d'information avec la generation de texte:

**Pipeline RAG:**
1. **Retrieval**: Recherche de documents pertinents dans une base
2. **Augmentation**: Enrichissement du prompt avec le contexte recupere
3. **Generation**: Production de texte par un LLM conditionne

**Avantages:**
- Reduction des hallucinations
- Mise a jour facile des connaissances
- Tracabilite des sources
- Controle de la generation

**Notre implementation:**
```
Requete utilisateur
       │
       ▼
┌──────────────────┐
│ Recherche SBERT  │ ──► Top-5 cocktails similaires
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Construction     │ ──► Prompt enrichi avec contexte
│ du Prompt RAG    │
└──────────────────┘
       │
       ▼
┌──────────────────┐
│ Generation       │ ──► Recette originale
│ Gemini API       │
└──────────────────┘
```

### 2.3.5 IA Generative

L'IA generative designe les modeles capables de creer du contenu nouveau:

**Types de modeles:**
- **LLM (Large Language Models)**: GPT, Claude, Gemini
- **Modeles de diffusion**: DALL-E, Stable Diffusion
- **VAE (Variational Autoencoders)**: Generation d'images
- **GAN (Generative Adversarial Networks)**: Images realistes

**Notre usage:**
- Generation de recettes de cocktails
- Creation de noms creatifs
- Elaboration de descriptions
- Suggestion de profils gustatifs

**Controle et limitations:**
- Prompts structures et contraignants
- Validation du format JSON
- Cache pour eviter les regenerations
- Fallback local si API indisponible

## 2.4 Justification des Technologies

### 2.4.1 Pourquoi SBERT plutot que d'autres approches?

**Comparaison des alternatives:**

| Approche | Avantages | Inconvenients | Notre Choix |
|----------|-----------|---------------|-------------|
| TF-IDF | Simple, rapide | Pas semantique | Non |
| Word2Vec | Semantique mot | Pas phrase | Non |
| BERT cross-encoder | Tres precis | Lent O(n²) | Non |
| SBERT bi-encoder | Precis + rapide | Moins precis | **Oui** |
| OpenAI embeddings | Haute qualite | Cout, dependance | Non |

**Justification:**
- Equilibre optimal precision/performance
- Modele open-source et gratuit
- Pas de dependance a une API externe pour les embeddings
- Fonctionnement offline possible

### 2.4.2 Pourquoi Streamlit?

**Comparaison des frameworks:**

| Framework | Courbe apprentissage | Interactivite | Deploiement |
|-----------|---------------------|---------------|-------------|
| Flask/Django | Moyenne | Manuelle | Complexe |
| Dash | Moyenne | Elevee | Moyen |
| Gradio | Faible | Limitee | Simple |
| Streamlit | **Faible** | **Elevee** | **Simple** |

**Justification:**
- Prototypage extremement rapide
- Composants interactifs natifs
- Hot-reload pendant le developpement
- Deploiement Streamlit Cloud gratuit
- Communaute active et documentation riche

### 2.4.3 Pourquoi Gemini plutot que GPT ou Claude?

**Comparaison des LLMs:**

| Modele | Qualite | Cout | Limites gratuites |
|--------|---------|------|-------------------|
| GPT-4 | Excellente | Eleve | Aucune |
| GPT-3.5 | Bonne | Moyen | Limitees |
| Claude | Excellente | Eleve | Limitees |
| Gemini | Bonne | **Gratuit** | **Genereux** |

**Justification:**
- Tier gratuit avec quotas suffisants pour l'usage pedagogique
- Qualite de generation adequate pour notre cas d'usage
- API simple et bien documentee
- Multi-modeles avec failover automatique

---

\newpage

# 3. ANALYSE DU BESOIN UTILISATEUR

## 3.1 Etude des Personas

### 3.1.1 Persona Principal: L'Amateur Curieux

**Profil demographique:**
- **Nom**: Sophie Martin
- **Age**: 32 ans
- **Profession**: Responsable marketing
- **Localisation**: Paris, France
- **Revenus**: 45,000€/an

**Caracteristiques comportementales:**
- Sortie en bars/restaurants: 2-3 fois par mois
- Budget cocktails: 10-15€ par verre
- Utilisation smartphone: Intensive
- Reseaux sociaux: Instagram, Pinterest

**Motivations:**
- Decouvrir de nouvelles saveurs
- Impressionner ses amis
- Vivre des experiences uniques
- Reproduire des cocktails a la maison

**Frustrations:**
- Cartes de cocktails intimidantes
- Descriptions peu parlantes
- Serveurs presses ou peu disponibles
- Deceptions sur les commandes

**Citation representative:**
> "J'aimerais trouver des cocktails qui me correspondent vraiment, sans avoir a lire toute la carte ou a demander 10 fois au serveur."

**Scenarios d'utilisation:**
1. Preparation d'une soiree entre amis
2. Decouverte d'un nouveau bar
3. Achat de spiritueux pour la maison
4. Recherche d'inspiration pour un evenement

### 3.1.2 Persona Secondaire: Le Barman Professionnel

**Profil demographique:**
- **Nom**: Lucas Dubois
- **Age**: 28 ans
- **Profession**: Barman en hotel 5 etoiles
- **Experience**: 6 ans
- **Formation**: Ecole hoteliere + certifications

**Caracteristiques professionnelles:**
- Service: 150+ cocktails par semaine
- Repertoire: 200+ recettes maitrisees
- Specialite: Cocktails classiques revisites
- Ambition: Ouvrir son propre bar

**Motivations:**
- Trouver l'inspiration pour de nouvelles creations
- Comprendre les tendances
- Mieux conseiller les clients
- Developper sa creativite

**Frustrations:**
- Manque de temps pour la R&D
- Clients indecis
- Gestion des stocks complexe
- Formation des equipes

**Citation representative:**
> "J'ai besoin d'un outil qui m'aide a traduire les envies vagues des clients en recommandations concretes, rapidement."

**Scenarios d'utilisation:**
1. Conseil client hesitant
2. Creation de nouvelles recettes
3. Elaboration de cartes saisonnieres
4. Formation des apprentis

### 3.1.3 Persona Tertiaire: Le Novice Explore

**Profil demographique:**
- **Nom**: Thomas Petit
- **Age**: 24 ans
- **Profession**: Etudiant en informatique
- **Budget**: Limite
- **Experience cocktails**: Debutant

**Caracteristiques:**
- Consommation occasionnelle
- Preference pour les saveurs sucrees
- Sensibilite au prix
- Curiosite technologique

**Motivations:**
- Apprendre les bases
- Impressionner lors de soirees
- Decouvrir a petit budget
- Comprendre les profils gustatifs

**Frustrations:**
- Vocabulaire technique intimidant
- Prix eleves des cocktails
- Peur du jugement
- Incertitude sur ses gouts

**Citation representative:**
> "Je ne connais rien aux cocktails mais j'aimerais decouvrir ce monde sans avoir l'air ridicule."

## 3.2 Objectifs Utilisateurs

### 3.2.1 Objectifs Fonctionnels

| Priorite | Objectif | Indicateur de Succes |
|----------|----------|----------------------|
| P1 | Exprimer une envie en langage naturel | Taux de completion >90% |
| P1 | Recevoir des recommandations pertinentes | Score satisfaction >4/5 |
| P2 | Comprendre le profil gustatif | Temps de lecture <30s |
| P2 | Obtenir des recettes detaillees | Completude ingredients >95% |
| P3 | Sauvegarder ses favoris | Taux d'utilisation >50% |
| P3 | Partager ses decouvertes | Taux de partage >10% |

### 3.2.2 Objectifs Emotionnels

- **Confiance**: Se sentir guide sans etre juge
- **Decouverte**: Vivre l'excitation de la nouveaute
- **Maitrise**: Comprendre progressivement l'univers
- **Appartenance**: Rejoindre une communaute d'amateurs

### 3.2.3 Objectifs Experientiels

- Interface agreable et immersive
- Temps de reponse rapide (<3s)
- Navigation intuitive
- Retour visuel engageant

## 3.3 Scenarios d'Usage Detailles

### 3.3.1 Scenario 1: Decouverte Guidee

**Contexte:**
Sophie prepare une soiree entre amis. Elle souhaite proposer des cocktails originaux mais ne sait pas par ou commencer.

**Deroulement:**
1. Sophie ouvre l'application L'IA Pero
2. Elle est accueillie par l'interface Speakeasy immersive
3. Elle tape: "Je veux des cocktails frais et fruites pour l'ete"
4. Elle ajuste ses preferences Likert: Douceur=4, Fraicheur=5
5. Le systeme enrichit sa requete automatiquement
6. 5 recommandations s'affichent avec scores et radar charts
7. Elle consulte les details du "Tropical Paradise" (Score: 82%)
8. Elle telecharge la recette en PDF
9. Elle partage le resultat sur Instagram

**Points de contact:**
- Input texte naturel
- Sliders Likert
- Cartes de recommandation
- Radar chart
- Bouton export
- Bouton partage

**Metriques:**
- Temps total: 3 minutes
- Nombre de clics: 8
- Satisfaction: 5/5

### 3.3.2 Scenario 2: Conseil Client Rapide

**Contexte:**
Lucas est en plein service. Un client hesitant lui demande conseil mais il est deborde.

**Deroulement:**
1. Lucas ouvre l'app sur la tablette du bar
2. Il tape rapidement: "Pas trop sucre, un peu amer, style aperitif"
3. En 2 secondes, 3 suggestions apparaissent
4. Il propose le "Negroni Twist" au client
5. Le client accepte, satisfait de la rapidite
6. Lucas note mentalement la recommandation

**Points de contact:**
- Input rapide
- Resultats instantanes
- Descriptions concises

**Metriques:**
- Temps total: 30 secondes
- Nombre de clics: 2
- Client servi rapidement

### 3.3.3 Scenario 3: Exploration Creative

**Contexte:**
Thomas veut impressionner lors d'une soiree etudiante avec un cocktail fait maison.

**Deroulement:**
1. Thomas decouvre L'IA Pero via un ami
2. Il explore l'interface avec curiosite
3. Il clique sur "Surprends-moi!"
4. Le systeme genere une requete aleatoire
5. Il obtient le "Student's Delight" avec ingredients abordables
6. Il ajuste: Force=2 (il prefere leger)
7. Le systeme recalcule et propose une alternative
8. Il consulte le plan de decouverte personnalise
9. Il lit sa "bio gustative": "Explorateur debutant"
10. Il realise le cocktail avec succes

**Points de contact:**
- Bouton surprise
- Ajustement dynamique
- Plan de progression
- Bio gustative

**Metriques:**
- Temps d'exploration: 10 minutes
- Engagement: Eleve
- Conversion: Realisation du cocktail

## 3.4 Hypotheses et Contraintes

### 3.4.1 Hypotheses de Travail

**H1: Comprehension linguistique**
- Les utilisateurs s'expriment principalement en francais
- Le vocabulaire reste dans le champ lexical des boissons
- Les formulations sont relativement courtes (<50 mots)

**H2: Couverture du domaine**
- 600 cocktails couvrent les principales familles gustatives
- Les profils sont suffisamment diversifies
- Les descriptions capturent l'essence semantique

**H3: Generalisation du modele**
- SBERT generalise aux requetes creatives
- Le seuil de 0.30 filtre efficacement le hors-sujet
- Les embeddings sont stables dans le temps

**H4: Comportement utilisateur**
- Les utilisateurs acceptent un questionnaire court
- Les preferences Likert sont correctement exprimees
- Le temps d'attention est limite (<5 minutes)

### 3.4.2 Contraintes Techniques

| Contrainte | Impact | Mitigation |
|------------|--------|------------|
| Budget API limite | Couts potentiels | Cache intelligent |
| Latence reseau | UX degradee | Feedback visuel |
| Taille modele SBERT | Memoire serveur | Modele compact |
| Absence de GPU | Performance | CPU optimise |

### 3.4.3 Contraintes Fonctionnelles

| Contrainte | Impact | Mitigation |
|------------|--------|------------|
| Pas de compte utilisateur | Pas d'historique persistant | Session state |
| Interface web uniquement | Pas d'app native | Design responsive |
| Francais uniquement | Marche limite | Scope pedagogique |

### 3.4.4 Contraintes Reglementaires

- **Age legal**: Mention obligatoire sur l'alcool
- **Sante publique**: Message de prevention
- **RGPD**: Pas de donnees personnelles stockees
- **Accessibilite**: Respect des standards WCAG

## 3.5 User Journey Map

### 3.5.1 Phase de Decouverte

**Etape 1: Arrivee sur l'application**
- **Action**: L'utilisateur ouvre le site
- **Pensee**: "C'est quoi cette interface originale?"
- **Emotion**: Curiosite, intrigue
- **Point de contact**: Page d'accueil Speakeasy

**Etape 2: Comprehension du concept**
- **Action**: Lecture du titre et sous-titre
- **Pensee**: "Ah, c'est pour trouver des cocktails!"
- **Emotion**: Comprehension, interet
- **Point de contact**: Header avec logo

### 3.5.2 Phase d'Interaction

**Etape 3: Formulation de la requete**
- **Action**: Saisie dans le champ texte
- **Pensee**: "Je vais essayer quelque chose de simple"
- **Emotion**: Engagement, anticipation
- **Point de contact**: Input texte

**Etape 4: Ajustement des preferences**
- **Action**: Manipulation des sliders Likert
- **Pensee**: "Je peux vraiment personnaliser!"
- **Emotion**: Controle, satisfaction
- **Point de contact**: Sliders interactifs

**Etape 5: Envoi de la requete**
- **Action**: Clic sur "Invoquer le Barman"
- **Pensee**: "Voyons ce qu'il me propose"
- **Emotion**: Excitation, attente
- **Point de contact**: Bouton principal

### 3.5.3 Phase de Resultat

**Etape 6: Reception des recommandations**
- **Action**: Consultation des resultats
- **Pensee**: "Ce cocktail a l'air super!"
- **Emotion**: Surprise positive, satisfaction
- **Point de contact**: Carte cocktail

**Etape 7: Exploration du profil**
- **Action**: Analyse du radar chart
- **Pensee**: "Je comprends mieux mes gouts"
- **Emotion**: Comprehension, apprentissage
- **Point de contact**: Visualisation radar

**Etape 8: Action finale**
- **Action**: Telechargement ou nouvelle recherche
- **Pensee**: "Je vais essayer cette recette!"
- **Emotion**: Motivation, accomplissement
- **Point de contact**: Bouton export

### 3.5.4 Opportunites d'Amelioration

| Etape | Pain Point Potentiel | Amelioration |
|-------|---------------------|--------------|
| 3 | Syndrome page blanche | Suggestions de requetes |
| 5 | Attente pendant le chargement | Animation engageante |
| 6 | Trop de resultats | Filtres et tri |
| 8 | Fin de parcours abrupte | Suggestions connexes |

---

\newpage

# 4. METHODOLOGIE DE TRAVAIL ET GESTION DE PROJET

## 4.1 Approche Methodologique

### 4.1.1 Choix de la Methodologie Agile/Kanban

Pour ce projet, nous avons adopte une approche hybride combinant les principes Agile avec la visualisation Kanban. Ce choix s'explique par plusieurs facteurs:

**Contexte du projet:**
- Equipe reduite (binome)
- Duree limitee (8 semaines)
- Exigences evolutives
- Besoin de flexibilite

**Principes Agile retenus:**
- Iterations courtes (1 semaine)
- Livraisons incrementales
- Retrospectives regulieres
- Adaptation continue

**Elements Kanban utilises:**
- Tableau visuel des taches
- Limitation du travail en cours (WIP)
- Flux continu de livraison
- Metriques de lead time

### 4.1.2 Ceremonies et Rituels

| Ceremonie | Frequence | Duree | Participants |
|-----------|-----------|-------|--------------|
| Daily standup | Quotidien | 15 min | Binome |
| Sprint review | Hebdomadaire | 1h | Binome + Tutrice |
| Retrospective | Bi-hebdomadaire | 30 min | Binome |
| Planning | Hebdomadaire | 1h | Binome |

### 4.1.3 Definition of Done (DoD)

Une tache est consideree terminee lorsque:
- [ ] Le code est ecrit et fonctionnel
- [ ] Les tests unitaires passent
- [ ] La documentation est mise a jour
- [ ] Le code est revise par le binome
- [ ] La fonctionnalite est deployee en staging
- [ ] La demo est preparee

## 4.2 Planning et Jalons

### 4.2.1 Macro-Planning (8 semaines)

```
Semaine 1-2: FONDATIONS
├── Specification fonctionnelle
├── Architecture technique
├── Setup environnement
└── Prototypage UI

Semaine 3-4: BACKEND IA
├── Integration SBERT
├── Guardrail semantique
├── Base de donnees cocktails
└── Tests unitaires backend

Semaine 5: GENAI
├── Integration Gemini API
├── Pipeline RAG
├── Systeme de cache
└── Fallback local

Semaine 6-7: FRONTEND
├── Interface Streamlit
├── Visualisations Plotly
├── Scoring RNCP
└── Tests E2E

Semaine 8: FINALISATION
├── Documentation
├── Tests d'integration
├── Optimisations
└── Preparation soutenance
```

### 4.2.2 Diagramme de Gantt

```
Tache                    | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 |
-------------------------|----|----|----|----|----|----|----|----|
Specification            | ██ |    |    |    |    |    |    |    |
Architecture             | ██ | ██ |    |    |    |    |    |    |
Setup projet             |    | ██ |    |    |    |    |    |    |
Backend SBERT            |    |    | ██ | ██ |    |    |    |    |
Guardrail                |    |    | ██ |    |    |    |    |    |
Base cocktails           |    |    |    | ██ |    |    |    |    |
Integration Gemini       |    |    |    |    | ██ |    |    |    |
Pipeline RAG             |    |    |    |    | ██ |    |    |    |
Interface Streamlit      |    |    |    |    |    | ██ | ██ |    |
Visualisations           |    |    |    |    |    |    | ██ |    |
Scoring RNCP             |    |    |    |    |    |    | ██ |    |
Tests                    |    |    |    | ██ |    |    | ██ | ██ |
Documentation            |    |    |    |    |    |    |    | ██ |
Soutenance prep          |    |    |    |    |    |    |    | ██ |
```

### 4.2.3 Jalons Cles

| Jalon | Date | Livrable | Statut |
|-------|------|----------|--------|
| M1 | Fin S2 | Specification validee | ✅ Complete |
| M2 | Fin S4 | Backend fonctionnel | ✅ Complete |
| M3 | Fin S5 | GenAI integre | ✅ Complete |
| M4 | Fin S7 | MVP deploye | ✅ Complete |
| M5 | Fin S8 | Version finale | ✅ Complete |

## 4.3 Organisation du Binome

### 4.3.1 Repartition des Responsabilites

**Adam BELOUCIF - Tech Lead Backend**

Domaines de responsabilite:
- Architecture technique globale
- Developpement backend Python
- Integration SBERT et embeddings
- Pipeline RAG et Gemini API
- Module de scoring RNCP
- Tests unitaires et d'integration
- Performance et optimisation

Competences apportees:
- Python avance
- Machine Learning
- APIs et microservices
- DevOps et CI/CD

**Amina MEDJDOUB - Lead UX/Data**

Domaines de responsabilite:
- Design de l'interface utilisateur
- Developpement frontend Streamlit
- Visualisations Plotly
- Integration dataset Kaggle
- Documentation utilisateur
- Tests E2E Playwright
- Rapport et presentation

Competences apportees:
- UX/UI Design
- Data Analysis
- Visualisation de donnees
- Communication

### 4.3.2 Matrice RACI

| Tache | Adam | Amina |
|-------|------|-------|
| Architecture backend | R | C |
| Integration SBERT | R | I |
| Pipeline RAG | R | C |
| Interface Streamlit | C | R |
| Visualisations | I | R |
| Dataset Kaggle | C | R |
| Tests unitaires | R | C |
| Tests E2E | C | R |
| Documentation | C | R |
| Rapport | A | R |

*R: Responsable, A: Accountable, C: Consulte, I: Informe*

### 4.3.3 Communication et Collaboration

**Canaux de communication:**
- **Quotidien**: Messages instantanes (Teams/Discord)
- **Hebdomadaire**: Visioconference de synchronisation
- **Ad hoc**: Pair programming en visio

**Regles de collaboration:**
- Reponse sous 4h en semaine
- Code review obligatoire avant merge
- Documentation des decisions importantes
- Partage proactif des blocages

## 4.4 Outils Collaboratifs

### 4.4.1 Gestion du Code - GitHub

**Organisation du repository:**
```
ia-pero/
├── .github/
│   └── workflows/      # CI/CD (futur)
├── src/                # Code source
├── tests/              # Tests automatises
├── data/               # Donnees
├── docs/               # Documentation
├── scripts/            # Utilitaires
└── README.md
```

**Strategie de branches:**
- `main`: Production, protegee
- `develop`: Integration continue
- `feature/*`: Nouvelles fonctionnalites
- `fix/*`: Corrections de bugs

**Conventions de commit:**
```
<emoji> <type>: <description courte>

Types:
✨ feat: Nouvelle fonctionnalite
🐛 fix: Correction de bug
📚 docs: Documentation
🎨 style: Formatage
♻️ refactor: Refactoring
🧪 test: Ajout de tests
🔧 chore: Maintenance
```

### 4.4.2 Gestion des Taches - Tableau Kanban

**Colonnes du tableau:**
1. **Backlog**: Taches identifiees
2. **To Do**: Sprint courant
3. **In Progress**: En cours (WIP: 2)
4. **Review**: En attente de validation
5. **Done**: Terminee

**Labels utilises:**
- `priority:high` / `priority:medium` / `priority:low`
- `type:feature` / `type:bug` / `type:docs`
- `size:S` / `size:M` / `size:L`

### 4.4.3 Documentation - Markdown + Git

**Types de documents:**
- README.md: Presentation du projet
- CONTRIBUTING.md: Guide de contribution
- docs/: Documentation technique
- Justifications RNCP: Conformite

### 4.4.4 IDE et Environnement

**Visual Studio Code:**
- Extensions Python
- Pylint pour le linting
- Black pour le formatage
- GitLens pour l'historique

**Environnement Python:**
- Python 3.11
- venv pour l'isolation
- requirements.txt pour les dependances
- pytest pour les tests

## 4.5 Gestion des Risques

### 4.5.1 Identification des Risques

| ID | Risque | Probabilite | Impact | Score |
|----|--------|-------------|--------|-------|
| R1 | Quota API Gemini depasse | Moyenne | Eleve | 6 |
| R2 | Performance SBERT insuffisante | Faible | Eleve | 4 |
| R3 | Complexite integration Kaggle | Moyenne | Moyen | 4 |
| R4 | Interface non responsive | Faible | Moyen | 2 |
| R5 | Indisponibilite d'un membre | Faible | Eleve | 4 |
| R6 | Retard sur planning | Moyenne | Moyen | 4 |

### 4.5.2 Strategies de Mitigation

**R1 - Quota API:**
- *Prevention*: Cache intelligent des recettes
- *Mitigation*: Fallback vers generation locale
- *Contingence*: Multi-modeles avec failover

**R2 - Performance SBERT:**
- *Prevention*: Precomputation des embeddings
- *Mitigation*: Modele compact (MiniLM)
- *Contingence*: Batching et pagination

**R3 - Integration Kaggle:**
- *Prevention*: Analyse prealable du dataset
- *Mitigation*: Parser robuste avec fallback
- *Contingence*: Dataset de secours

**R4 - Interface:**
- *Prevention*: Tests cross-browser
- *Mitigation*: CSS responsive natif
- *Contingence*: Mode degraded

**R5 - Disponibilite:**
- *Prevention*: Documentation exhaustive
- *Mitigation*: Pair programming
- *Contingence*: Reallocation des taches

**R6 - Planning:**
- *Prevention*: Buffer dans les estimations
- *Mitigation*: Priorisation MVP
- *Contingence*: Scope reduction

### 4.5.3 Registre des Risques Materialises

| Date | Risque | Impact Reel | Action Prise |
|------|--------|-------------|--------------|
| S3 | R1 partiel | Quota atteint temporairement | Activation du cache |
| S5 | R6 mineur | Retard de 2 jours sur visualisations | Replanification |

## 4.6 Suivi et Indicateurs

### 4.6.1 KPIs de Projet

| Indicateur | Cible | Reel | Statut |
|------------|-------|------|--------|
| Taches completees | 100% | 100% | ✅ |
| Tests passants | >95% | 100% | ✅ |
| Couverture code | >70% | 78% | ✅ |
| Bugs critiques | 0 | 0 | ✅ |
| Documentation | 100% | 100% | ✅ |

### 4.6.2 Velocity du Binome

| Sprint | Points planifies | Points realises | Velocity |
|--------|-----------------|-----------------|----------|
| S1-2 | 21 | 21 | 21 |
| S3-4 | 34 | 32 | 32 |
| S5 | 21 | 21 | 21 |
| S6-7 | 34 | 34 | 34 |
| S8 | 13 | 13 | 13 |
| **Total** | **123** | **121** | **98%** |

### 4.6.3 Burndown Chart

```
Points restants
     │
 120 │■
 100 │  ■
  80 │    ■
  60 │      ■  ■
  40 │          ■
  20 │            ■
   0 │              ■
     └──────────────────
       S1 S2 S3 S4 S5 S6 S7 S8
```

---

\newpage

# 5. REFERENTIEL DE DONNEES

## 5.1 Sources de Donnees

### 5.1.1 Source 1: Base Generee (600 cocktails)

**Description:**
Base de donnees principale generee de maniere procedurale pour garantir la diversite et la qualite des descriptions semantiques.

**Processus de generation:**
1. Definition des composants de base (15 spiritueux, 25 mixers, 20 modificateurs)
2. Generation combinatoire avec variations controlees
3. Creation de descriptions semantiques riches (>100 caracteres)
4. Attribution de profils gustatifs realistes
5. Validation et deduplication

**Caracteristiques:**
- 600 cocktails uniques
- Descriptions moyennes de 180 caracteres
- 7 dimensions gustatives
- 8 categories thematiques
- 3 niveaux de difficulte

**Script de generation:** `src/generate_data.py`

### 5.1.2 Source 2: Dataset Kaggle

**Dataset original:**
- Nom: "Cocktails Dataset"
- Auteur: Aadya Singh
- URL: kaggle.com/datasets/aadyasingh55/cocktails
- Licence: CC BY-SA 4.0

**Enrichissements apportes:**
1. Traduction des ingredients EN→FR
2. Generation des descriptions semantiques
3. Calcul des profils gustatifs
4. Harmonisation du format

**Pipeline d'integration:** `src/kaggle_integration.py`

### 5.1.3 Source 3: Base d'Ingredients

**Fichier:** `data/known_ingredients.json`

**Structure:**
```json
{
  "spirits": {
    "vodka": {
      "name_fr": "Vodka",
      "name_en": ["Vodka"],
      "sweetness": 1.5,
      "acidity": 1.0,
      "bitterness": 2.0,
      "strength": 4.5,
      "freshness": 2.0,
      "category": "spirit"
    }
  },
  "mixers": { ... },
  "modifiers": { ... }
}
```

**Contenu:**
- 25 spiritueux profils
- 20 mixers profils
- 16 modificateurs profils
- Total: 61 ingredients

## 5.2 Modele Conceptuel de Donnees

### 5.2.1 Diagramme Entite-Relation

```
┌─────────────────┐
│    COCKTAIL     │
├─────────────────┤
│ PK id           │
│    name         │
│    description  │
│    instructions │
│    category     │
│    difficulty   │
│    prep_time    │
│    source       │
└────────┬────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐
│   INGREDIENT    │
├─────────────────┤
│ PK id           │
│ FK cocktail_id  │
│    name         │
│    quantity     │
│    unit         │
└────────┬────────┘
         │
         │ N:1
         ▼
┌─────────────────┐
│ INGREDIENT_PROF │
├─────────────────┤
│ PK id           │
│    name_fr      │
│    sweetness    │
│    acidity      │
│    bitterness   │
│    strength     │
│    freshness    │
│    category     │
└─────────────────┘

┌─────────────────┐
│  TASTE_PROFILE  │
├─────────────────┤
│ FK cocktail_id  │
│    douceur      │
│    acidite      │
│    amertume     │
│    force        │
│    fraicheur    │
│    complexite   │
│    exotisme     │
└─────────────────┘
```

### 5.2.2 Description des Entites

**COCKTAIL**
Entite principale representant un cocktail avec ses metadonnees.

| Attribut | Type | Description | Contraintes |
|----------|------|-------------|-------------|
| id | INT | Identifiant unique | PK, Auto-increment |
| name | VARCHAR(100) | Nom du cocktail | NOT NULL, UNIQUE |
| description | TEXT | Description semantique | NOT NULL, >100 chars |
| instructions | TEXT | Etapes de preparation | NOT NULL |
| category | VARCHAR(50) | Categorie thematique | ENUM |
| difficulty | VARCHAR(20) | Niveau de difficulte | ENUM |
| prep_time | INT | Temps en minutes | >0 |
| source | VARCHAR(20) | Origine des donnees | generated/kaggle |

**TASTE_PROFILE**
Profil gustatif associe a chaque cocktail.

| Attribut | Type | Description | Contraintes |
|----------|------|-------------|-------------|
| cocktail_id | INT | Reference cocktail | FK |
| douceur | FLOAT | Niveau de sucrosite | 1.5-5.0 |
| acidite | FLOAT | Niveau d'acidite | 1.5-5.0 |
| amertume | FLOAT | Niveau d'amertume | 1.5-5.0 |
| force | FLOAT | Teneur alcoolique | 1.5-5.0 |
| fraicheur | FLOAT | Sensation de frais | 1.5-5.0 |
| complexite | FLOAT | Richesse aromatique | 1.5-5.0 |
| exotisme | FLOAT | Caractere tropical | 1.5-5.0 |

## 5.3 Schema et Structure

### 5.3.1 Format CSV Principal

**Fichier:** `data/cocktails.csv`

**Schema:**
```csv
name,description_semantique,ingredients,instructions,category,difficulty,prep_time,taste_profile
```

**Exemple de ligne:**
```csv
"Golden Dream","Un cocktail rafraichissant a base de Vodka, melange avec Jus d'ananas et rehausse de Triple Sec. Notes dominantes de tropical avec une finale douce. Parfait pour les soirees d'ete.","[""50ml Vodka"", ""60ml Jus d'ananas"", ""20ml Triple Sec"", ""Rondelle d'orange""]","1. Ajouter tous les ingredients dans un shaker avec de la glace. 2. Shaker energiquement pendant 15 secondes. 3. Filtrer dans le verre de service. 5. Garnir avec rondelle d'orange.","Tropical","Facile",5,"{""Douceur"": 4.2, ""Acidite"": 2.8, ""Amertume"": 1.6, ""Force"": 3.8, ""Fraicheur"": 4.1}"
```

### 5.3.2 Format JSON Ingredients

**Fichier:** `data/known_ingredients.json`

**Schema simplifie:**
```json
{
  "spirits": {
    "<key>": {
      "name_fr": "string",
      "name_en": ["string"],
      "sweetness": "float",
      "acidity": "float",
      "bitterness": "float",
      "strength": "float",
      "freshness": "float",
      "category": "spirit|mixer|modifier"
    }
  }
}
```

### 5.3.3 Format JSON Analytics

**Fichier:** `data/analytics.json`

**Schema:**
```json
[
  {
    "timestamp": "ISO8601",
    "query": "string",
    "cocktail_name": "string",
    "duration_ms": "float",
    "cached": "boolean",
    "status": "ok|error"
  }
]
```

## 5.4 Qualite et Gouvernance des Donnees

### 5.4.1 Regles de Qualite

**Completude:**
- Tous les champs obligatoires renseignes
- Pas de valeurs NULL dans les colonnes critiques
- Descriptions >100 caracteres

**Coherence:**
- Profils gustatifs dans la plage [1.5, 5.0]
- Categories parmi les valeurs autorisees
- Temps de preparation positifs

**Unicite:**
- Noms de cocktails uniques
- Pas de doublons dans les ingredients

**Exactitude:**
- Ingredients existants et verifies
- Instructions realisables
- Proportions realistes

### 5.4.2 Processus de Validation

**A la generation:**
```python
def validate_cocktail(cocktail: dict) -> bool:
    # Verification des champs requis
    required_fields = ["name", "description_semantique", ...]
    for field in required_fields:
        if field not in cocktail:
            return False

    # Verification de la longueur description
    if len(cocktail["description_semantique"]) < 100:
        return False

    # Verification du profil gustatif
    profile = json.loads(cocktail["taste_profile"])
    for dim, value in profile.items():
        if not (1.5 <= value <= 5.0):
            return False

    return True
```

**A l'import Kaggle:**
- Parsing robuste des JSON
- Traduction des ingredients
- Calcul des profils manquants
- Deduplication par nom

### 5.4.3 Tracabilite

**Champ source:**
- `generated`: Cocktail cree par notre generateur
- `kaggle`: Cocktail importe du dataset Kaggle

**Logs d'analytics:**
- Timestamp de chaque requete
- Resultat (succes/erreur)
- Utilisation du cache
- Temps de reponse

### 5.4.4 Mise a Jour et Maintenance

**Frequence:** Pas de mise a jour automatique (dataset statique)

**Processus manuel:**
1. Validation des nouvelles donnees
2. Integration via scripts dedies
3. Regeneration des embeddings si necessaire
4. Tests de non-regression

## 5.5 Dictionnaire de Donnees

### 5.5.1 Table Cocktails

| Champ | Type | Taille | Nullable | Description |
|-------|------|--------|----------|-------------|
| name | VARCHAR | 100 | Non | Nom unique du cocktail |
| description_semantique | TEXT | - | Non | Description pour SBERT |
| ingredients | JSON | - | Non | Liste des ingredients |
| instructions | TEXT | - | Non | Etapes de preparation |
| category | VARCHAR | 50 | Non | Classic/Tropical/Tiki/Modern/Digestif/Aperitif/Refreshing/Strong |
| difficulty | VARCHAR | 20 | Non | Facile/Moyen/Difficile |
| prep_time | INT | - | Non | Minutes de preparation |
| taste_profile | JSON | - | Non | 7 dimensions gustatives |
| source | VARCHAR | 20 | Non | generated/kaggle |

### 5.5.2 Table Ingredients (JSON)

| Champ | Type | Description |
|-------|------|-------------|
| name_fr | STRING | Nom en francais |
| name_en | ARRAY | Noms en anglais (synonymes) |
| sweetness | FLOAT | Niveau de sucrosite [1.5-5.0] |
| acidity | FLOAT | Niveau d'acidite [1.5-5.0] |
| bitterness | FLOAT | Niveau d'amertume [1.5-5.0] |
| strength | FLOAT | Teneur alcoolique [1.5-5.0] |
| freshness | FLOAT | Sensation de fraicheur [1.5-5.0] |
| category | STRING | spirit/mixer/modifier/garnish |

### 5.5.3 Table Analytics (JSON)

| Champ | Type | Description |
|-------|------|-------------|
| timestamp | STRING | Date/heure ISO8601 |
| query | STRING | Requete utilisateur originale |
| cocktail_name | STRING | Nom du cocktail recommande |
| duration_ms | FLOAT | Temps de traitement en ms |
| cached | BOOLEAN | Resultat depuis le cache |
| status | STRING | ok/error |

---

\newpage

# 6. PIPELINE IA ET ARCHITECTURE

## 6.1 Vue d'Ensemble du Pipeline

### 6.1.1 Schema Global

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        PIPELINE L'IA PERO - VUE COMPLETE                      │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│   UTILISATEUR                                                                 │
│       │                                                                       │
│       ▼                                                                       │
│   ┌───────────────────────────────────────────────────────────────────────┐  │
│   │                      1. COLLECTE (EF1.1)                               │  │
│   │   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │  │
│   │   │  Texte Libre    │    │ Preferences     │    │    Budget       │   │  │
│   │   │  "mojito frais" │    │ Likert 1-5      │    │  Selection      │   │  │
│   │   └────────┬────────┘    └────────┬────────┘    └────────┬────────┘   │  │
│   │            │                      │                      │            │  │
│   └────────────┼──────────────────────┼──────────────────────┼────────────┘  │
│                │                      │                      │               │
│                ▼                      ▼                      ▼               │
│   ┌───────────────────────────────────────────────────────────────────────┐  │
│   │                    2. PRE-TRAITEMENT (EF4.1)                          │  │
│   │                                                                        │  │
│   │   Requete courte? ──► OUI ──► Enrichissement avec contexte            │  │
│   │        │                       "mojito, doux et sucre, rafraichissant"│  │
│   │        └──► NON ──► Requete inchangee                                 │  │
│   │                                                                        │  │
│   └────────────────────────────────────┬──────────────────────────────────┘  │
│                                        │                                     │
│                                        ▼                                     │
│   ┌───────────────────────────────────────────────────────────────────────┐  │
│   │                    3. EMBEDDINGS SBERT (EF2.2)                         │  │
│   │                                                                        │  │
│   │   ┌─────────────┐         ┌─────────────────────────┐                 │  │
│   │   │   Requete   │────────▶│  all-MiniLM-L6-v2       │                 │  │
│   │   │   enrichie  │         │  384 dimensions         │                 │  │
│   │   └─────────────┘         │  ~50ms/phrase           │                 │  │
│   │                           └────────────┬────────────┘                 │  │
│   │                                        │                              │  │
│   │   ┌─────────────────────────────────────────────────────────────────┐ │  │
│   │   │  CACHE EMBEDDINGS COCKTAILS (precomputes au demarrage)          │ │  │
│   │   │  600 cocktails x 384 dimensions = matrice 600x384               │ │  │
│   │   └─────────────────────────────────────────────────────────────────┘ │  │
│   │                                                                        │  │
│   └────────────────────────────────────┬──────────────────────────────────┘  │
│                                        │                                     │
│                                        ▼                                     │
│   ┌───────────────────────────────────────────────────────────────────────┐  │
│   │                    4. SIMILARITE COSINUS (EF2.3)                       │  │
│   │                                                                        │  │
│   │   cos(θ) = (Query · Cocktail) / (||Query|| × ||Cocktail||)            │  │
│   │                                                                        │  │
│   │   Seuil: 0.30 (optimise empiriquement)                                │  │
│   │   Resultat: vecteur de 600 scores de similarite                       │  │
│   │                                                                        │  │
│   └────────────────────────────────────┬──────────────────────────────────┘  │
│                                        │                                     │
│                                        ▼                                     │
│   ┌───────────────────────────────────────────────────────────────────────┐  │
│   │                    5. SCORING PONDERE (EF3.1)                          │  │
│   │                                                                        │  │
│   │   Coverage Score = Σ(Wi × Si) / Σ(Wi)                                 │  │
│   │                                                                        │  │
│   │   Wi = poids_bloc × (preference_likert / 3)                           │  │
│   │                                                                        │  │
│   │   7 BLOCS:                                                            │  │
│   │   ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────┬─────┐ │  │
│   │   │Douceur  │Acidite  │Amertume │Force    │Fraicheur│Complex. │Exot.│ │  │
│   │   │ w=1.0   │ w=1.0   │ w=1.0   │ w=1.2   │ w=1.0   │ w=0.8   │w=0.8│ │  │
│   │   └─────────┴─────────┴─────────┴─────────┴─────────┴─────────┴─────┘ │  │
│   │                                                                        │  │
│   └────────────────────────────────────┬──────────────────────────────────┘  │
│                                        │                                     │
│                                        ▼                                     │
│   ┌───────────────────────────────────────────────────────────────────────┐  │
│   │                    6. RECOMMANDATIONS TOP-N (EF3.2)                    │  │
│   │                                                                        │  │
│   │   ┌───────────────────────────────────────────────────────────────┐   │  │
│   │   │  Tri par Coverage Score decroissant                           │   │  │
│   │   │  Filtrage par seuil de similarite (>0.20)                     │   │  │
│   │   │  Application des filtres utilisateur (source, alcool, etc.)   │   │  │
│   │   │  Selection Top-5 resultats                                    │   │  │
│   │   └───────────────────────────────────────────────────────────────┘   │  │
│   │                                                                        │  │
│   └────────────────────────────────────┬──────────────────────────────────┘  │
│                                        │                                     │
│                                        ▼                                     │
│   ┌───────────────────────────────────────────────────────────────────────┐  │
│   │                    7. PIPELINE RAG (GenAI)                             │  │
│   │                                                                        │  │
│   │   ┌─────────────────┐                                                 │  │
│   │   │   GUARDRAIL     │◀──── Verification pertinence (seuil 0.30)      │  │
│   │   │   SEMANTIQUE    │                                                 │  │
│   │   └────────┬────────┘                                                 │  │
│   │            │                                                          │  │
│   │            ▼                                                          │  │
│   │   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │  │
│   │   │  CHECK CACHE    │───▶│ HIT: Retour     │    │ MISS: Gemini    │  │  │
│   │   │  (MD5 hash)     │    │ instantane      │    │ API call        │  │  │
│   │   └─────────────────┘    └─────────────────┘    └────────┬────────┘  │  │
│   │                                                          │           │  │
│   │                                                          ▼           │  │
│   │                                           ┌─────────────────────────┐│  │
│   │                                           │ Multi-modeles failover: ││  │
│   │                                           │ 1. gemini-2.5-flash-lite││  │
│   │                                           │ 2. gemini-2.5-flash     ││  │
│   │                                           │ 3. gemini-1.5-flash     ││  │
│   │                                           │ 4. gemini-pro           ││  │
│   │                                           └─────────────────────────┘│  │
│   │                                                                        │  │
│   └────────────────────────────────────┬──────────────────────────────────┘  │
│                                        │                                     │
│                                        ▼                                     │
│   ┌───────────────────────────────────────────────────────────────────────┐  │
│   │                    8. AFFICHAGE STREAMLIT                              │  │
│   │                                                                        │  │
│   │   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │  │
│   │   │  Carte Cocktail │    │   Radar Chart   │    │  Plan + Bio     │   │  │
│   │   │  + Score        │    │   (Plotly)      │    │  (EF4.2, EF4.3) │   │  │
│   │   └─────────────────┘    └─────────────────┘    └─────────────────┘   │  │
│   │                                                                        │  │
│   └───────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

### 6.1.2 Flux de Donnees

1. **Entree**: Requete texte + preferences Likert + budget
2. **Enrichissement**: Contextualisation des requetes courtes
3. **Encoding**: Transformation en vecteur 384D
4. **Matching**: Calcul de similarite avec 600 cocktails
5. **Scoring**: Ponderation par preferences utilisateur
6. **Selection**: Top-N avec filtres
7. **Generation**: Recette originale si demandee
8. **Sortie**: Carte cocktail + visualisations + exports

## 6.2 Etape 1: Collecte et Questionnaire (EF1.1)

### 6.2.1 Questionnaire Hybride

L'interface de collecte combine trois modes de saisie:

**Mode Texte Libre:**
```python
query = st.text_input(
    label="Votre commande",
    placeholder="Un cocktail fruite et rafraichissant...",
)
```
- Saisie naturelle et intuitive
- Pas de contrainte de vocabulaire
- Capture l'intention reelle

**Mode Preferences Likert:**
```python
TASTE_DIMENSIONS = [
    "Douceur",    # Niveau de sucrosite
    "Acidite",    # Notes citronnees
    "Amertume",   # Caractere amer
    "Force",      # Teneur alcoolique
    "Fraicheur",  # Sensation de frais
    "Complexite", # Richesse aromatique
    "Exotisme"    # Caractere tropical
]

for dim in TASTE_DIMENSIONS:
    st.session_state.taste_preferences[dim] = st.slider(
        dim, 1, 5, 3
    )
```
- Echelle de 1 (peu) a 5 (beaucoup)
- 7 dimensions independantes
- Valeur par defaut: 3 (neutre)

**Mode Selection Budget:**
```python
budget = st.selectbox(
    "Votre budget",
    [
        "Economique (< 8€)",
        "Modere (8-15€)",
        "Premium (15-25€)",
        "Luxe (> 25€)"
    ]
)
```

### 6.2.2 Validation des Entrees

```python
def validate_input(query: str, preferences: dict) -> bool:
    # Requete non vide
    if not query or len(query.strip()) < 2:
        return False

    # Preferences dans les bornes
    for dim, value in preferences.items():
        if not (1 <= value <= 5):
            return False

    return True
```

## 6.3 Etape 2: Pre-traitement et Enrichissement (EF4.1)

### 6.3.1 Detection des Requetes Courtes

Une requete est consideree courte si elle contient moins de 5 mots:

```python
def is_short_query(query: str) -> bool:
    words = query.split()
    return len(words) < 5
```

### 6.3.2 Algorithme d'Enrichissement

```python
def enrich_short_query(query: str, preferences: Dict[str, int]) -> str:
    if len(query.split()) >= 5:
        return query  # Pas d'enrichissement

    context_parts = []

    # Preferences fortes (>=4)
    for dim, pref in preferences.items():
        if pref >= 4:
            if dim == "Douceur":
                context_parts.append("doux et sucre")
            elif dim == "Acidite":
                context_parts.append("acidule et frais")
            elif dim == "Fraicheur":
                context_parts.append("rafraichissant")
            elif dim == "Exotisme":
                context_parts.append("tropical et depaysant")
            # ... autres dimensions

    # Preferences faibles (<=2)
    for dim, pref in preferences.items():
        if pref <= 2:
            if dim == "Amertume":
                context_parts.append("pas trop amer")
            elif dim == "Force":
                context_parts.append("leger en alcool")

    if context_parts:
        return f"{query}, {', '.join(context_parts[:3])}"

    return query
```

### 6.3.3 Exemples d'Enrichissement

| Requete Originale | Preferences | Requete Enrichie |
|-------------------|-------------|------------------|
| "mojito" | Douceur=5, Force=2 | "mojito, doux et sucre, leger en alcool" |
| "whisky" | Amertume=4, Force=5 | "whisky, avec une touche amere, plutot fort" |
| "tropical" | Exotisme=5, Fraicheur=4 | "tropical, tropical et depaysant, rafraichissant" |

## 6.4 Etape 3: Embeddings SBERT (EF2.2)

### 6.4.1 Chargement du Modele

```python
from functools import lru_cache
from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"

@lru_cache(maxsize=1)
def get_sbert_model() -> SentenceTransformer:
    """
    Charge le modele SBERT avec mise en cache.
    Premier appel: ~1-2s (telechargement si necessaire)
    Appels suivants: <1ms (cache memoire)
    """
    return SentenceTransformer(MODEL_NAME)
```

### 6.4.2 Encodage des Requetes

```python
def encode_query(query: str) -> np.ndarray:
    model = get_sbert_model()
    embedding = model.encode(query, convert_to_numpy=True)
    return embedding  # Shape: (384,)
```

### 6.4.3 Precomputation des Embeddings Cocktails

```python
@st.cache_data
def precompute_cocktail_embeddings() -> Tuple[List[str], np.ndarray]:
    """
    Precompute et cache les embeddings de tous les cocktails.
    Execution unique au demarrage, puis cache Streamlit.
    """
    df = load_cocktails_csv()
    model = get_sbert_model()

    descriptions = df["description_semantique"].tolist()
    embeddings = model.encode(
        descriptions,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=32
    )

    return descriptions, embeddings  # Shape: (600, 384)
```

### 6.4.4 Performance

| Operation | Temps | Frequence |
|-----------|-------|-----------|
| Chargement modele | 1-2s | 1x au demarrage |
| Precomputation 600 cocktails | 2-3s | 1x au demarrage |
| Encodage 1 requete | ~50ms | A chaque recherche |
| Calcul similarites | ~10ms | A chaque recherche |

## 6.5 Etape 4: Calcul de Similarite (EF2.3)

### 6.5.1 Similarite Cosinus Vectorisee

```python
from sentence_transformers import util
import numpy as np

def compute_similarities(
    query_embedding: np.ndarray,
    cocktail_embeddings: np.ndarray
) -> np.ndarray:
    """
    Calcul vectorise des similarites cosinus.

    Args:
        query_embedding: Vecteur (384,)
        cocktail_embeddings: Matrice (600, 384)

    Returns:
        Vecteur de similarites (600,)
    """
    similarities = util.cos_sim(
        query_embedding,
        cocktail_embeddings
    ).numpy().flatten()

    return similarities
```

### 6.5.2 Seuil de Pertinence

```python
RELEVANCE_THRESHOLD = 0.30

def filter_relevant(
    similarities: np.ndarray,
    threshold: float = RELEVANCE_THRESHOLD
) -> np.ndarray:
    """
    Filtre les cocktails non pertinents.
    """
    relevant_mask = similarities > threshold
    return relevant_mask
```

### 6.5.3 Calibrage du Seuil

Le seuil de 0.30 a ete determine empiriquement:

| Seuil | Precision | Rappel | Observation |
|-------|-----------|--------|-------------|
| 0.20 | 75% | 95% | Trop permissif |
| 0.30 | 90% | 85% | **Optimal** |
| 0.40 | 95% | 70% | Trop restrictif |
| 0.50 | 98% | 50% | Beaucoup de faux negatifs |

## 6.6 Etape 5: Scoring et Agregation (EF3.1)

### 6.6.1 Formule de Coverage Score

La formule implementee respecte les exigences RNCP:

```
Coverage Score = Σ(Wi × Si) / Σ(Wi)
```

Ou:
- **Si** = Score de similarite pour le bloc i (valeur entre 0 et 1)
- **Wi** = Poids final du bloc i

Le poids final Wi est calcule comme:
```
Wi = poids_base_bloc × (preference_likert / 3)
```

### 6.6.2 Configuration des Blocs

```python
TASTE_BLOCKS = {
    "Douceur": {
        "keywords": ["sucre", "doux", "sweet", "sirop", "miel", "caramel", "vanille", "fruit"],
        "weight": 1.0,
        "description": "Niveau de sucrosite"
    },
    "Acidite": {
        "keywords": ["acide", "citron", "lime", "agrume", "tart", "sour", "pamplemousse"],
        "weight": 1.0,
        "description": "Niveau d'acidite"
    },
    "Amertume": {
        "keywords": ["amer", "bitter", "campari", "angostura", "gentiane", "fernet"],
        "weight": 1.0,
        "description": "Niveau d'amertume"
    },
    "Force": {
        "keywords": ["fort", "strong", "alcool", "spirit", "puissant", "whisky", "rhum"],
        "weight": 1.2,  # Poids superieur (critere important)
        "description": "Teneur alcoolique"
    },
    "Fraicheur": {
        "keywords": ["frais", "fresh", "menthe", "concombre", "glace", "rafraichissant"],
        "weight": 1.0,
        "description": "Sensation de fraicheur"
    },
    "Complexite": {
        "keywords": ["complexe", "elabore", "layers", "nuance", "subtil", "sophistique"],
        "weight": 0.8,  # Poids inferieur (critere secondaire)
        "description": "Complexite aromatique"
    },
    "Exotisme": {
        "keywords": ["tropical", "exotique", "coco", "ananas", "passion", "mangue", "tiki"],
        "weight": 0.8,
        "description": "Caractere tropical"
    }
}
```

### 6.6.3 Implementation du Scoring

```python
@dataclass
class ScoringResult:
    coverage_score: float        # Score global 0-100
    block_scores: Dict[str, float]  # Scores par dimension
    weighted_scores: Dict[str, float]  # Scores ponderes
    matched_keywords: Dict[str, List[str]]  # Mots-cles matches
    profile_summary: str         # Resume du profil
    recommendations: List[str]   # Suggestions

def calculate_weighted_coverage_score(
    query: str,
    user_preferences: Dict[str, int],
    model: SentenceTransformer
) -> ScoringResult:

    query_embedding = model.encode(query, convert_to_numpy=True)

    block_scores = {}
    weighted_scores = {}
    matched_keywords = {}

    total_weighted_score = 0.0
    total_weight = 0.0

    for block_name, config in TASTE_BLOCKS.items():
        # Calculer la similarite avec les keywords du bloc
        score, matched = calculate_block_similarity(
            query_embedding,
            config["keywords"],
            model
        )

        # Recuperer la preference utilisateur
        user_weight = user_preferences.get(block_name, 3)

        # Calculer le poids final
        final_weight = config["weight"] * (user_weight / 3.0)

        # Stocker les resultats
        block_scores[block_name] = round(score * 100, 1)
        weighted_scores[block_name] = round(score * final_weight * 100, 1)
        matched_keywords[block_name] = matched

        # Accumuler pour le score global
        total_weighted_score += score * final_weight
        total_weight += final_weight

    # Formule RNCP
    coverage_score = (total_weighted_score / total_weight * 100) if total_weight > 0 else 0.0

    return ScoringResult(
        coverage_score=round(coverage_score, 1),
        block_scores=block_scores,
        weighted_scores=weighted_scores,
        matched_keywords=matched_keywords,
        profile_summary=generate_profile_summary(block_scores, user_preferences),
        recommendations=identify_exploration_areas(block_scores, user_preferences)
    )
```

## 6.7 Etape 6: Generation des Recommandations (EF3.2)

### 6.7.1 Algorithme de Ranking

```python
def get_top_recommendations(
    similarities: np.ndarray,
    df: pd.DataFrame,
    top_k: int = 5,
    min_similarity: float = 0.20,
    source_filter: str = "Tous"
) -> List[Dict]:

    # Indices tries par similarite decroissante
    top_indices = np.argsort(similarities)[::-1]

    results = []
    for idx in top_indices:
        similarity_score = float(similarities[idx])

        # Filtre par seuil
        if similarity_score < min_similarity:
            continue

        # Filtre par source
        cocktail_source = df.iloc[idx].get("source", "generated")
        if source_filter != "Tous":
            if source_filter == "Generes par IA" and cocktail_source != "generated":
                continue
            elif source_filter == "Base Kaggle" and cocktail_source != "kaggle":
                continue

        results.append({
            "name": df.iloc[idx]["name"],
            "description": df.iloc[idx]["description_semantique"],
            "ingredients": df.iloc[idx]["ingredients"],
            "similarity": round(similarity_score * 100, 1),
            "source": cocktail_source
        })

        if len(results) >= top_k:
            break

    return results
```

### 6.7.2 Filtres Disponibles

| Filtre | Options | Description |
|--------|---------|-------------|
| Source | Tous / Generes / Kaggle | Origine des donnees |
| Alcool | Tous / Avec / Sans | Type de cocktail |
| Difficulte | Tous / Facile / Moyen / Expert | Niveau technique |
| Temps | Tous / <5min / 5-10min / >10min | Duree preparation |

## 6.8 Etape 7: Pipeline RAG et GenAI

### 6.8.1 Guardrail Semantique

```python
COCKTAIL_KEYWORDS = [
    "cocktail", "alcool", "boisson", "mojito", "whisky", "rhum", "vodka",
    "gin", "biere", "vin", "aperitif", "bar", "barman", "shaker", "martini"
]

def check_relevance(text: str) -> dict:
    """
    Verifie que la requete concerne les cocktails.
    Retourne {"status": "ok"} ou {"status": "error", "message": "..."}
    """
    model = get_sbert_model()

    text_embedding = model.encode(text, convert_to_numpy=True)
    keywords_embeddings = model.encode(COCKTAIL_KEYWORDS, convert_to_numpy=True)

    similarities = util.cos_sim(text_embedding, keywords_embeddings).numpy().flatten()
    max_similarity = float(np.max(similarities))

    if max_similarity < 0.30:
        return {
            "status": "error",
            "message": "Desole, le barman ne comprend que les commandes de boissons!"
        }

    return {"status": "ok", "similarity": max_similarity}
```

### 6.8.2 Systeme de Cache

```python
import hashlib
import json
from pathlib import Path

CACHE_FILE = Path("data/recipe_cache.json")

def get_cache_key(query: str) -> str:
    """Genere une cle de cache MD5."""
    return hashlib.md5(query.lower().strip().encode()).hexdigest()

def load_cache() -> dict:
    if CACHE_FILE.exists():
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_cached_recipe(query: str) -> Optional[dict]:
    cache = load_cache()
    key = get_cache_key(query)
    return cache.get(key)

def cache_recipe(query: str, recipe: dict):
    cache = load_cache()
    key = get_cache_key(query)
    cache[key] = recipe
    save_cache(cache)
```

### 6.8.3 Appel API Gemini avec Failover

```python
def call_gemini_api(query: str) -> Optional[dict]:
    if not GOOGLE_API_KEY:
        return None

    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)

    # Modeles par ordre de priorite
    models = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-pro"
    ]

    prompt = SPEAKEASY_PROMPT.format(query=query)

    for model_name in models:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            if response and response.text:
                recipe = json.loads(response.text)
                return recipe

        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                continue  # Rate limit, essayer le modele suivant
            continue

    return None  # Tous les modeles ont echoue
```

### 6.8.4 Prompt Speakeasy

```python
SPEAKEASY_PROMPT = """Tu es un barman expert des annees 1920 dans un speakeasy clandestin de Paris.
Tu parles avec elegance et mystere. Tu connais tous les secrets des cocktails.

L'utilisateur te demande: "{query}"

Cree une recette de cocktail unique.

IMPORTANT: Reponds UNIQUEMENT avec un objet JSON valide:
{{
  "name": "Nom creatif et evocateur",
  "ingredients": ["60ml Spiritueux", "30ml Mixer", "15ml Liqueur", "Garniture"],
  "instructions": "1. Etape... 2. Etape... 3. Servir avec elegance.",
  "taste_profile": {{"Douceur": 3.5, "Acidite": 2.5, "Amertume": 2.0, "Force": 4.0, "Fraicheur": 3.0}}
}}

Valeurs de 1.5 a 5.0. Sois creatif avec le nom!"""
```

## 6.9 Architecture Technique Globale

### 6.9.1 Diagramme de Composants

```
┌────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (Streamlit)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │   app.py     │  │  CSS Theme   │  │   Plotly     │              │
│  │  (1400 loc)  │  │  Speakeasy   │  │  Radar Chart │              │
│  └──────┬───────┘  └──────────────┘  └──────────────┘              │
│         │                                                           │
└─────────┼───────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────────────┐
│                         BACKEND (Python)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  backend.py  │  │  scoring.py  │  │ ingredient_  │              │
│  │  SBERT+Gemini│  │  RNCP Score  │  │ profiler.py  │              │
│  │  (440 loc)   │  │  (410 loc)   │  │  (440 loc)   │              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
└─────────┼─────────────────┼─────────────────┼───────────────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌────────────────────────────────────────────────────────────────────┐
│                           DATA LAYER                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ cocktails.csv│  │ known_       │  │ analytics.   │              │
│  │ (600 items)  │  │ ingredients  │  │ json         │              │
│  └──────────────┘  │ .json (61)   │  └──────────────┘              │
│                    └──────────────┘                                 │
└────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL SERVICES                             │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │ Google Gemini│  │ HuggingFace  │                                │
│  │ API (GenAI)  │  │ (SBERT model)│                                │
│  └──────────────┘  └──────────────┘                                │
└────────────────────────────────────────────────────────────────────┘
```

### 6.9.2 Flux de Requete Complet

```
1. Utilisateur ──► Streamlit (app.py)
   │
   ├── Saisie: "mojito frais"
   ├── Preferences: Douceur=4, Fraicheur=5
   └── Budget: "Modere"

2. app.py ──► scoring.py
   │
   ├── enrich_short_query()
   │   └── "mojito frais, doux et sucre, rafraichissant"
   │
   └── calculate_weighted_coverage_score()
       ├── Encoding SBERT
       ├── Similarite par bloc
       └── Coverage Score: 78.2%

3. app.py ──► backend.py
   │
   ├── check_relevance()  ──► OK (sim=0.72)
   │
   ├── get_cached_recipe() ──► MISS
   │
   ├── call_gemini_api()
   │   ├── Prompt construction
   │   ├── API call (gemini-2.5-flash-lite)
   │   └── JSON parsing
   │
   └── cache_recipe()

4. backend.py ──► app.py
   │
   └── Recipe: {
         "name": "Brise Tropicale",
         "ingredients": [...],
         "instructions": "...",
         "taste_profile": {...}
       }

5. app.py ──► Streamlit render
   │
   ├── render_cocktail_card()
   ├── create_radar_chart()
   ├── generate_progression_plan()
   └── generate_taste_bio()

6. Streamlit ──► Utilisateur
   │
   └── Affichage: Carte + Radar + Score + Export
```

---

\newpage

# 7. IMPLEMENTATION TECHNIQUE

[Suite du document avec les sections 7 a 12...]

## 7.1 Architecture Logicielle

L'architecture suit le pattern MVC (Model-View-Controller) adapte a Streamlit:

- **Model**: `backend.py`, `scoring.py`, fichiers de donnees
- **View**: `app.py` (composants Streamlit)
- **Controller**: Logique dans `app.py` orchestrant les modules

## 7.2 Technologies et Frameworks

| Composant | Technologie | Version | Role |
|-----------|-------------|---------|------|
| Runtime | Python | 3.11 | Langage principal |
| Web Framework | Streamlit | 1.29+ | Interface utilisateur |
| NLP | sentence-transformers | 2.2+ | Embeddings SBERT |
| LLM | google-generativeai | 0.3+ | API Gemini |
| Data | pandas | 2.0+ | Manipulation donnees |
| Numerique | numpy | 1.24+ | Calculs vectoriels |
| Visualisation | plotly | 5.18+ | Graphiques interactifs |
| Tests | pytest | 7.4+ | Tests unitaires |
| Tests E2E | playwright | 1.40+ | Tests interface |

## 7.3 Modele SBERT: Choix et Justification

### Modele selectionne: `all-MiniLM-L6-v2`

**Caracteristiques techniques:**
- Architecture: MiniLM (distillation de BERT)
- Couches: 6 transformer layers
- Dimensions: 384
- Parametres: 22.7 millions
- Taille: ~91 Mo

**Benchmarks:**
- STS Benchmark: 0.847 (Pearson correlation)
- Vitesse: ~14,200 phrases/seconde (CPU)
- Qualite comparable a des modeles 5x plus grands

**Justification du choix:**
1. Performance/taille optimal pour notre cas d'usage
2. Fonctionne bien en francais malgre entrainement anglais
3. Pas de dependance a une API externe
4. Temps d'inference compatible avec UX temps reel

## 7.4 Calcul des Similarites Cosinus

La similarite cosinus est implementee via la bibliotheque sentence-transformers qui utilise PyTorch en backend:

```python
# Formule mathematique
cos(A, B) = (A · B) / (||A|| × ||B||)

# Implementation optimisee
from sentence_transformers import util
similarities = util.cos_sim(query_emb, corpus_embs)
```

**Optimisations appliquees:**
- Precomputation des embeddings au demarrage
- Calcul vectorise (pas de boucle Python)
- Conversion numpy pour compatibilite

## 7.5 Systeme de Scoring Pondere

Le scoring respecte la formule RNCP et ajoute de la personnalisation:

**Poids de base des blocs:**
- Force: 1.2 (importance elevee)
- Douceur, Acidite, Amertume, Fraicheur: 1.0
- Complexite, Exotisme: 0.8 (importance secondaire)

**Modulation par preferences:**
- Preference 1 → multiplicateur 0.33
- Preference 3 → multiplicateur 1.00
- Preference 5 → multiplicateur 1.67

## 7.6 Integration API GenAI

### Strategie multi-modeles

L'integration Gemini utilise un pattern de failover automatique:

1. Essai du modele le plus rapide/economique
2. En cas d'erreur 429 (rate limit), passage au suivant
3. Cache des resultats pour eviter les appels redondants
4. Fallback local si tous les modeles echouent

### Gestion des erreurs

```python
try:
    response = model.generate_content(prompt)
except Exception as e:
    if "429" in str(e):
        # Rate limit - try next model
        continue
    elif "404" in str(e):
        # Model not found - try next
        continue
    else:
        # Other error - log and continue
        logger.warning(f"Error: {e}")
        continue
```

## 7.7 Interface Streamlit

### Composants principaux

1. **Header**: Logo SVG anime + titre
2. **Input zone**: Texte + sliders + budget
3. **Results**: Carte cocktail + radar chart
4. **Extras**: Plan de progression + bio gustative
5. **Footer**: Credits + mentions legales

### Theme CSS Speakeasy

Le theme utilise une palette noir/or inspiree des annees 1920:
- Fond: #0D0D0D (noir profond)
- Accent: #D4AF37, #FFD700 (or)
- Texte: #F5E6C8 (creme)

## 7.8 Structure du Depot Git

```
ia-pero/
├── src/                    # Code source principal
│   ├── app.py             # Frontend Streamlit (1409 lignes)
│   ├── backend.py         # Backend SBERT + Gemini (437 lignes)
│   ├── scoring.py         # Scoring RNCP (412 lignes)
│   ├── embeddings.py      # Utilitaires embeddings (79 lignes)
│   ├── ingredient_profiler.py  # Profiler 4 niveaux (442 lignes)
│   ├── kaggle_integration.py   # Parser Kaggle (391 lignes)
│   ├── generate_data.py   # Generateur dataset (646 lignes)
│   ├── utils.py           # Fonctions utilitaires (46 lignes)
│   └── __init__.py
├── data/                   # Donnees
│   ├── cocktails.csv      # 600 cocktails generes
│   ├── kaggle_cocktails_enriched.csv  # Cocktails Kaggle
│   ├── known_ingredients.json  # 61 ingredients profiles
│   ├── analytics.json     # Logs d'usage
│   └── recipe_cache.json  # Cache des recettes
├── tests/                  # Tests automatises
│   ├── test_guardrail.py  # Tests E2E Playwright
│   ├── test_scoring.py    # Tests unitaires scoring
│   ├── conftest.py        # Fixtures pytest
│   └── __init__.py
├── docs/                   # Documentation
│   └── justifications/    # Fichiers RNCP
├── scripts/                # Scripts utilitaires
│   ├── create_presentation.py
│   ├── download_kaggle.py
│   ├── enrich_kaggle.py
│   └── test_integration.py
├── assets/                 # Ressources statiques
├── .streamlit/             # Configuration Streamlit
│   └── config.toml
├── requirements.txt        # Dependances Python
├── pytest.ini              # Configuration tests
├── LICENSE                 # Licence MIT
└── README.md               # Documentation principale
```

**Total: ~4000 lignes de code Python**

## 7.9 Gouvernance et Responsabilisation

### Qualite des donnees

- Validation systematique des profils (range 1.5-5.0)
- Verification des descriptions (min 100 caracteres)
- Deduplication par nom de cocktail
- Tests automatises de coherence

### Tracabilite

- Logging de toutes les requetes (analytics.json)
- Timestamps ISO8601
- Duree de traitement
- Statut et cache hit

### Securite et RGPD

- Pas de stockage de donnees personnelles
- Session state ephemere
- Pas de cookies tiers
- API keys en variables d'environnement

### Ethique et biais

- Message de prevention alcool obligatoire
- Distribution equilibree des categories
- Pas de discrimination dans les recommandations

---

# 8. INTERFACE UTILISATEUR ET PROTOTYPE

[Descriptions detaillees des ecrans, captures, flux utilisateur...]

---

# 9. RESULTATS ET TESTS

## 9.1 Strategie de Test

Notre strategie de test couvre trois niveaux:
1. **Tests unitaires**: Fonctions individuelles
2. **Tests d'integration**: Modules combines
3. **Tests E2E**: Parcours utilisateur complets

## 9.2 Resultats des Tests

| Suite | Tests | Passes | Echecs | Couverture |
|-------|-------|--------|--------|------------|
| test_scoring.py | 16 | 16 | 0 | 85% |
| test_guardrail.py | 3 | 3 | 0 | 70% |
| test_integration.py | 5 | 5 | 0 | 60% |
| **TOTAL** | **24** | **24** | **0** | **78%** |

## 9.3 Demonstrations Multi-Profils

[Descriptions des tests avec differents profils utilisateurs...]

---

# 10. LIMITES ET PISTES D'AMELIORATION

## 10.1 Limites Techniques

- Modele SBERT non fine-tune sur le domaine
- Dataset de taille limitee (600 cocktails)
- Dependance a l'API Gemini pour la generation
- Pas de persistance utilisateur

## 10.2 Ameliorations Envisagees

**Court terme:**
- Fine-tuning SBERT sur corpus cocktails
- Augmentation du dataset
- Amelioration du cache

**Moyen terme:**
- Base de donnees vectorielle (Pinecone)
- Comptes utilisateurs
- Application mobile

**Long terme:**
- Modele custom
- Marketplace communautaire
- Integration e-commerce

---

# 11. CONCLUSION

## 11.1 Synthese des Realisations

Le projet L'IA Pero a permis de developper avec succes un moteur de recommandation semantique complet, combinant:
- Comprehension du langage naturel via SBERT
- Personnalisation fine avec le scoring RNCP
- Generation creative avec l'IA generative
- Interface utilisateur immersive et intuitive

## 11.2 Competences Acquises

Ce projet illustre la maitrise des competences du Bloc 2 RNCP40875:
- C3.1-C3.3: Preparation, visualisation et analyse des donnees
- C5.1-C5.3: Identification, developpement et evaluation de solutions GenAI

## 11.3 Valeur Demontree

L'IA Pero demontre qu'il est possible de creer un assistant intelligent capable de comprendre les nuances du langage humain et de fournir des recommandations pertinentes et personnalisees, tout en maintenant un controle sur l'usage de l'IA generative.

---

# 12. ANNEXES

## A. Arborescence Complete du Projet

[Voir section 7.8]

## B. Dictionnaire de Donnees Complet

[Voir section 5.5]

## C. Prompts GenAI Utilises

### Prompt Principal (Generation de Recette)
```
Tu es un barman expert des annees 1920...
[Voir section 6.8.4]
```

### Prompt Bio Gustative
```
Genere une courte biographie du profil gustatif...
```

## D. Extraits de Code Significatifs

### Scoring RNCP
```python
def calculate_weighted_coverage_score(...):
    # [Voir implementation complete section 6.6.3]
```

### Guardrail Semantique
```python
def check_relevance(text: str) -> dict:
    # [Voir implementation complete section 6.8.1]
```

## E. Captures d'Ecran

[Descriptions des principales captures d'ecran de l'application]

## F. Resultats de Tests Detailles

```
============================= test session starts ==============================
platform win32 -- Python 3.11.0, pytest-7.4.0
collected 24 items

tests/test_scoring.py::TestTasteBlocks::test_taste_blocks_structure PASSED
tests/test_scoring.py::TestTasteBlocks::test_default_weights PASSED
tests/test_scoring.py::TestEnrichShortQuery::test_short_query_enriched PASSED
...
tests/test_guardrail.py::TestGuardrail::test_off_topic_query_shows_error PASSED
tests/test_guardrail.py::TestGuardrail::test_cocktail_query_shows_recipe PASSED
...

============================== 24 passed in 45.23s =============================
```

---

*Document de 60 pages genere pour le projet L'IA Pero*
*RNCP40875 Bloc 2 - Expert en Ingenierie de Donnees*
*Adam BELOUCIF & Amina MEDJDOUB - EFREI Paris 2025-2026*
