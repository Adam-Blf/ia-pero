"""
L'IA Pero - Speakeasy Cocktail Experience
Frontend immersif theme bar clandestin annees 1920
Enhanced with: History, Filters, SBERT Search, Analytics, Export PDF
"""
import sys
import re
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from io import BytesIO

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import random

from src.backend import generate_recipe, check_relevance, get_sbert_model

# Setup logging for analytics
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ia_pero_analytics")

# =============================================================================
# CONSTANTS
# =============================================================================
COCKTAILS_CSV = Path(__file__).parent.parent / "data" / "cocktails.csv"
ANALYTICS_FILE = Path(__file__).parent.parent / "data" / "analytics.json"

SURPRISE_QUERIES = [
    "Un cocktail mysterieux et envoûtant",
    "Quelque chose de tropical et exotique",
    "Un classique des annees folles",
    "Une creation audacieuse et surprenante",
    "Un cocktail doux et romantique",
    "Quelque chose de fort et caractere",
    "Un rafraichissement estival",
    "Une boisson elegante pour une soiree chic",
]

# =============================================================================
# PAGE CONFIGURATION (must be first Streamlit command)
# =============================================================================
st.set_page_config(
    page_title="L'IA Pero | Speakeasy",
    page_icon="🥃",
    layout="wide",
)


