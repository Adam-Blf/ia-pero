"""
L'IA Pero - Speakeasy Cocktail Experience
Frontend immersif theme bar clandestin annees 1920
"""
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
import random

from src.backend import generate_recipe


# =============================================================================
# PAGE CONFIGURATION (must be first Streamlit command)
# =============================================================================
st.set_page_config(
    page_title="L'IA Pero | Speakeasy",
    page_icon="🥃",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# =============================================================================
# SPEAKEASY CSS THEME
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

.cocktail-name {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    color: #FFD700;
    text-align: center;
    margin-bottom: 1.5rem;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}

.cocktail-section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.1rem;
    color: #D4AF37;
    text-transform: uppercase;
    letter-spacing: 0.2em;
    margin: 1.5rem 0 0.8rem 0;
    padding-bottom: 0.3rem;
    border-bottom: 1px solid rgba(212, 175, 55, 0.3);
}

.ingredient-list {
    list-style: none;
    padding: 0;
    margin: 0;
}

.ingredient-item {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    color: #F5E6C8;
    padding: 0.4rem 0;
    padding-left: 1.5rem;
    position: relative;
}

.ingredient-item::before {
    content: '\\25C6';
    position: absolute;
    left: 0;
    color: #D4AF37;
    font-size: 0.6rem;
    top: 50%;
    transform: translateY(-50%);
}

.instructions-text {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.1rem;
    color: #F5E6C8;
    line-height: 1.8;
    font-style: italic;
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

/* ----- Spinner Customization ----- */
.stSpinner > div {
    border-color: #D4AF37 !important;
}

/* ----- Cached Badge ----- */
.cached-badge {
    display: inline-block;
    background: rgba(212, 175, 55, 0.2);
    border: 1px solid #D4AF37;
    color: #D4AF37;
    font-family: 'Cormorant Garamond', serif;
    font-size: 0.8rem;
    padding: 0.2rem 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-left: 1rem;
}

/* ----- Plotly Chart Container ----- */
.radar-container {
    background: transparent;
    padding: 1rem;
    margin: 1rem 0;
}

/* ----- Responsive Adjustments ----- */
@media (max-width: 768px) {
    .speakeasy-header h1 {
        font-size: 2rem;
        letter-spacing: 0.15em;
    }

    .cocktail-card {
        padding: 1rem;
    }
}
</style>
"""


# =============================================================================
# CSS INJECTION
# =============================================================================
def inject_speakeasy_css():
    """Inject custom CSS for Speakeasy theme."""
    st.markdown(SPEAKEASY_CSS, unsafe_allow_html=True)


# =============================================================================
# COCKTAIL CHARACTERISTICS (SIMULATED)
# =============================================================================
def generate_cocktail_characteristics(recipe_name: str) -> dict:
    """
    Generate pseudo-random characteristics based on recipe name hash.
    Uses name hash for reproducible values across sessions.
    """
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
# RADAR CHART COMPONENT
# =============================================================================
def create_radar_chart(characteristics: dict) -> go.Figure:
    """
    Create styled radar chart for cocktail profile.

    Args:
        characteristics: Dict with keys as category names and values as scores (1-5)

    Returns:
        Plotly Figure configured for Speakeasy theme
    """
    categories = list(characteristics.keys())
    values = list(characteristics.values())

    # Close the polygon by repeating first value
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]

    fig = go.Figure()

    # Add the radar trace
    fig.add_trace(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(212, 175, 55, 0.2)',
        line=dict(
            color='#D4AF37',
            width=2
        ),
        marker=dict(
            color='#FFD700',
            size=8,
            symbol='diamond'
        ),
        name='Profil'
    ))

    # Configure layout for dark theme
    fig.update_layout(
        polar=dict(
            bgcolor='rgba(0, 0, 0, 0)',
            radialaxis=dict(
                visible=True,
                range=[0, 5],
                showline=False,
                gridcolor='rgba(212, 175, 55, 0.2)',
                tickfont=dict(
                    color='#A89968',
                    family='Cormorant Garamond'
                ),
            ),
            angularaxis=dict(
                gridcolor='rgba(212, 175, 55, 0.3)',
                linecolor='rgba(212, 175, 55, 0.5)',
                tickfont=dict(
                    color='#D4AF37',
                    size=12,
                    family='Cormorant Garamond'
                ),
            ),
        ),
        showlegend=False,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        margin=dict(l=80, r=80, t=40, b=40),
        height=350,
    )

    return fig


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


def render_cocktail_input() -> tuple[str, str]:
    """
    Render hybrid questionnaire: text input + budget dropdown.

    Returns:
        tuple: (query, budget) - The user's cocktail request and selected budget
    """
    st.markdown("""
        <p style="text-align: center; font-size: 1.2rem; margin-bottom: 1rem;">
            <em>Chuchotez votre envie au barman...</em>
        </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        # Text input for free-form cocktail request
        query = st.text_input(
            label="Votre commande",
            placeholder="Un cocktail fruite et rafraichissant...",
            label_visibility="collapsed",
            key="cocktail_query"
        )

        # Budget dropdown (structured data - RNCP requirement)
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
            index=1,  # Default: Modere
            label_visibility="collapsed",
            key="budget_select"
        )

        submitted = st.button(
            "Invoquer le Barman",
            use_container_width=True,
            type="primary"
        )

    if submitted and query:
        return query, budget
    return "", ""


