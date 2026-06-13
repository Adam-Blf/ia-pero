"""
L'IA Pero - GenAI Evaluation Scaffold (LLM-as-judge)
=====================================================

Evaluates recipe generation quality using a RAGAS-inspired LLM-as-judge
approach, gated behind GOOGLE_API_KEY.

Two metrics are computed for each in-domain query:

1. **faithfulness**: Does the generated recipe contain plausible cocktail
   ingredients and instructions, without hallucinating clearly wrong
   combinations? Scored 0-1 by the judge LLM.

2. **answer_relevancy**: Is the recipe actually relevant to the user's
   request (e.g., a tropical recipe for a tropical request)?
   Scored 0-1 by the judge LLM.

Prerequisite
------------
GOOGLE_API_KEY must be set (env var or .env file).

Usage
-----
    python scripts/eval_genai.py                    # full eval, writes reports/EVAL_GENAI.md
    python scripts/eval_genai.py --queries 5        # limit to first 5 queries (fast smoke test)
    python scripts/eval_genai.py --quiet            # summary line only

The app itself does NOT require GOOGLE_API_KEY at runtime; this script
is a standalone evaluation tool for developers.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Force UTF-8 stdout on Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
EVAL_FILE = ROOT / "data" / "eval" / "queries.jsonl"
REPORT_FILE = ROOT / "reports" / "EVAL_GENAI.md"


# ---------------------------------------------------------------------------
# Guard: fail fast if no API key
# ---------------------------------------------------------------------------

def _require_api_key() -> None:
    """Abort with a clear message when GOOGLE_API_KEY is absent."""
    if not GOOGLE_API_KEY:
        print(
            "\n[SKIP] GOOGLE_API_KEY is not set.\n"
            "This script requires a valid Gemini API key to run LLM-as-judge evaluation.\n"
            "Set it via:\n"
            "  • .env file: GOOGLE_API_KEY=your_key\n"
            "  • Environment variable: export GOOGLE_API_KEY=your_key\n\n"
            "The main app (src/app.py) works without this key (fallback mode).\n",
            file=sys.stderr,
        )
        sys.exit(0)  # Exit cleanly (not an error in CI when key is absent)


# ---------------------------------------------------------------------------
# Judge LLM
# ---------------------------------------------------------------------------

JUDGE_PROMPT_FAITHFULNESS = """You are an expert cocktail evaluator.

User request: "{query}"

Generated recipe:
  Name: {name}
  Ingredients: {ingredients}
  Instructions: {instructions}

Score the FAITHFULNESS of this recipe: does it contain realistic cocktail
ingredients (real spirits, mixers, garnishes) and plausible preparation steps?
A score of 1.0 means fully faithful to cocktail craft. A score of 0.0 means
the ingredients or instructions are nonsensical for a cocktail.

Respond with ONLY a JSON object: {{"score": <float 0.0-1.0>, "reason": "<one sentence>"}}
"""

JUDGE_PROMPT_RELEVANCY = """You are an expert cocktail evaluator.

User request: "{query}"

Generated recipe:
  Name: {name}
  Ingredients: {ingredients}

Score the ANSWER RELEVANCY: how well does this recipe match what the user asked for?
A score of 1.0 means the recipe is a perfect match for the request.
A score of 0.0 means the recipe is completely unrelated to the request.

