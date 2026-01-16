"""
L'IA Pero - Semantic similarity explorer with Sentence-Transformers
"""
import streamlit as st
import pandas as pd
import numpy as np

from src.embeddings import (
    load_sbert_model,
    compute_embeddings,
    compute_similarity_matrix,
    find_most_similar_pairs,
)
from src.utils import truncate_text, parse_multiline_input, format_similarity_score


# =============================================================================
# PAGE CONFIGURATION (must be first Streamlit command)
# =============================================================================
st.set_page_config(
    page_title="L'IA Pero",
    page_icon="🍐",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =============================================================================
# CACHED RESOURCES
# =============================================================================
@st.cache_resource(show_spinner="Chargement du modele SBERT...")
def get_model(model_name: str):
    """Load SBERT model with caching (loaded once per session)."""
    return load_sbert_model(model_name)


@st.cache_data(show_spinner="Generation des embeddings...")
def get_embeddings(_model, texts: tuple) -> np.ndarray:
    """
    Compute embeddings with caching.
    _model prefixed with _ to skip hashing (non-serializable).
    texts as tuple to be hashable.
    """
    return compute_embeddings(_model, list(texts))


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    # Header
    st.title("🍐 L'IA Pero")
    st.markdown(
        "**Explorez la similarite semantique entre vos textes** "
        "grace aux embeddings Sentence-Transformers."
    )

    # ----- Sidebar: Configuration -----
    with st.sidebar:
        st.header("Configuration")

        model_name = st.selectbox(
            "Modele SBERT",
            options=[
                "all-MiniLM-L6-v2",
                "all-mpnet-base-v2",
                "paraphrase-multilingual-MiniLM-L12-v2",
            ],
            help="all-MiniLM-L6-v2: Rapide (384 dim) | all-mpnet-base-v2: Meilleure qualite (768 dim) | multilingual: Support multilingue"
        )

        st.markdown("---")
        st.markdown("### A propos")
        st.info(
            "L'IA Pero utilise SBERT pour transformer vos textes "
            "en vecteurs et calculer leur proximite semantique."
        )

        st.markdown("---")
        st.caption("Built with Streamlit + Sentence-Transformers")

    # Load model
    model = get_model(model_name)

    # ----- Main content -----
    st.subheader("Entrez vos textes")

    default_texts = (
        "Le chat dort sur le canape.\n"
        "Le felin se repose sur le sofa.\n"
        "J'aime manger des pommes.\n"
        "La voiture roule vite sur l'autoroute."
    )

    text_input = st.text_area(
        "Un texte par ligne",
        value=default_texts,
        height=200,
        help="Entrez plusieurs phrases pour comparer leur similarite semantique"
    )

    texts = parse_multiline_input(text_input)

    if len(texts) < 2:
        st.warning("Veuillez entrer au moins 2 textes pour comparer.")
        return

    # Analysis button
    if st.button("Analyser la similarite", type="primary", use_container_width=True):
        # Compute embeddings and similarity
        embeddings = get_embeddings(model, tuple(texts))
        similarity_matrix = compute_similarity_matrix(embeddings)

        st.success(f"Analyse terminee ! {len(texts)} textes compares.")

        # Results layout
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Matrice de similarite")
            labels = [f"T{i+1}" for i in range(len(texts))]
            df_sim = pd.DataFrame(
                similarity_matrix,
                index=labels,
                columns=labels
            )
            st.dataframe(
                df_sim.style.background_gradient(cmap="RdYlGn", vmin=0, vmax=1),
                use_container_width=True
            )

        with col2:
            st.subheader("Legende")
            for i, text in enumerate(texts):
                st.markdown(f"**T{i+1}**: {truncate_text(text)}")

        # Most similar pairs
        st.subheader("Paires les plus similaires")
        top_pairs = find_most_similar_pairs(texts, similarity_matrix, top_k=3)

        for i, j, score in top_pairs:
            st.markdown(
                f"- **T{i+1}** et **T{j+1}** : `{format_similarity_score(score)}` de similarite"
            )

        # Embeddings info
        with st.expander("Details techniques"):
            st.markdown(f"""
            - **Modele**: `{model_name}`
            - **Dimension des embeddings**: `{embeddings.shape[1]}`
            - **Nombre de textes**: `{len(texts)}`
            """)


if __name__ == "__main__":
    main()
