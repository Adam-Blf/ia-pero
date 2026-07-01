"""
L'IA Pero - Embeddings module
Handles SBERT model loading and similarity computation.

Includes EmbeddingEngine class (ported from cocktail-ia-generatif)
for disk-cached, OOP-friendly access.
"""
from __future__ import annotations

import hashlib
import logging
import pickle
from pathlib import Path
from typing import Optional

import numpy as np
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(__file__).parent.parent / ".cache"
_CACHE_DIR.mkdir(exist_ok=True)


def load_sbert_model(model_name: str = "all-MiniLM-L6-v2") -> SentenceTransformer:
    """
    Load a pre-trained Sentence Transformer model.

    Args:
        model_name: Name of the model from HuggingFace Hub

    Returns:
        SentenceTransformer model instance

    Available models:
        - all-MiniLM-L6-v2: Fast, lightweight (384 dim)
        - all-mpnet-base-v2: Best quality (768 dim)
        - paraphrase-multilingual-MiniLM-L12-v2: Multilingual support
    """
    return SentenceTransformer(model_name)


def compute_embeddings(model: SentenceTransformer, texts: list[str]) -> np.ndarray:
    """
    Generate embeddings for a list of texts.

    Args:
        model: SentenceTransformer model instance
        texts: List of text strings to encode

    Returns:
        numpy array of shape (n_texts, embedding_dim)
    """
    return model.encode(texts, convert_to_numpy=True)


def compute_similarity_matrix(embeddings: np.ndarray) -> np.ndarray:
    """
    Compute cosine similarity matrix between all embeddings.

    Args:
        embeddings: numpy array of shape (n, dim)

    Returns:
        numpy array of shape (n, n) with similarity scores
    """
    return util.cos_sim(embeddings, embeddings).numpy()


def find_most_similar_pairs(
    texts: list[str],
    similarity_matrix: np.ndarray,
    top_k: int = 3
) -> list[tuple[int, int, float]]:
    """
    Find the top-k most similar pairs of texts.

    Args:
        texts: Original list of texts
        similarity_matrix: Precomputed similarity matrix
        top_k: Number of top pairs to return

    Returns:
        List of tuples (idx1, idx2, similarity_score)
    """
    pairs = []
    n = len(texts)

    for i in range(n):
        for j in range(i + 1, n):
            pairs.append((i, j, similarity_matrix[i][j]))

    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs[:top_k]


class EmbeddingEngine:
    """
    SBERT wrapper with disk-based MD5 cache.
    Avoids re-encoding the corpus on every script run.

    Usage:
        engine = EmbeddingEngine()
        corpus_embs = engine.encode(descriptions)   # cached after first call
        query_emb   = engine.encode_single(query)
        score       = engine.similarity(query_emb, corpus_embs[0])
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache: bool = True):
        self.model_name = model_name
        self.use_cache = cache
        self._model: Optional[SentenceTransformer] = None

    @property
    def model(self) -> SentenceTransformer:
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
            logger.info("SBERT loaded: %s", self.model_name)
        return self._model

    def encode(self, texts: list[str], batch_size: int = 64, show_progress: bool = False) -> np.ndarray:
        """Encode a list of texts. Uses disk cache to avoid recomputation."""
        key = self._cache_key(texts)
        path = _CACHE_DIR / f"{key}.pkl"
        if self.use_cache and path.exists():
            with open(path, "rb") as f:
                return pickle.load(f)
        embs = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        if self.use_cache:
            with open(path, "wb") as f:
                pickle.dump(embs, f)
        return embs

    def encode_single(self, text: str) -> np.ndarray:
        """Encode one text (no cache, used for real-time queries)."""
        return self.model.encode(text, normalize_embeddings=True, convert_to_numpy=True)

    def similarity(self, vec_a: np.ndarray, vec_b: np.ndarray) -> float:
        """Cosine similarity between two L2-normalised vectors (dot product)."""
        return float(np.dot(vec_a, vec_b))

    def similarity_matrix(self, emb_a: np.ndarray, emb_b: Optional[np.ndarray] = None) -> np.ndarray:
        """Return a (N, M) cosine similarity matrix."""
        b = emb_a if emb_b is None else emb_b
        return np.dot(emb_a, b.T)

    @property
    def embedding_dim(self) -> int:
        return self.model.get_sentence_embedding_dimension()

    def _cache_key(self, texts: list[str]) -> str:
        content = self.model_name + "||".join(texts)
        return hashlib.md5(content.encode("utf-8")).hexdigest()