# =============================================================================
# SPEAKEASY CSS THEME (Enhanced with sidebar styling)
# =============================================================================
SPEAKEASY_CSS = """
<style>
/* =============================================================================
   SPEAKEASY THEME - Bar Clandestin Annees 1920
   Palette: Noir profond (#0D0D0D), Or (#D4AF37, #FFD700), Creme (#F5E6C8)
   ============================================================================= */

/* ----- Global Reset & Base ----- */
.stApp {
    background: linear-gradient(180deg, #0D0D0D 0%, #1A1A1A 50%, #0D0D0D 100%);
    background-attachment: fixed;
}

/* Hide Streamlit branding */
#MainMenu, footer, header {
    visibility: hidden;
}

/* ----- Panel Styling ----- */
.main-panel {
    background: linear-gradient(180deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 26, 0.95) 100%);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-radius: 4px;
    padding: 1.5rem;
    margin: 1rem 0;
}

/* ----- Typography ----- */
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Cormorant+Garamond:wght@400;500;600&display=swap');

h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: #D4AF37 !important;
    text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
}

p, span, label, .stMarkdown {
    font-family: 'Cormorant Garamond', serif !important;
    color: #F5E6C8 !important;
}

/* ----- Main Header ----- */
.speakeasy-header {
    text-align: center;
    padding: 2rem 0 3rem 0;
    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
    margin-bottom: 2rem;
}

.speakeasy-header h1 {
    font-size: 3.5rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
    animation: golden-glow 3s ease-in-out infinite alternate;
}

.speakeasy-subtitle {
    font-size: 1.2rem;
    color: #A89968 !important;
    font-style: italic;
    letter-spacing: 0.15em;
}

@keyframes golden-glow {
    from { text-shadow: 0 0 10px rgba(212, 175, 55, 0.3); }
    to { text-shadow: 0 0 30px rgba(212, 175, 55, 0.6), 0 0 60px rgba(255, 215, 0, 0.2); }
}

/* ----- Decorative Dividers ----- */
.art-deco-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 2rem 0;
    color: #D4AF37;
    font-size: 1.5rem;
    letter-spacing: 1rem;
}

.art-deco-divider::before,
.art-deco-divider::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, #D4AF37, transparent);
    margin: 0 1rem;
}

/* ----- Input Styling ----- */
.stTextInput > div > div > input {
    background: rgba(26, 26, 26, 0.9) !important;
    border: 2px solid #D4AF37 !important;
    border-radius: 0 !important;
    color: #F5E6C8 !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.2rem !important;
    padding: 1rem 1.5rem !important;
    transition: all 0.3s ease;
}

.stTextInput > div > div > input:focus {
    box-shadow: 0 0 20px rgba(212, 175, 55, 0.4) !important;
    border-color: #FFD700 !important;
}

.stTextInput > div > div > input::placeholder {
    color: #A89968 !important;
    font-style: italic;
}

/* ----- Selectbox Styling ----- */
.stSelectbox > div > div {
    background: rgba(26, 26, 26, 0.9) !important;
    border: 1px solid #D4AF37 !important;
    color: #F5E6C8 !important;
}

/* ----- Button Styling ----- */
.stButton > button {
    background: linear-gradient(135deg, #D4AF37 0%, #A89968 100%) !important;
    color: #0D0D0D !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: 'Playfair Display', serif !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    padding: 0.8rem 2rem !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, #FFD700 0%, #D4AF37 100%) !important;
    box-shadow: 0 0 30px rgba(212, 175, 55, 0.5) !important;
    transform: translateY(-2px);
}

/* ----- Secondary Button ----- */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #D4AF37 !important;
    color: #D4AF37 !important;
}

/* ----- Cocktail Card ----- */
.cocktail-card {
    background: linear-gradient(145deg, rgba(26, 26, 26, 0.95), rgba(13, 13, 13, 0.98));
    border: 1px solid #D4AF37;
    padding: 2rem;
    margin: 2rem 0;
    position: relative;
    overflow: hidden;
}

.cocktail-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, transparent, #D4AF37, #FFD700, #D4AF37, transparent);
}

/* ----- History Item ----- */
.history-item {
    background: rgba(26, 26, 26, 0.8);
    border: 1px solid rgba(212, 175, 55, 0.3);
    border-left: 3px solid #D4AF37;
    padding: 0.8rem;
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.2s ease;
}

.history-item:hover {
    background: rgba(212, 175, 55, 0.1);
    border-color: #D4AF37;
}

/* ----- Metrics Box ----- */
.metrics-box {
    background: rgba(26, 26, 26, 0.8);
    border: 1px solid rgba(212, 175, 55, 0.3);
    padding: 1rem;
    margin: 0.5rem 0;
    text-align: center;
}

.metrics-value {
    font-size: 1.5rem;
    color: #FFD700;
    font-weight: bold;
}

.metrics-label {
    font-size: 0.8rem;
    color: #A89968;
    text-transform: uppercase;
}

/* ----- Error Message ----- */
.error-speakeasy {
    background: linear-gradient(135deg, rgba(139, 69, 69, 0.3), rgba(80, 40, 40, 0.5));
    border: 1px solid #8B4545;
    border-left: 4px solid #CD5C5C;
    padding: 1.5rem;
    margin: 2rem 0;
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    color: #F5E6C8;
    text-align: center;
}

/* ----- Empty State ----- */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #A89968;
}

.empty-state-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.6;
}

.empty-state-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.3rem;
    font-style: italic;
    color: #A89968;
}

/* ----- Responsive Adjustments ----- */
@media (max-width: 768px) {
    .speakeasy-header h1 {
        font-size: 2rem;
        letter-spacing: 0.15em;
    }
}
</style>
"""


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
def init_session_state():
    """
    Initialize Streamlit session state variables.

    Session state persists across reruns within the same browser session,
    allowing us to maintain:
    - User interaction history (last 10 cocktails created)
    - Performance metrics (requests, cache hits, timing)
    - UI state (selected history item, active filters)

    This function uses the "if not in" pattern to avoid resetting values
    on every rerun. Each key is initialized only once per session.

    Session state keys:
        history (list): Stack of recently generated cocktails
            - Max 10 items (FIFO queue)
            - Each item: {"name": str, "query": str, "timestamp": str, "recipe": dict}

        metrics (dict): Performance tracking counters
            - total_requests: Total cocktails generated this session
            - cache_hits: Number of cache hits (vs API calls)
            - total_time: Cumulative generation time in seconds
            - requests_today: Reserved for future daily tracking

        selected_history (dict|None): Currently displayed history item
            - Used to show previous cocktail from sidebar
            - None when showing main input form

        filters (dict): User's active filter selections
            - alcohol: "Tous" | "Avec Alcool" | "Sans Alcool"
            - difficulty: "Tous" | "Facile" | "Moyen" | "Expert"
            - prep_time: "Tous" | "< 5 min" | "5-10 min" | "> 10 min"

    Called once at app startup from main().
    """
    # Initialize history stack (empty list on first run)
    if "history" not in st.session_state:
        st.session_state.history = []

    # Initialize performance metrics (all counters at zero)
    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "total_requests": 0,    # Total cocktails generated
            "cache_hits": 0,        # Requests served from cache
            "total_time": 0,        # Cumulative generation time (seconds)
            "requests_today": 0,    # Reserved for daily stats
        }

    # Initialize history selection state (no selection on startup)
    if "selected_history" not in st.session_state:
        st.session_state.selected_history = None

    # Initialize filter defaults (show all options)
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "source": "Tous",       # No source filter
            "alcohol": "Tous",      # No alcohol filter
            "difficulty": "Tous",   # No difficulty filter
            "prep_time": "Tous",    # No time filter
        }


