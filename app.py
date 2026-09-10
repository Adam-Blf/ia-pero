"""
L'IA Pero - Explorateur de similarite semantique avec SBERT
Soutenance RNCP40875 - Adam Beloucif & Emilien Morice
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
# PAGE CONFIGURATION
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
@st.cache_resource(show_spinner="Chargement du modèle SBERT...")
def get_model(model_name: str):
    return load_sbert_model(model_name)


@st.cache_data(show_spinner="Génération des embeddings...")
def get_embeddings(_model, texts: tuple) -> np.ndarray:
    return compute_embeddings(_model, list(texts))


def _call_openai(api_key: str, prompt: str) -> str:
    """Appel OpenAI GPT pour enrichissement sémantique (mode API activé)."""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es un expert en analyse sémantique. Réponds de manière concise."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=300,
            temperature=0.5,
        )
        return resp.choices[0].message.content.strip()
    except ImportError:
        return "openai non installé (pip install openai)"
    except Exception as e:
        return f"Erreur API : {e}"


# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    # Header
    st.title("🍐 L'IA Pero")
    st.markdown(
        "**Explorez la similarité sémantique entre vos textes** "
        "grâce aux embeddings Sentence-Transformers."
    )

    # ----- Sidebar: Configuration -----
    with st.sidebar:
        st.header("⚙️ Configuration")

        model_name = st.selectbox(
            "Modèle SBERT",
            options=[
                "all-MiniLM-L6-v2",
                "all-mpnet-base-v2",
                "paraphrase-multilingual-MiniLM-L12-v2",
            ],
            help=(
                "all-MiniLM-L6-v2 : Rapide (384 dim) | "
                "all-mpnet-base-v2 : Meilleure qualité (768 dim) | "
                "multilingual : Support multilingue"
            ),
        )

        st.markdown("---")
        st.markdown("### 🔑 Clé API (optionnel)")
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="sk-...",
            help=(
                "Entrez votre clé OpenAI pour activer l'enrichissement GPT des résultats. "
                "Sans clé, le mode local SBERT s'applique normalement."
            ),
            key="openai_api_key",
        )

        if api_key:
            st.success("✅ Mode API activé - GPT enrichissement disponible")
        else:
            st.info("🖥️ Mode local - SBERT uniquement")

        st.markdown("---")
        st.markdown("### À propos")
        st.info(
            "L'IA Pero utilise SBERT pour transformer vos textes "
            "en vecteurs et calculer leur proximité sémantique. "
            "Avec une clé API, GPT enrichit l'interprétation des résultats."
        )
        st.markdown("---")
        st.caption("SBERT + GPT (optionnel) | RNCP40875 | Adam Beloucif")

    # Load model
    model = get_model(model_name)

    # ----- Main content -----
    st.subheader("Entrez vos textes")

    default_texts = (
        "Le chat dort sur le canapé.\n"
        "Le félin se repose sur le sofa.\n"
        "J'aime manger des pommes.\n"
        "La voiture roule vite sur l'autoroute."
    )

    text_input = st.text_area(
        "Un texte par ligne",
        value=default_texts,
        height=200,
        help="Entrez plusieurs phrases pour comparer leur similarité sémantique",
    )

    texts = parse_multiline_input(text_input)

    if len(texts) < 2:
        st.warning("Veuillez entrer au moins 2 textes pour comparer.")
        return

    # Analysis button
    if st.button("Analyser la similarité", type="primary", use_container_width=True):
        embeddings = get_embeddings(model, tuple(texts))
        similarity_matrix = compute_similarity_matrix(embeddings)

        st.success(f"Analyse terminée ! {len(texts)} textes comparés.")

        # Results layout
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Matrice de similarité")
            labels = [f"T{i+1}" for i in range(len(texts))]
            df_sim = pd.DataFrame(similarity_matrix, index=labels, columns=labels)
            st.dataframe(
                df_sim.style.background_gradient(cmap="RdYlGn", vmin=0, vmax=1),
                use_container_width=True,
            )

        with col2:
            st.subheader("Légende")
            for i, text in enumerate(texts):
                st.markdown(f"**T{i+1}**: {truncate_text(text)}")

        # Most similar pairs
        st.subheader("Paires les plus similaires")
        top_pairs = find_most_similar_pairs(texts, similarity_matrix, top_k=3)
        for i, j, score in top_pairs:
            st.markdown(
                f"- **T{i+1}** et **T{j+1}** : `{format_similarity_score(score)}` de similarité"
            )

        # GPT enrichissement si clé présente
        if api_key and top_pairs:
            st.subheader("🤖 Enrichissement GPT")
            best_i, best_j, best_score = top_pairs[0]
            t1 = texts[best_i]
            t2 = texts[best_j]
            prompt = (
                f"Ces deux phrases ont une similarité sémantique de {best_score:.1%} :\n"
                f"1. \"{t1}\"\n"
                f"2. \"{t2}\"\n"
                f"Explique en 2-3 phrases pourquoi elles sont proches sémantiquement."
            )
            with st.spinner("GPT analyse les résultats..."):
                explication = _call_openai(api_key, prompt)
            st.info(explication)

        # Details techniques
        with st.expander("Détails techniques"):
            mode = "SBERT + GPT (OpenAI)" if api_key else "SBERT local uniquement"
            st.markdown(f"""
            - **Modèle SBERT** : `{model_name}`
            - **Mode** : `{mode}`
            - **Dimension des embeddings** : `{embeddings.shape[1]}`
            - **Nombre de textes** : `{len(texts)}`
            """)


if __name__ == "__main__":
    main()
