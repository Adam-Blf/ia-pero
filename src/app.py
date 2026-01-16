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
    layout="centered",
    initial_sidebar_state="expanded",
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

/* ----- Sidebar Styling ----- */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0D0D0D 0%, #1A1A1A 100%);
    border-right: 1px solid rgba(212, 175, 55, 0.3);
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #D4AF37 !important;
    font-family: 'Playfair Display', serif !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #F5E6C8 !important;
    font-family: 'Cormorant Garamond', serif !important;
}

/* Sidebar selectbox styling */
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(26, 26, 26, 0.9) !important;
    border: 1px solid #D4AF37 !important;
    color: #F5E6C8 !important;
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
    """Initialize session state variables."""
    if "history" not in st.session_state:
        st.session_state.history = []
    if "metrics" not in st.session_state:
        st.session_state.metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "total_time": 0,
            "requests_today": 0,
        }
    if "selected_history" not in st.session_state:
        st.session_state.selected_history = None
    if "filters" not in st.session_state:
        st.session_state.filters = {
            "alcohol": "Tous",
            "difficulty": "Tous",
            "prep_time": "Tous",
        }


# =============================================================================
# ANALYTICS & LOGGING
# =============================================================================
def log_request(query: str, result: dict, duration: float, cached: bool):
    """Log request for analytics."""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "query": query,
        "cocktail_name": result.get("recipe", {}).get("name", "Unknown"),
        "duration_ms": round(duration * 1000, 2),
        "cached": cached,
        "status": result.get("status", "unknown"),
    }

    logger.info(f"REQUEST: {json.dumps(entry)}")

    # Update session metrics
    st.session_state.metrics["total_requests"] += 1
    st.session_state.metrics["total_time"] += duration
    if cached:
        st.session_state.metrics["cache_hits"] += 1

    # Save to file for persistence
    try:
        analytics = []
        if ANALYTICS_FILE.exists():
            with open(ANALYTICS_FILE, "r", encoding="utf-8") as f:
                analytics = json.load(f)
        analytics.append(entry)
        # Keep last 1000 entries
        analytics = analytics[-1000:]
        with open(ANALYTICS_FILE, "w", encoding="utf-8") as f:
            json.dump(analytics, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"Failed to save analytics: {e}")


def add_to_history(recipe: dict, query: str):
    """Add recipe to session history."""
    entry = {
        "name": recipe.get("name", "Cocktail Mystere"),
        "query": query,
        "timestamp": datetime.now().strftime("%H:%M"),
        "recipe": recipe,
    }
    st.session_state.history.insert(0, entry)
    # Keep last 10 items
    st.session_state.history = st.session_state.history[:10]


# =============================================================================
# SBERT SEARCH IN CSV
# =============================================================================
@st.cache_data
def load_cocktails_csv():
    """Load cocktails from CSV file."""
    if COCKTAILS_CSV.exists():
        return pd.read_csv(COCKTAILS_CSV)
    return pd.DataFrame()


