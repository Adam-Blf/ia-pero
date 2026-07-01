"""
L'IA Pero - Standalone retrieval module.

Extracted from src/app.py (Speakeasy). No Streamlit dependency.
Use this module for testing, evaluation, and CLI scripts.
"""
from __future__ import annotations

import logging
from pathlib import Path

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CSV_PATH = DATA_DIR / "cocktails.csv"
MODEL_NAME = "all-MiniLM-L6-v2"


def load_cocktails() -> pd.DataFrame:
    """Load the cocktails CSV into a DataFrame."""
    if not CSV_PATH.exists():
        logger.error("cocktails.csv not found at %s", CSV_PATH)
        return pd.DataFrame()
    return pd.read_csv(CSV_PATH)


def _build_description(row: pd.Series) -> str:
    """Build a single text representation for a cocktail row."""
    parts = [str(row.get("name", "")), str(row.get("description_semantique", ""))]
    ingredients = str(row.get("ingredients", ""))
    if ingredients:
        parts.append(ingredients)
    return " ".join(p for p in parts if p)


class CocktailRetrieval:
    """
    SBERT + FAISS retrieval engine for cocktails.
    Standalone (no Streamlit). Use for evaluation and CLI.
    """

    def __init__(self, model_name: str = MODEL_NAME):
        self.model_name = model_name
        self._model = None
        self._df: pd.DataFrame | None = None
        self._descriptions: list[str] | None = None
        self._embeddings: np.ndarray | None = None
        self._faiss_index = None

    # ---------- lazy properties ----------

    @property
    def model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            logger.info("SBERT loaded: %s", self.model_name)
        return self._model

    def fit(self, df: pd.DataFrame | None = None) -> "CocktailRetrieval":
        """
        Build the FAISS index from the cocktail DataFrame.
        Call once before calling search().
        """
        self._df = df if df is not None else load_cocktails()
        self._descriptions = [_build_description(row) for _, row in self._df.iterrows()]

        logger.info("Encoding %d cocktails...", len(self._descriptions))
        raw = self.model.encode(
            self._descriptions,
            batch_size=64,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        norms = np.linalg.norm(raw, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1, norms)
        self._embeddings = (raw / norms).astype("float32")

        try:
            import faiss
            dim = self._embeddings.shape[1]
            index = faiss.IndexFlatIP(dim)
            index.add(self._embeddings)
            self._faiss_index = index
            logger.info("FAISS index built (%d vectors, dim=%d)", index.ntotal, dim)
        except ImportError:
            logger.warning("faiss-cpu not installed, using numpy fallback")
            self._faiss_index = None

        return self

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Semantic search over the cocktail corpus.

        Returns list of dicts with keys: name, category, similarity, description, ingredients.
        """
        if self._df is None or self._embeddings is None:
            raise RuntimeError("Call fit() before search().")

        q_raw = self.model.encode(query, convert_to_numpy=True).astype("float32")
        q_norm_val = np.linalg.norm(q_raw)
        q_vec = (q_raw / max(q_norm_val, 1e-9)).reshape(1, -1)

        if self._faiss_index is not None:
            scores, indices = self._faiss_index.search(q_vec, top_k)
            pairs = [(int(indices[0][i]), float(scores[0][i])) for i in range(len(indices[0])) if indices[0][i] >= 0]
        else:
            sims = (self._embeddings @ q_vec.T).flatten()
            top_idx = np.argsort(sims)[::-1][:top_k]
            pairs = [(int(i), float(sims[i])) for i in top_idx]

        results = []
        for idx, score in pairs:
            row = self._df.iloc[idx]
            results.append({
                "name": str(row["name"]),
                "category": str(row.get("category", "")),
                "similarity": round(score, 4),
                "description": str(row.get("description_semantique", "")),
                "ingredients": str(row.get("ingredients", "")),
            })
        return results