Respond with ONLY a JSON object: {{"score": <float 0.0-1.0>, "reason": "<one sentence>"}}
"""


def _call_judge(prompt: str) -> dict[str, Any]:
    """
    Call the Gemini API with a judge prompt and parse the JSON response.

    Returns:
        dict with 'score' (float) and 'reason' (str), or error dict on failure.
    """
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Strip markdown code fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        result = json.loads(text.strip())
        return {
            "score": float(result.get("score", 0.0)),
            "reason": str(result.get("reason", "")),
        }
    except Exception as exc:
        return {"score": 0.0, "reason": f"Judge error: {exc}"}


# ---------------------------------------------------------------------------
# Recipe generation (without Streamlit)
# ---------------------------------------------------------------------------

def _generate_recipe_for_eval(query: str) -> dict[str, Any] | None:
    """
    Call src.backend.generate_recipe() directly (no Streamlit dependency).

    Returns the recipe dict, or None if generation failed.
    """
    from src.backend import generate_recipe
    result = generate_recipe(query)
    if result.get("status") == "ok":
        return result["recipe"]
    return None


# ---------------------------------------------------------------------------
# Main evaluation loop
# ---------------------------------------------------------------------------

def evaluate_genai(
    queries: list[dict[str, Any]],
    quiet: bool = False,
) -> dict[str, Any]:
    """
    Run LLM-as-judge evaluation on a set of in-domain queries.

    Args:
        queries: List of in-domain query dicts from queries.jsonl.
        quiet:   If True, suppress per-query output.

    Returns:
        Summary dict with mean faithfulness, mean answer_relevancy, and details.
    """
    details: list[dict[str, Any]] = []
    faithfulness_scores: list[float] = []
    relevancy_scores: list[float] = []

    for q in queries:
        query = q["query"]
        if not quiet:
            print(f"  Evaluating: {query[:60]}", flush=True)

        # Generate recipe
        recipe = _generate_recipe_for_eval(query)
        if recipe is None:
            if not quiet:
                print("    [SKIP] Recipe generation failed.")
            details.append({
                "id": q["id"],
                "query": query,
                "faithfulness": None,
                "answer_relevancy": None,
                "faithfulness_reason": "generation failed",
                "relevancy_reason": "generation failed",
            })
            continue

        name = recipe.get("name", "?")
        ingredients = ", ".join(recipe.get("ingredients", []))
        instructions = recipe.get("instructions", "")

        # Judge: faithfulness
        t0 = time.time()
        faith_result = _call_judge(
            JUDGE_PROMPT_FAITHFULNESS.format(
                query=query, name=name,
                ingredients=ingredients, instructions=instructions,
            )
        )
        time.sleep(0.5)  # Rate-limit courtesy

        # Judge: answer relevancy
        rel_result = _call_judge(
            JUDGE_PROMPT_RELEVANCY.format(
                query=query, name=name, ingredients=ingredients,
            )
        )
        elapsed = time.time() - t0

        faithfulness_scores.append(faith_result["score"])
        relevancy_scores.append(rel_result["score"])

        if not quiet:
            print(
                f"    [{name[:30]}] faithfulness={faith_result['score']:.2f} "
                f"relevancy={rel_result['score']:.2f}  ({elapsed:.1f}s)"
            )

        details.append({
            "id": q["id"],
            "query": query,
            "recipe_name": name,
            "faithfulness": faith_result["score"],
            "answer_relevancy": rel_result["score"],
            "faithfulness_reason": faith_result["reason"],
            "relevancy_reason": rel_result["reason"],
        })

    mean_faith = (
        sum(s for s in faithfulness_scores if s is not None) / len(faithfulness_scores)
        if faithfulness_scores else 0.0
    )
    mean_rel = (
        sum(s for s in relevancy_scores if s is not None) / len(relevancy_scores)
        if relevancy_scores else 0.0
    )

    return {
        "mean_faithfulness": mean_faith,
        "mean_answer_relevancy": mean_rel,
        "n_queries": len(queries),
        "details": details,
    }


# ---------------------------------------------------------------------------
# Report writer
# ---------------------------------------------------------------------------

def _write_report(results: dict[str, Any]) -> None:
    """Write EVAL_GENAI.md to reports/."""
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# GenAI Evaluation Report · L'IA Pero",
        "",
        "> **Method**: LLM-as-judge (Gemini 2.5 Flash Lite) on "
        f"{results['n_queries']} in-domain queries from "
        "`data/eval/queries.jsonl`.",
        "",
        "## Summary",
        "",
        "| Metric | Score |",
        "|--------|-------|",
        f"| mean faithfulness | **{results['mean_faithfulness']:.2f}** / 1.00 |",
        f"| mean answer relevancy | **{results['mean_answer_relevancy']:.2f}** / 1.00 |",
        "",
        "## Definitions",
        "",
        "- **faithfulness**: Does the generated recipe contain realistic cocktail "
        "ingredients and plausible preparation steps? Scored 0-1 by the judge LLM.",
        "- **answer relevancy**: How well does the recipe match the user request? "
        "Scored 0-1 by the judge LLM.",
        "",
        "## Per-query results",
        "",
        "| id | query | recipe | faith. | relevancy |",
        "|----|-------|--------|--------|-----------|",
    ]

    for d in results["details"]:
        f_score = f"{d['faithfulness']:.2f}" if d["faithfulness"] is not None else "N/A"
        r_score = f"{d['answer_relevancy']:.2f}" if d["answer_relevancy"] is not None else "N/A"
        recipe = d.get("recipe_name", "-")[:25]
        q = d["query"].replace("|", "\\|")[:50]
        lines.append(f"| {d['id']} | {q} | {recipe} | {f_score} | {r_score} |")

    lines += [
        "",
        "---",
        "Generated by `scripts/eval_genai.py` · requires `GOOGLE_API_KEY`.",
        "",
    ]

    REPORT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nReport written to {REPORT_FILE}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="L'IA Pero GenAI evaluation (LLM-as-judge). Requires GOOGLE_API_KEY."
    )
    parser.add_argument(
        "--queries", type=int, default=0,
        help="Limit evaluation to first N in-domain queries (0 = all)",
    )
    parser.add_argument("--quiet", action="store_true", help="Print summary only")
    parser.add_argument("--no-report", action="store_true", help="Skip writing EVAL_GENAI.md")
    args = parser.parse_args()

    # Gate: abort cleanly if GOOGLE_API_KEY is absent
    _require_api_key()

    # Load in-domain queries
    if not EVAL_FILE.exists():
        print(f"[ERROR] Eval file not found: {EVAL_FILE}", file=sys.stderr)
        sys.exit(1)

    all_queries = []
    with open(EVAL_FILE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                q = json.loads(line)
                if q["type"] == "in-domain":
                    all_queries.append(q)

    if args.queries > 0:
        all_queries = all_queries[: args.queries]

    if not args.quiet:
        print(f"\nL'IA Pero - GenAI Evaluation (LLM-as-judge)")
        print(f"  {len(all_queries)} in-domain queries to evaluate\n")

    results = evaluate_genai(all_queries, quiet=args.quiet)

    if not args.quiet:
        print(f"\n{'='*55}")
        print(f"  mean faithfulness    : {results['mean_faithfulness']:.2f}")
        print(f"  mean answer relevancy: {results['mean_answer_relevancy']:.2f}")
        print(f"{'='*55}")

    if not args.no_report:
        _write_report(results)