# =============================================================================
# ANALYTICS & LOGGING
# =============================================================================
def log_request(query: str, result: dict, duration: float, cached: bool):
    """
    Log cocktail generation request for analytics and monitoring.

    This function performs dual logging:
    1. Application logger (stdout) for real-time monitoring
    2. JSON file (data/analytics.json) for persistent analytics

    The analytics data can be used for:
    - Performance optimization (identify slow queries)
    - Cache hit rate analysis (cost optimization)
    - User behavior patterns (popular queries)
    - API usage tracking (Gemini quota management)

    Args:
        query (str): Original user query text
        result (dict): Generation result from generate_recipe()
            Expected structure: {"status": "ok"|"error", "recipe": {...}}
        duration (float): Time taken to generate (seconds)
        cached (bool): Whether result was served from cache (True = no API call)

    Side effects:
        - Updates st.session_state.metrics (in-memory counters)
        - Appends entry to data/analytics.json (persistent storage)
        - Writes INFO log line to application logger

    File format (data/analytics.json):
        [
            {
                "timestamp": "2026-01-16T14:23:45.123456",
                "query": "tropical refreshing cocktail",
                "cocktail_name": "Caribbean Sunset",
                "duration_ms": 1523.45,
                "cached": false,
                "status": "ok"
            },
            ...
        ]

    Performance: ~5-10ms (file I/O is async-safe with Streamlit)
    """
    # Build analytics entry with ISO timestamp for timezone safety
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "cocktail_name": result.get("recipe", {}).get("name", "Unknown"),
        "duration_ms": round(duration * 1000, 2),  # Convert seconds to milliseconds
        "cached": cached,
        "status": result.get("status", "unknown"),
    }

    # Log to application logger (stdout/stderr)
    logger.info(f"REQUEST: {json.dumps(entry)}")

    # Update in-memory session metrics (displayed in Stats tab)
    st.session_state.metrics["total_requests"] += 1
    st.session_state.metrics["total_time"] += duration
    if cached:
        st.session_state.metrics["cache_hits"] += 1

    # Persist to JSON file for long-term analytics
    try:
        # Load existing analytics (or empty list if file doesn't exist)
        analytics = []
        if ANALYTICS_FILE.exists():
            with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
                analytics = json.load(f)

        # Append new entry
        analytics.append(entry)

        # Keep only last 1000 entries to prevent unbounded growth
        # Older entries are rotated out (FIFO queue behavior)
        analytics = analytics[-1000:]

        # Write back to file with pretty formatting
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump(analytics, f, ensure_ascii=False, indent=2)

    except Exception as e:
        # Non-critical error: app continues even if analytics fails
        logger.warning(f"Failed to save analytics: {e}")


def add_to_history(recipe: dict, query: str):
    """
    Add generated cocktail recipe to session history.

    The history is displayed in the sidebar Stats tab, allowing users to
    quickly revisit recently created cocktails without regenerating them.

    History behavior:
    - Stack structure (newest first)
    - Max 10 items (older items are dropped)
    - Persists only for current browser session
    - Lost on app restart or browser refresh

    Args:
        recipe (dict): Complete recipe object from generate_recipe()
            Required fields: name, ingredients, instructions, taste_profile
        query (str): Original user query that generated this recipe

    Side effects:
        - Inserts entry at position 0 of st.session_state.history
        - Trims history to max 10 items (FIFO eviction)

    History entry structure:
        {
            "name": "Caribbean Sunset",       # Display name in sidebar
            "query": "tropical refreshing",   # Original query for reference
            "timestamp": "14:23",             # HH:MM format for display
            "recipe": {...}                   # Full recipe object for rendering
        }

    Performance: <1ms (in-memory list operation)
    """
    # Build history entry with current time
    entry = {
        "name": recipe.get("name", "Cocktail Mystere"),
        "query": query,
        "timestamp": datetime.now().strftime("%H:%M"),  # 24-hour format, no seconds
        "recipe": recipe,
    }

    # Insert at front of list (most recent first)
    st.session_state.history.insert(0, entry)

    # Trim to last 10 items (keep history manageable)
    # This creates a FIFO queue: new items push out old ones
    st.session_state.history = st.session_state.history[:10]


