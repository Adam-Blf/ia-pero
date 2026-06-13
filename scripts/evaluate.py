"""
L'IA Pero - Evaluation script
==================================

Computes two offline metrics from data/eval/queries.jsonl:

1. **hit@5** (in-domain queries):
   For each query labeled "in-domain", the SBERT search returns the top-5
   most similar cocktails from the 600-cocktail database. A query is a *hit*
   if at least one of the top-5 descriptions/names contains a keyword from
   the query's ``expected_keywords`` list.

2. **correct-refusal rate** (out-of-domain queries):
   For each query labeled "out-domain", check_relevance() from backend.py
   is called. A correct refusal is when the guardrail returns status="error".

Usage:
    python scripts/evaluate.py                   # prints and writes reports/EVALUATION.md
    python scripts/evaluate.py --quiet           # prints only the summary line

Note: This script imports src.backend directly (no Streamlit dependency).
      faiss-cpu is NOT required; the script uses pure numpy cosine similarity.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

# Force UTF-8 stdout on Windows so that ✓/✗ symbols render correctly
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.backend import check_relevance, get_sbert_model  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
EVAL_FILE = ROOT / "data" / "eval" / "queries.jsonl"
COCKTAILS_CSV = ROOT / "data" / "cocktails.csv"
REPORT_FILE = ROOT / "reports" / "EVALUATION.md"
BASELINE_FILE = ROOT / "reports" / "EVALUATION_baseline.json"
TOP_K = 5


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_queries() -> list[dict[str, Any]]:
    """Load queries.jsonl into a list of dicts."""
    if not EVAL_FILE.exists():
        raise FileNotFoundError(f"Eval file not found: {EVAL_FILE}")
    queries = []
    with open(EVAL_FILE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                queries.append(json.loads(line))
    return queries


def _build_corpus_embeddings(model) -> tuple[list[str], list[str], np.ndarray]:
    """Load cocktails CSV and encode descriptions with SBERT.

    Returns:
        (names, descriptions, embeddings_array)
    """
    df = pd.read_csv(COCKTAILS_CSV)
    names = df["name"].fillna("").tolist()
    descriptions = df["description_semantique"].fillna("").tolist()
    print(f"  Encoding {len(descriptions)} cocktail descriptions with SBERT...", flush=True)
    t0 = time.time()
    embeddings = model.encode(descriptions, convert_to_numpy=True, show_progress_bar=False)
    print(f"  Done in {time.time() - t0:.1f}s", flush=True)
    return names, descriptions, embeddings


def _cosine_top_k(
    query_emb: np.ndarray,
    corpus_embs: np.ndarray,
    k: int = TOP_K,
) -> list[tuple[int, float]]:
    """Return (idx, score) pairs for the top-k cosine-similarity matches."""
    norms_q = np.linalg.norm(query_emb)
    norms_c = np.linalg.norm(corpus_embs, axis=1)
    safe_norms = np.where(norms_c == 0, 1.0, norms_c)
    scores = (corpus_embs @ query_emb) / (safe_norms * max(norms_q, 1e-9))
    top_indices = np.argsort(scores)[::-1][:k]
    return [(int(i), float(scores[i])) for i in top_indices]


def _hit_at_k(
    query: str,
    expected_keywords: list[str],
    names: list[str],
    descriptions: list[str],
    corpus_embs: np.ndarray,
    model,
    k: int = TOP_K,
) -> tuple[bool, list[str]]:
    """Return (hit, top_cocktail_names) for an in-domain query."""
    q_emb = model.encode(query, convert_to_numpy=True)
    top_results = _cosine_top_k(q_emb, corpus_embs, k=k)
    top_names = [names[idx] for idx, _ in top_results]
    top_texts = [
        (names[idx] + " " + descriptions[idx]).lower()
        for idx, _ in top_results
    ]
    if not expected_keywords:
        # No expected keywords → any result counts as a hit
        return bool(top_results), top_names
    hit = any(
        kw.lower() in text
        for text in top_texts
        for kw in expected_keywords
    )
    return hit, top_names


# ---------------------------------------------------------------------------
# Main evaluation routine
# ---------------------------------------------------------------------------

def evaluate(quiet: bool = False) -> dict[str, Any]:
    """
    Run the full evaluation and return a results dict.

    Returns:
        {
            "hit_at_5": float,           # in-domain hit@5 rate
            "in_domain_total": int,
            "in_domain_hits": int,
            "refusal_rate": float,       # out-of-domain correct-refusal rate
            "out_domain_total": int,
            "out_domain_correct_refusals": int,
            "details": list[dict],
        }
    """
    queries = _load_queries()
    in_domain = [q for q in queries if q["type"] == "in-domain"]
    out_domain = [q for q in queries if q["type"] == "out-domain"]

    if not quiet:
        print("\nL'IA Pero - Offline Evaluation")
        print(f"  {len(in_domain)} in-domain queries, {len(out_domain)} out-of-domain queries\n")

    # ---- Load SBERT model ----
    if not quiet:
        print("Loading SBERT model...", flush=True)
    model = get_sbert_model()

    # ---- Build corpus embeddings ----
    if not quiet:
        print("Building corpus embeddings...", flush=True)
    names, descriptions, corpus_embs = _build_corpus_embeddings(model)

    details: list[dict] = []

    # ---- In-domain: hit@5 ----
    if not quiet:
        print(f"\nEvaluating in-domain queries (hit@{TOP_K})...")
    hits = 0
    for q in in_domain:
        hit, top_names = _hit_at_k(
            q["query"],
            q.get("expected_keywords", []),
            names,
            descriptions,
            corpus_embs,
            model,
        )
        if hit:
            hits += 1
        symbol = "✓" if hit else "✗"
        if not quiet:
            print(f"  [{symbol}] {q['id']}: {q['query'][:55]}")
            if not hit:
                print(f"       top-5: {top_names[:3]}")
        details.append({
            "id": q["id"],
            "type": "in-domain",
            "query": q["query"],
            "hit": hit,
            "top_5": top_names,
        })

    hit_at_5 = hits / len(in_domain) if in_domain else 0.0

    # ---- Out-of-domain: correct-refusal rate ----
    if not quiet:
        print("\nEvaluating out-of-domain queries (guardrail refusal)...")
    correct_refusals = 0
    for q in out_domain:
        result = check_relevance(q["query"])
        refused = result["status"] == "error"
        reason = result.get("reason", "?")
        if refused:
            correct_refusals += 1
        symbol = "✓" if refused else "✗"
        if not quiet:
            print(f"  [{symbol}] {q['id']}: {q['query'][:55]}  (reason={reason})")
        details.append({
            "id": q["id"],
            "type": "out-domain",
            "query": q["query"],
            "refused": refused,
            "reason": reason,
        })

    refusal_rate = correct_refusals / len(out_domain) if out_domain else 0.0

    results = {
        "hit_at_5": hit_at_5,
        "in_domain_total": len(in_domain),
        "in_domain_hits": hits,
        "refusal_rate": refusal_rate,
        "out_domain_total": len(out_domain),
        "out_domain_correct_refusals": correct_refusals,
        "details": details,
    }

    if not quiet:
        print(f"\n{'='*55}")
        print(f"  hit@5             : {hit_at_5:.1%}  ({hits}/{len(in_domain)})")
        print(f"  correct refusals  : {refusal_rate:.1%}  ({correct_refusals}/{len(out_domain)})")
        print(f"{'='*55}\n")

    return results


def _write_report(results: dict[str, Any], baseline: dict[str, Any] | None = None) -> None:
    """Write EVALUATION.md to reports/, with optional before/after comparison."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    in_lines = [d for d in results["details"] if d["type"] == "in-domain"]
    out_lines = [d for d in results["details"] if d["type"] == "out-domain"]

    lines = [
        "# Evaluation Report · L'IA Pero",
        "",
        "## Summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| hit@5 (in-domain) | **{results['hit_at_5']:.1%}** ({results['in_domain_hits']}/{results['in_domain_total']}) |",
        f"| correct-refusal rate (out-of-domain) | **{results['refusal_rate']:.1%}** ({results['out_domain_correct_refusals']}/{results['out_domain_total']}) |",
        "",
    ]

    if baseline is not None:
        lines += [
            "## Before / After · guardrail improvement",
            "",
            "| Metric | Before | After | Delta |",
            "|--------|--------|-------|-------|",
            f"| hit@5 | {baseline['hit_at_5']:.1%} | {results['hit_at_5']:.1%} "
            f"| {results['hit_at_5'] - baseline['hit_at_5']:+.1%} |",
            f"| correct-refusal rate | {baseline['refusal_rate']:.1%} | {results['refusal_rate']:.1%} "
            f"| {results['refusal_rate'] - baseline['refusal_rate']:+.1%} |",
            "",
        ]

    lines += [
        "## Definitions",
        "",
        "- **hit@5**: for each in-domain query the top-5 SBERT results are checked "
        "for at least one cocktail whose name or description contains an "
        "`expected_keyword`. Computed over pure numpy cosine similarity on the "
        "600-cocktail corpus (no Streamlit, no FAISS dependency).",
        "- **correct-refusal rate**: fraction of out-of-domain queries that the "
        "two-level guardrail (`check_relevance()`) correctly rejects (status=error).",
        "",
        "## In-domain results",
        "",
        "| id | query | hit | top-1 |",
        "|----|-------|-----|-------|",
    ]

    for d in in_lines:
        top1 = d["top_5"][0] if d["top_5"] else "-"
        mark = "yes" if d["hit"] else "**no**"
        q = d["query"].replace("|", "\\|")
        lines.append(f"| {d['id']} | {q} | {mark} | {top1} |")

    lines += [
        "",
        "## Out-of-domain results",
        "",
        "| id | query | refused | reason |",
        "|----|-------|---------|--------|",
    ]

    for d in out_lines:
        mark = "yes" if d["refused"] else "**no (false pass)**"
        q = d["query"].replace("|", "\\|")
        lines.append(f"| {d['id']} | {q} | {mark} | {d.get('reason', '?')} |")

    lines += ["", "---", "Generated by `scripts/evaluate.py`.", ""]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {REPORT_FILE}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="L'IA Pero offline evaluation")
    parser.add_argument("--quiet", action="store_true", help="Print summary only")
    parser.add_argument("--no-report", action="store_true", help="Skip writing EVALUATION.md")
    parser.add_argument(
        "--save-baseline",
        action="store_true",
        help="Save current results as baseline for before/after comparison",
    )
    args = parser.parse_args()

    results = evaluate(quiet=args.quiet)

    # Load existing baseline for comparison (if available)
    baseline: dict[str, Any] | None = None
    if BASELINE_FILE.exists():
        try:
            baseline = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
        except Exception:
            baseline = None

    if args.save_baseline:
        BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
        slim = {k: v for k, v in results.items() if k != "details"}
        BASELINE_FILE.write_text(json.dumps(slim, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Baseline saved to {BASELINE_FILE}")

    if not args.no_report:
        _write_report(results, baseline=baseline)

    # Exit with non-zero if hit@5 < 50% or refusal rate < 80% (CI gate)
    ok = results["hit_at_5"] >= 0.50 and results["refusal_rate"] >= 0.80
    sys.exit(0 if ok else 1)