def render_error_message(message: str):
    """Render styled error message."""
    st.markdown(f"""
        <div class="error-speakeasy">
            {message}
        </div>
    """, unsafe_allow_html=True)


def render_cocktail_card(recipe: dict, characteristics: dict, cached: bool = False):
    """Render cocktail result with radar chart using native Streamlit components."""
    name = recipe.get("name", "Cocktail Mystere")
    instructions = recipe.get("instructions", "Melanger avec elegance...")
    ingredients = recipe.get("ingredients", [])

    # Use native Streamlit container with custom styling
    with st.container():
        # Cocktail name header
        if cached:
            st.markdown(f"## 🥃 {name} <small style='color: #D4AF37; font-size: 0.5em;'>Du Cellier</small>", unsafe_allow_html=True)
        else:
            st.markdown(f"## 🥃 {name}")

        st.divider()

        # Ingredients section
        st.markdown("### 📜 Ingrédients")
        for ing in ingredients:
            st.markdown(f"- ◆ {ing}")

        st.divider()

        # Preparation section
        st.markdown("### 🍸 Préparation")
        st.markdown(f"*{instructions}*")

        st.divider()

        # Radar chart section
        st.markdown("### 📊 Profil Gustatif")

    fig = create_radar_chart(characteristics)
    st.plotly_chart(fig, config={'displayModeBar': False}, key="radar_chart")


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
    # Inject CSS first
    inject_speakeasy_css()

    # Render header
    render_header()

    # Get user input (hybrid questionnaire: text + budget dropdown)
    query, budget = render_cocktail_input()

    # Handle states
    if query:
        # Enrich query with budget context for better recommendations
        enriched_query = f"{query} (budget: {budget})"
        # Loading state with custom spinner
        with st.spinner("Le barman prepare votre creation..."):
            result = generate_recipe(enriched_query)

        # Error state
        if result["status"] == "error":
            render_error_message(result["message"])

        # Success state
        else:
            recipe = result["recipe"]
            cached = result.get("cached", False)

            # Use taste_profile from Gemini if available, otherwise generate fallback
            if "taste_profile" in recipe and recipe["taste_profile"]:
                characteristics = recipe["taste_profile"]
            else:
                characteristics = generate_cocktail_characteristics(recipe["name"])

            # Render cocktail card with radar
            render_cocktail_card(recipe, characteristics, cached)

            # Show query used
            st.markdown(f"""
                <p style="text-align: center; color: #A89968; font-size: 0.9rem; margin-top: 2rem;">
                    <em>Inspire par: "{recipe.get('query', query)}"</em>
                </p>
            """, unsafe_allow_html=True)
    else:
        # Empty state
        render_empty_state()

    # Footer with authors and disclaimer
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