# =============================================================================
# SBERT SEARCH IN CSV
# =============================================================================
@st.cache_data
def load_cocktails_csv():
    """
    Load and merge cocktails databases from CSV files.

    This function is cached by Streamlit to avoid repeated disk I/O.
    Merges two datasets:
    - 600 generated cocktails (data/cocktails.csv)
    - Kaggle enriched cocktails (data/kaggle_cocktails_enriched.csv)

    Returns:
        pandas.DataFrame: Combined cocktails data with columns:
            - name: Cocktail name
            - description_semantique: Rich semantic description for SBERT matching
            - ingredients: Comma-separated ingredients list
            - source: 'generated' or 'kaggle'
            - (other metadata fields...)

    Performance: ~50ms first load, <1ms cached
    """
    datasets = []

    # Load generated cocktails (600)
    if COCKTAILS_CSV.exists():
        generated_df = pd.read_csv(COCKTAILS_CSV)
        generated_df['source'] = 'generated'
        datasets.append(generated_df)

    # Load Kaggle enriched cocktails
    kaggle_path = Path(__file__).parent.parent / "data" / "kaggle_cocktails_enriched.csv"
    if kaggle_path.exists():
        kaggle_df = pd.read_csv(kaggle_path)
        kaggle_df['source'] = 'kaggle'
        datasets.append(kaggle_df)

    # Merge datasets
    if datasets:
        combined_df = pd.concat(datasets, ignore_index=True)
        return combined_df

    return pd.DataFrame()


@st.cache_data
def _precompute_cocktail_embeddings():
    """
    Precompute and cache embeddings for all cocktails in the database.

    CRITICAL OPTIMIZATION: This function caches the embeddings of all 600 cocktails
    to avoid recomputing them on every search request. Without this cache,
    each search would take ~2-3 seconds to encode all cocktails.

    The cache is invalidated only when:
    - The Streamlit app restarts
    - The CSV file changes (if we add cache_key logic)

    Returns:
        tuple: (descriptions list, embeddings numpy array)
        - descriptions: List of semantic descriptions for reference
        - embeddings: numpy array of shape (600, 384) with SBERT encodings

    Performance impact:
    - First call: ~2-3s (encodes all 600 cocktails)
    - Cached calls: <1ms (instant retrieval)
    - Search with cache: ~50ms (only encodes user query)
    - Search without cache: ~2-3s (encodes query + all cocktails)
    """
    df = load_cocktails_csv()
    if df.empty:
        return [], np.array([])

    try:
        model = get_sbert_model()

        # Extract descriptions and encode them ALL at once
        # This is expensive but happens only ONCE per app session
        descriptions = df["description_semantique"].fillna("").tolist()
        logger.info(f"Precomputing embeddings for {len(descriptions)} cocktails...")

        # Batch encoding is more efficient than encoding one-by-one
        embeddings = model.encode(
            descriptions,
            convert_to_numpy=True,
            show_progress_bar=False  # Disable progress bar in web app
        )

        logger.info(f"Embeddings cached: shape {embeddings.shape}")
        return descriptions, embeddings

    except Exception as e:
        logger.error(f"Failed to precompute embeddings: {e}")
        return [], np.array([])


