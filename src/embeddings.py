"""
L'IA Pero - Embeddings module
Handles SBERT model loading and similarity computation
"""
import numpy as np
from sentence_transformers import SentenceTransformer, util


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
