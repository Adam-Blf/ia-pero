#!/usr/bin/env python3
"""
L'IA Pero - P@K / NDCG evaluation (ported from cocktail-ia-generatif).

Computes formal information-retrieval metrics on category-based test queries.

Usage:
    python scripts/evaluate_pk.py
    python scripts/evaluate_pk.py --queries tests/test_queries.json --k 1 3 5 10 --save
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.retrieval import CocktailRetrieval
from src.evaluation import EvalConfig, evaluate_retrieval, print_summary, save_results

DEFAULT_QUERIES = ROOT / "tests" / "test_queries.json"


def main(args: argparse.Namespace) -> None:
    queries_path = Path(args.queries)
    if not queries_path.exists():
        print(f"[ERROR] File not found: {queries_path}")
        sys.exit(1)

    with open(queries_path, encoding="utf-8") as f:
        test_queries = json.load(f)

    print(f"Queries loaded: {len(test_queries)} from {queries_path.name}")
    print("Building retrieval engine (SBERT + FAISS)...")

    engine = CocktailRetrieval()
    engine.fit()
    print(f"  {len(engine._df)} cocktails indexed")

    cfg = EvalConfig(k_values=args.k or [1, 3, 5, 10])
    results = evaluate_retrieval(engine, test_queries, config=cfg)
    print_summary(results)

    if args.save:
        out = save_results(results)
        print(f"Report saved -> {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", default=str(DEFAULT_QUERIES))
    parser.add_argument("--k", nargs="+", type=int)
    parser.add_argument("--save", action="store_true")
    main(parser.parse_args())