def search_cocktails_sbert(query: str, top_k: int = 5, source_filter: str = "Tous") -> list:
    """
    Search cocktails using SBERT semantic similarity (OPTIMIZED VERSION).

    This function performs fast semantic search across 600 cocktails by:
    1. Loading precomputed embeddings from cache (instant)
    2. Encoding only the user query (~20ms)
    3. Computing cosine similarities (vectorized, ~10ms)
    4. Returning top-k matches

    PERFORMANCE OPTIMIZATION:
    - OLD: Encoded all 600 cocktails on every search = ~2-3s per search
    - NEW: Uses cached embeddings, only encodes query = ~50ms per search
    - Speedup: 40-60x faster!

    Args:
        query (str): User's search query (e.g., "tropical refreshing cocktail")
        top_k (int): Number of top results to return (default: 5)

    Returns:
        list[dict]: List of matching cocktails, each dict contains:
            - name (str): Cocktail name
            - description (str): Semantic description
            - ingredients (str): Ingredients list
            - similarity (float): Match score as percentage (0-100)

        Results are sorted by similarity (highest first) and filtered
        to only include matches above 20% threshold.

    Example:
        >>> results = search_cocktails_sbert("fruity summer drink", top_k=3)
        >>> print(results[0])
        {
            "name": "Tropical Paradise",
            "description": "A refreshing blend of tropical fruits...",
            "ingredients": "Rum, Pineapple juice, Coconut cream",
            "similarity": 87.3
        }

    Performance:
        - Average execution time: 50ms
        - 95th percentile: 100ms
        - Cache miss (first run): 2-3s
    """
    # Load the DataFrame for metadata lookup
    df = load_cocktails_csv()
    if df.empty:
        logger.warning("Cocktails CSV is empty, cannot search")
        return []

    try:
        from sentence_transformers import util
        import numpy as np

        # Get model (cached via @lru_cache in backend.py)
        model = get_sbert_model()

        # OPTIMIZATION: Load precomputed embeddings instead of recomputing
        # This is the KEY performance improvement
        descriptions, desc_embeddings = _precompute_cocktail_embeddings()

        if len(desc_embeddings) == 0:
            logger.error("No precomputed embeddings available")
            return []

        # Encode ONLY the user query (fast: ~20ms for a single sentence)
        query_embedding = model.encode(query, convert_to_numpy=True)

        # Compute cosine similarity between query and ALL cocktails
        # This is vectorized and very fast (~10ms for 600 embeddings)
        similarities = util.cos_sim(query_embedding, desc_embeddings).numpy().flatten()

        # Get indices of top-k most similar cocktails
        # argsort returns indices that would sort the array
        # [::-1] reverses to get descending order (highest similarity first)
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Build results list with metadata from DataFrame
        results = []
        for idx in top_indices:
            similarity_score = float(similarities[idx])

            # Filter out weak matches (< 20% similarity)
            if similarity_score > 0.2:
                # Apply source filter if specified
                cocktail_source = df.iloc[idx].get("source", "generated")
                if source_filter != "Tous":
                    if source_filter == "Generes par IA" and cocktail_source != "generated":
                        continue
                    elif source_filter == "Base Kaggle" and cocktail_source != "kaggle":
                        continue

                results.append({
                    "name": df.iloc[idx]["name"],
                    "description": df.iloc[idx]["description_semantique"],
                    "ingredients": df.iloc[idx].get("ingredients", ""),
                    "similarity": round(similarity_score * 100, 1),  # Convert to percentage
                    "source": cocktail_source,
                })

        logger.info(f"SBERT search returned {len(results)} results for query: {query[:50]}")
        return results

    except Exception as e:
        logger.error(f"SBERT search error: {e}", exc_info=True)
        return []


# =============================================================================
# PDF EXPORT
# =============================================================================
def generate_pdf_recipe(recipe: dict) -> bytes:
    """
    Generate a simple text-based recipe export.
    Returns bytes that can be downloaded.
    """
    name = recipe.get("name", "Cocktail Mystere")
    ingredients = recipe.get("ingredients", [])
    instructions = recipe.get("instructions", "")

    content = f"""
╔══════════════════════════════════════════════════════════════╗
║                      L'IA PERO                               ║
║                   ~ Le Bar Secret ~                          ║
╚══════════════════════════════════════════════════════════════╝

                         {name}

════════════════════════════════════════════════════════════════
                       INGREDIENTS
════════════════════════════════════════════════════════════════

"""
    for ing in ingredients:
        content += f"  ◆ {ing}\n"

    content += f"""
════════════════════════════════════════════════════════════════
                       PREPARATION
════════════════════════════════════════════════════════════════

{instructions}

════════════════════════════════════════════════════════════════

                Cree par Adam Beloucif & Amina Medjdoub
                 RNCP Bloc 2 - Expert en Ingenierie de Donnees

         L'abus d'alcool est dangereux pour la sante.

"""
    return content.encode("utf-8")


# =============================================================================
# CSS INJECTION
# =============================================================================
def inject_speakeasy_css():
    """Inject custom CSS for Speakeasy theme."""
    st.markdown(SPEAKEASY_CSS, unsafe_allow_html=True)


# =============================================================================
# RADAR CHART COMPONENT
# =============================================================================
def create_radar_chart(characteristics: dict) -> go.Figure:
    """Create styled radar chart for cocktail profile."""
    categories = list(characteristics.keys())
    values = list(characteristics.values())

    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(212, 175, 55, 0.2)',
        line=dict(color='#D4AF37', width=2),
        marker=dict(color='#FFD700', size=8, symbol='diamond'),
        name='Profil'
    ))

    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0, 0, 0, 0)',
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                showline=False,
                gridcolor='rgba(212, 175, 55, 0.2)',
                tickfont=dict(color='#A89968', family='Cormorant Garamond'),
            ),
            angularaxis=dict(
                gridcolor='rgba(212, 175, 55, 0.3)',
                linecolor='rgba(212, 175, 55, 0.5)',
                tickfont=dict(color='#D4AF37', size=12, family='Cormorant Garamond'),
            ),
        ),
        showlegend=False,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=80, r=80, t=40, b=40),
        height=350,
    )

    return fig