def search_cocktails_sbert(query: str, top_k: int = 5) -> list:
    """
    Search cocktails in CSV using SBERT semantic similarity.

    Args:
        query: User search query
        top_k: Number of results to return

    Returns:
        List of matching cocktails with similarity scores
    """
    df = load_cocktails_csv()
    if df.empty:
        return []

    try:
        from sentence_transformers import util
        import numpy as np

        model = get_sbert_model()

        # Encode query
        query_embedding = model.encode(query, convert_to_numpy=True)

        # Encode all cocktail descriptions
        descriptions = df["description_semantique"].fillna("").tolist()
        desc_embeddings = model.encode(descriptions, convert_to_numpy=True)

        # Compute similarities
        similarities = util.cos_sim(query_embedding, desc_embeddings).numpy().flatten()

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.2:  # Minimum threshold
                results.append({
                    "name": df.iloc[idx]["name"],
                    "description": df.iloc[idx]["description_semantique"],
                    "ingredients": df.iloc[idx].get("ingredients", ""),
                    "similarity": round(float(similarities[idx]) * 100, 1),
                })

        return results
    except Exception as e:
        logger.error(f"SBERT search error: {e}")
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
# SIDEBAR COMPONENTS
# =============================================================================
def render_sidebar():
    """Render sidebar with history, filters, search, and metrics."""
    with st.sidebar:
        st.markdown("## 🥃 Le Carnet du Bar")

        # =========================
        # FILTERS SECTION
        # =========================
        st.markdown("### Filtres Avances")

        col1, col2 = st.columns(2)
        with col1:
            alcohol = st.selectbox(
                "Type",
                ["Tous", "Avec Alcool", "Sans Alcool"],
                key="filter_alcohol"
            )
        with col2:
            difficulty = st.selectbox(
                "Difficulte",
                ["Tous", "Facile", "Moyen", "Expert"],
                key="filter_difficulty"
            )

        prep_time = st.selectbox(
            "Temps de preparation",
            ["Tous", "< 5 min", "5-10 min", "> 10 min"],
            key="filter_prep_time"
        )

        st.session_state.filters = {
            "alcohol": alcohol,
            "difficulty": difficulty,
            "prep_time": prep_time,
        }

        st.divider()

        # =========================
        # SBERT SEARCH SECTION
        # =========================
        st.markdown("### Recherche dans la Cave")
        st.caption("600 cocktails indexes par SBERT")

        search_query = st.text_input(
            "Rechercher...",
            placeholder="mojito, tropical, amer...",
            key="sbert_search",
            label_visibility="collapsed"
        )

        if search_query:
            with st.spinner("Recherche semantique..."):
                results = search_cocktails_sbert(search_query, top_k=5)

            if results:
                for r in results:
                    with st.expander(f"**{r['name']}** ({r['similarity']}%)"):
                        st.write(r["description"][:200] + "...")
            else:
                st.caption("Aucun resultat trouve")

        st.divider()

        # =========================
        # HISTORY SECTION
        # =========================
        st.markdown("### Historique des Creations")

        if st.session_state.history:
            for i, item in enumerate(st.session_state.history[:5]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        f"🍸 {item['name'][:20]}...",
                        key=f"history_{i}",
                        use_container_width=True
                    ):
                        st.session_state.selected_history = item
                        st.rerun()
                with col2:
                    st.caption(item["timestamp"])
        else:
            st.caption("*Aucune creation encore...*")

        st.divider()

        # =========================
        # METRICS SECTION
        # =========================
        st.markdown("### Metriques de Session")

        metrics = st.session_state.metrics

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Requetes", metrics["total_requests"])
        with col2:
            cache_rate = 0
            if metrics["total_requests"] > 0:
                cache_rate = round(metrics["cache_hits"] / metrics["total_requests"] * 100)
            st.metric("Cache Hit", f"{cache_rate}%")

        avg_time = 0
        if metrics["total_requests"] > 0:
            avg_time = round(metrics["total_time"] / metrics["total_requests"] * 1000)
        st.metric("Temps moyen", f"{avg_time} ms")

        st.divider()

        # =========================
        # AMBIENT SOUND (Optional)
        # =========================
        st.markdown("### Ambiance Sonore")

        jazz_enabled = st.checkbox("Activer musique jazz", value=False, key="jazz_toggle")

        if jazz_enabled:
            st.markdown("""
                <audio autoplay loop>
                    <source src="https://stream.zeno.fm/0r0xa792kwzuv" type="audio/mpeg">
                </audio>
                <p style="font-size: 0.8rem; color: #666;">Radio Jazz en streaming</p>
            """, unsafe_allow_html=True)


# =============================================================================
# UI COMPONENTS
# =============================================================================
def render_header():
    """Render Speakeasy header with logo and title."""
    st.markdown("""
        <div class="speakeasy-header">
            <h1>L'IA Pero</h1>
            <p class="speakeasy-subtitle">~ Le Bar Secret ~</p>
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

    with st.container():
        # Header with cache badge and duration
        col1, col2 = st.columns([3, 1])
        with col1:
            if cached:
                st.markdown(f"## 🥃 {name} <small style='color: #D4AF37; font-size: 0.5em;'>Du Cellier</small>", unsafe_allow_html=True)
            else:
                st.markdown(f"## 🥃 {name}")
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

    # Render sidebar
    render_sidebar()

    # Render header
    render_header()

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
