"""
L'IA Pero - Evaluation metrics.

Computes Precision@K, Recall@K, NDCG@K for the retrieval engine
and precision/recall for the semantic guardrail.

Adapted from cocktail-ia-generatif/src/evaluation.py.
"""
from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


@dataclass
class EvalConfig:
    k_values: list[int] = None
    n_queries: int = 50
    guardrail_test_size: int = 30
    out_of_domain_queries: list[str] = None

    def __post_init__(self):
        if self.k_values is None:
            self.k_values = [1, 3, 5, 10]
        if self.out_of_domain_queries is None:
            self.out_of_domain_queries = [
                "repare mon velo",
                "quelle est la capitale de la France",
                "recommande-moi un film",
                "code un algorithme de tri",
                "meteorologie de demain",
                "recette de pizza italienne",
                "commande un taxi",
                "aide moi avec mes maths",
            ]


@dataclass
class EvalResults:
    precision_at_k: dict[int, float]
    recall_at_k: dict[int, float]
    ndcg_at_k: dict[int, float]
    guardrail_precision: float
    guardrail_recall: float
    n_queries_evaluated: int
    config: dict


def evaluate_retrieval(
    retrieval,
    test_queries: list[dict],
    config: Optional[EvalConfig] = None,
) -> EvalResults:
    """
    Evaluate the CocktailRetrieval engine on a list of test queries.

    Each test query is a dict:
        {
          "query": "cocktail tropical et fruite",
          "relevant_names": ["The Tropical Mirage", "Acapulco Mule", ...]
        }
    OR using category as ground-truth (if relevant_names not set):
        {
          "query": "...",
          "relevant_category": "Tropical"
        }
    """
    cfg = config or EvalConfig()
    max_k = max(cfg.k_values)

    p_at_k: dict[int, list[float]] = {k: [] for k in cfg.k_values}
    r_at_k: dict[int, list[float]] = {k: [] for k in cfg.k_values}
    n_at_k: dict[int, list[float]] = {k: [] for k in cfg.k_values}

    df = retrieval._df
    n_evaluated = 0

    for item in test_queries[:cfg.n_queries]:
        query = item["query"]

        # Ground-truth: explicit names take precedence over category
        if "relevant_names" in item and item["relevant_names"]:
            relevant = set(item["relevant_names"])
        elif "relevant_category" in item and df is not None:
            cat = item["relevant_category"]
            relevant = set(df[df["category"] == cat]["name"].tolist())
        else:
            continue

        if not relevant:
            continue

        results = retrieval.search(query, top_k=max_k)
        retrieved_names = [r["name"] for r in results]

        for k in cfg.k_values:
            p_at_k[k].append(_precision_at_k(relevant, retrieved_names, k))
            r_at_k[k].append(_recall_at_k(relevant, retrieved_names, k))
            n_at_k[k].append(_ndcg_at_k(relevant, retrieved_names, k))

        n_evaluated += 1

    return EvalResults(
        precision_at_k={k: round(float(np.mean(v)), 4) if v else 0.0 for k, v in p_at_k.items()},
        recall_at_k={k: round(float(np.mean(v)), 4) if v else 0.0 for k, v in r_at_k.items()},
        ndcg_at_k={k: round(float(np.mean(v)), 4) if v else 0.0 for k, v in n_at_k.items()},
        guardrail_precision=0.0,
        guardrail_recall=0.0,
        n_queries_evaluated=n_evaluated,
        config=asdict(cfg),
    )


def evaluate_guardrail(
    check_fn,
    config: Optional[EvalConfig] = None,
) -> dict:
    """
    Evaluate the semantic guardrail.

    check_fn(query: str) -> dict with key "pass": bool
    """
    cfg = config or EvalConfig()

    ood_queries = cfg.out_of_domain_queries
    in_domain_queries = [
        "cocktail avec vodka et citron",
        "quelque chose de frais et sucre",
        "mojito ou daiquiri",
        "recette avec rhum et menthe",
        "long drink pour l'ete",
        "boisson petillante pour une soiree",
        "aperitif leger",
    ]

    tp = fp = tn = fn = 0

    for q in ood_queries:
        result = check_fn(q)
        if not result.get("pass", True):
            tn += 1
        else:
            fp += 1

    for q in in_domain_queries:
        result = check_fn(q)
        if result.get("pass", False):
            tp += 1
        else:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "rejection_rate_ood": round(tn / len(ood_queries), 3) if ood_queries else 0.0,
        "tp": tp, "fp": fp, "tn": tn, "fn": fn,
    }


# ---------- metric helpers ----------

def _precision_at_k(relevant: set, retrieved: list, k: int) -> float:
    return len(set(retrieved[:k]) & relevant) / k if k > 0 else 0.0


def _recall_at_k(relevant: set, retrieved: list, k: int) -> float:
    return len(set(retrieved[:k]) & relevant) / max(len(relevant), 1)


def _ndcg_at_k(relevant: set, retrieved: list, k: int) -> float:
    dcg = sum(1.0 / np.log2(i + 2) for i, item in enumerate(retrieved[:k]) if item in relevant)
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / np.log2(i + 2) for i in range(ideal_hits))
    return dcg / idcg if idcg > 0 else 0.0


def save_results(results: EvalResults, path: Optional[Path] = None) -> Path:
    """Save evaluation results to JSON."""
    REPORTS_DIR.mkdir(exist_ok=True)
    out = path or REPORTS_DIR / "eval_results.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(asdict(results), f, indent=2, ensure_ascii=False)
    logger.info("Results saved: %s", out)
    return out


def print_summary(results: EvalResults) -> None:
    print("\n=== L'IA Pero - Resultats d'evaluation ===\n")
    print(f"Requetes evaluees : {results.n_queries_evaluated}")
    print("\nRetrieval - Precision@K :")
    for k, v in results.precision_at_k.items():
        print(f"  P@{k:2d}    = {v:.4f}")
    print("\nRetrieval - NDCG@K :")
    for k, v in results.ndcg_at_k.items():
        print(f"  NDCG@{k:2d} = {v:.4f}")
    if results.guardrail_precision > 0:
        print(f"\nGuardrail Precision : {results.guardrail_precision:.3f}")
        print(f"Guardrail Recall    : {results.guardrail_recall:.3f}")
    print("=" * 44)