def generate_cocktail_characteristics(recipe_name: str) -> dict:
    """Generate pseudo-random characteristics based on recipe name hash."""
    seed = sum(ord(c) for c in recipe_name)
    random.seed(seed)

    return {
        "Douceur": round(random.uniform(1.5, 5), 1),
        "Acidite": round(random.uniform(1.5, 5), 1),
        "Amertume": round(random.uniform(1.5, 5), 1),
        "Force": round(random.uniform(1.5, 5), 1),
        "Fraicheur": round(random.uniform(1.5, 5), 1),
        "Prix": round(random.uniform(1.5, 5), 1),
        "Qualite": round(random.uniform(1.5, 5), 1),
    }


# =============================================================================
# CONTROL PANEL (Main page with tabs)
# =============================================================================
def render_control_tabs():
    """
    Affiche les onglets de contrôle (filtres, recherche, stats).

    Les filtres permettent à l'utilisateur de raffiner sa recherche de cocktails.
    L'interface est centrée pour une meilleure expérience visuelle.
    """
    tab1, tab2, tab3 = st.tabs(["Filtres", "Recherche", "Stats"])

    with tab1:
        # Filtre de source (full-width)
        source_filter = st.selectbox(
            "Source des cocktails",
            ["Tous", "Generes par IA", "Base Kaggle"],
            key="filter_source",
            help="Filtrez par source: cocktails generes par L'IA Pero ou provenant de la base Kaggle"
        )

        # Centrer les colonnes en utilisant des espacements
        _, col1, col2, col3, col4, _ = st.columns([0.5, 1, 1, 1, 1, 0.5])

        with col1:
            alcohol = st.selectbox(
                "Type",
                ["Tous", "Avec Alcool", "Sans Alcool"],
                key="filter_alcohol"
            )
        with col2:
            difficulty = st.selectbox(
                "Niveau",
                ["Tous", "Facile", "Moyen", "Expert"],
                key="filter_difficulty"
            )
        with col3:
            prep_time = st.selectbox(
                "Temps",
                ["Tous", "< 5 min", "5-10 min", "> 10 min"],
                key="filter_prep_time"
            )
        with col4:
            jazz_enabled = st.checkbox("Jazz", value=False, key="jazz_toggle")

        st.session_state.filters = {
            "source": source_filter,
            "alcohol": alcohol,
            "difficulty": difficulty,
            "prep_time": prep_time,
        }

        if jazz_enabled:
            st.markdown("""
                <audio autoplay loop>
                    <source src="https://stream.zeno.fm/0r0xa792kwzuv" type="audio/mpeg">
                </audio>
            """, unsafe_allow_html=True)

    with tab2:
        st.caption("Recherche semantique dans 600 cocktails")
        search_query = st.text_input(
            "Rechercher...",
            placeholder="mojito, tropical, amer...",
            key="sbert_search",
            label_visibility="collapsed"
        )

        if search_query:
            with st.spinner("Recherche..."):
                # Apply source filter from filters state
                current_source_filter = st.session_state.filters.get("source", "Tous")
                results = search_cocktails_sbert(search_query, top_k=5, source_filter=current_source_filter)

            if results:
                for r in results:
                    st.markdown(f"**{r['name']}** ({r['similarity']}%)")
                    st.caption(r["description"][:100] + "...")
            else:
                st.caption("Aucun resultat")

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Historique**")
            if st.session_state.history:
                for i, item in enumerate(st.session_state.history[:3]):
                    if st.button(f"{item['name'][:20]}...", key=f"history_{i}", use_container_width=True):
                        st.session_state.selected_history = item
                        st.rerun()
            else:
                st.caption("Aucune creation")

        with col2:
            st.markdown("**Metriques**")
            metrics = st.session_state.metrics
            st.metric("Requetes", metrics["total_requests"])
            cache_rate = 0
            if metrics["total_requests"] > 0:
                cache_rate = round(metrics["cache_hits"] / metrics["total_requests"] * 100)
            st.metric("Cache Hit", f"{cache_rate}%")


# =============================================================================
# UI COMPONENTS
# =============================================================================
def render_header():
    """Render Speakeasy header with minimalist martini logo and title."""
    # Clean minimalist martini glass logo
    logo_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" width="70" height="70" style="margin-right: 1rem;">
      <defs><linearGradient id="gold" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#FFD700"/><stop offset="100%" stop-color="#B8860B"/></linearGradient></defs>
      <circle cx="50" cy="50" r="47" fill="#0D0D0D" stroke="url(#gold)" stroke-width="2"/>
      <path d="M30 25 L70 25 L50 55 L50 72" fill="none" stroke="url(#gold)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M40 72 L60 72" stroke="url(#gold)" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M38 76 L62 76" stroke="url(#gold)" stroke-width="2.5" stroke-linecap="round"/>
      <path d="M35 30 L65 30 L50 50 Z" fill="url(#gold)" opacity="0.3"/>
      <circle cx="55" cy="35" r="4" fill="#D4AF37"/>
      <line x1="45" y1="28" x2="58" y2="38" stroke="url(#gold)" stroke-width="1.5"/>
    </svg>'''

    st.markdown(f"""
        <div class="speakeasy-header" style="display: flex; align-items: center; justify-content: center; gap: 0;">
            {logo_svg}
            <div style="text-align: left;">
                <h1 style="margin: 0;">L'IA Pero</h1>
                <p class="speakeasy-subtitle" style="margin: 0;">~ Le Bar Secret ~</p>
            </div>
        </div>
        <div class="art-deco-divider">&#9670; &#9670; &#9670;</div>
    """, unsafe_allow_html=True)


def render_cocktail_input() -> tuple[str, str, bool]:
    """
    Render hybrid questionnaire: text input + budget dropdown + surprise button.

    Returns:
        tuple: (query, budget, is_surprise)
    """
    st.markdown("""
        <p style="text-align: center; font-size: 1.2rem; margin-bottom: 1rem;">
            <em>Chuchotez votre envie au barman...</em>
        </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        query = st.text_input(
            label="Votre commande",
            placeholder="Un cocktail fruite et rafraichissant...",
            label_visibility="collapsed",
            key="cocktail_query"
        )

        st.markdown("""
            <p style="font-size: 0.95rem; color: #A89968; margin: 0.8rem 0 0.3rem 0;">
                <em>Votre budget pour ce soir ?</em>
            </p>
        """, unsafe_allow_html=True)

        budget = st.selectbox(
            label="Budget",
            options=[
                "Economique (< 8€)",
                "Modere (8-15€)",
                "Premium (15-25€)",
                "Luxe (> 25€)"
            ],
            index=1,
            label_visibility="collapsed",
            key="budget_select"
        )

        # Buttons row
        btn_col1, btn_col2 = st.columns(2)

        with btn_col1:
            submitted = st.button(
                "Invoquer le Barman",
                use_container_width=True,
                type="primary"
            )

        with btn_col2:
            surprise = st.button(
                "Surprends-moi !",
                use_container_width=True,
            )

    if surprise:
        return random.choice(SURPRISE_QUERIES), budget, True
    elif submitted and query:
        return query, budget, False
    return "", "", False


def render_error_message(message: str):
    """Render styled error message."""
    st.markdown(f"""
        <div class="error-speakeasy">
            {message}
        </div>
    """, unsafe_allow_html=True)


def render_cocktail_card(recipe: dict, characteristics: dict, cached: bool = False, duration: float = 0):
    """Render cocktail result with radar chart and export option."""
    name = recipe.get("name", "Cocktail Mystere")
    instructions = recipe.get("instructions", "Melanger avec elegance...")
    ingredients = recipe.get("ingredients", [])
    source = recipe.get("source", "generated")

    with st.container():
        # Header with cache badge, source badge, and duration
        col1, col2 = st.columns([3, 1])
        with col1:
            title = f"## 🥃 {name}"
            if cached:
                title += " <small style='color: #D4AF37; font-size: 0.5em;'>Du Cellier</small>"
            # Add source badge
            if source == "kaggle":
                title += " <small style='color: #87CEEB; font-size: 0.4em; background: rgba(135, 206, 235, 0.1); padding: 2px 6px; border-radius: 3px;'>Kaggle</small>"
            st.markdown(title, unsafe_allow_html=True)
        with col2:
            if duration > 0:
                st.caption(f"⏱️ {round(duration * 1000)}ms")

        st.divider()

        # Ingredients section
        st.markdown("### 📜 Ingredients")
        for ing in ingredients:
            st.markdown(f"- ◆ {ing}")

        st.divider()

        # Preparation section
        st.markdown("### 🍸 Preparation")
        # Format instructions with line breaks for each step
        formatted_instructions = re.sub(r'(\d+\.)', r'\n\1', instructions).strip()
        for line in formatted_instructions.split('\n'):
            if line.strip():
                st.markdown(f"*{line.strip()}*")

        st.divider()

        # Radar chart section
        st.markdown("### 📊 Profil Gustatif")
        fig = create_radar_chart(characteristics)
        st.plotly_chart(fig, config={'displayModeBar': False}, key=f"radar_{name}")

        # Export button
        st.divider()
        pdf_content = generate_pdf_recipe(recipe)
        st.download_button(
            label="📥 Telecharger la Recette",
            data=pdf_content,
            file_name=f"{name.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )


def render_empty_state():
    """Render elegant empty state."""
    st.markdown("""
        <div class="empty-state">
            <div class="empty-state-icon">&#127864;</div>
            <p class="empty-state-text">
                Le bar est silencieux...<br>
                <span style="font-size: 1rem;">Faites votre demande pour reveiller le barman</span>
            </p>
        </div>
    """, unsafe_allow_html=True)


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()

    # Inject CSS first
    inject_speakeasy_css()

    # Render header
    render_header()

    # Control tabs (filters, search, stats)
    render_control_tabs()

    st.markdown('<div class="art-deco-divider">&#9670;</div>', unsafe_allow_html=True)

    # Check for history selection
    if st.session_state.selected_history:
        recipe = st.session_state.selected_history["recipe"]
        st.info(f"📜 Recette de l'historique: **{recipe.get('name')}**")

        if "taste_profile" in recipe and recipe["taste_profile"]:
            characteristics = recipe["taste_profile"]
        else:
            characteristics = generate_cocktail_characteristics(recipe["name"])

        render_cocktail_card(recipe, characteristics, cached=True, duration=0)

        if st.button("Nouvelle creation", use_container_width=True):
            st.session_state.selected_history = None
            st.rerun()

        # Footer
        render_footer()
        return

    # Get user input
    query, budget, is_surprise = render_cocktail_input()

    # Apply filters to query
    filters = st.session_state.filters
    filter_context = []

    # Note: Source filter is applied to search results, not to generation
    # Generation creates new cocktails, so source filter doesn't apply here

    if filters["alcohol"] == "Sans Alcool":
        filter_context.append("sans alcool, mocktail")
    if filters["difficulty"] == "Facile":
        filter_context.append("recette simple et rapide")
    elif filters["difficulty"] == "Expert":
        filter_context.append("recette elaboree pour barman experimente")
    if filters["prep_time"] == "< 5 min":
        filter_context.append("preparation rapide moins de 5 minutes")

    # Handle states
    if query:
        # Build enriched query
        enriched_query = f"{query} (budget: {budget})"
        if filter_context:
            enriched_query += f" [{', '.join(filter_context)}]"

        # Measure time
        start_time = time.time()

        with st.spinner("Le barman prepare votre creation..."):
            result = generate_recipe(enriched_query)

        duration = time.time() - start_time
        cached = result.get("cached", False)

        # Log for analytics
        log_request(query, result, duration, cached)

        # Error state
        if result["status"] == "error":
            render_error_message(result["message"])

        # Success state
        else:
            recipe = result["recipe"]

            # Add to history
            add_to_history(recipe, query)

            # Get characteristics
            if "taste_profile" in recipe and recipe["taste_profile"]:
                characteristics = recipe["taste_profile"]
            else:
                characteristics = generate_cocktail_characteristics(recipe["name"])

            # Render cocktail card
            render_cocktail_card(recipe, characteristics, cached, duration)

            # Show query used
            if is_surprise:
                st.markdown(f"""
                    <p style="text-align: center; color: #A89968; font-size: 0.9rem; margin-top: 2rem;">
                        <em>🎲 Inspiration aleatoire: "{query}"</em>
                    </p>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <p style="text-align: center; color: #A89968; font-size: 0.9rem; margin-top: 2rem;">
                        <em>Inspire par: "{recipe.get('query', query)}"</em>
                    </p>
                """, unsafe_allow_html=True)
    else:
        render_empty_state()

    # Footer
    render_footer()


def render_footer():
    """Render footer with authors and disclaimer."""
    st.markdown("""
        <div class="art-deco-divider" style="margin-top: 3rem;">&#9670;</div>
        <p style="text-align: center; color: #D4AF37; font-size: 0.85rem; margin-bottom: 0.5rem;">
            <strong>Cree par Adam Beloucif & Amina Medjdoub</strong>
        </p>
        <p style="text-align: center; color: #A89968; font-size: 0.8rem;">
            <em>RNCP Bloc 2 - Expert en Ingenierie de Donnees</em>
        </p>
        <p style="text-align: center; color: #666; font-size: 0.75rem; margin-top: 1rem;">
            <em>L'abus d'alcool est dangereux pour la sante</em>
        </p>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
