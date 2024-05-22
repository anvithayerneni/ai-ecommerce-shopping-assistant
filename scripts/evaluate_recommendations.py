from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# APPLICATION IMPORTS
# ============================================================

from app.db.session import SessionLocal
from app.models.product import Product

from app.services.embedding_service import embedding_service

from app.services.recommendation_model import ProductEncoder

from app.services.recommendation_service import (
    recommend_similar_products,
)

from app.services.recommendation_metrics import (
    hit_rate_at_k,
    precision_at_k,
    recall_at_k,
)

from scripts.enrich_product_metadata import product_text


# ============================================================
# CONFIGURATION
# ============================================================

EVALUATION_FILE = (
    PROJECT_ROOT
    / "data"
    / "recommendation_eval.json"
)

TOP_K = 5

# Hybrid weights
CATEGORY_WEIGHT = 0.40
USE_CASE_WEIGHT = 0.20
SEMANTIC_WEIGHT = 0.40


# ============================================================
# LOAD EVALUATION CASES
# ============================================================

def load_evaluation_cases() -> list[dict]:
    """
    Load recommendation evaluation cases from JSON.
    """

    with EVALUATION_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        data = json.load(file)

    return data["evaluation_cases"]


# ============================================================
# BUILD EMBEDDING CACHE
# ============================================================

def build_embedding_cache(
    products: list[Product],
) -> dict[int | str, list[float]]:
    """
    Generate semantic embeddings for all products once.

    Embeddings are cached by product ID.
    """

    texts = [
        product_text(product)
        for product in products
    ]

    print()
    print(
        "Generating product embeddings..."
    )

    print(
        f"Products to embed: {len(products)}"
    )

    embeddings = (
        embedding_service.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )
    )

    embedding_cache = {}

    for product, embedding in zip(
        products,
        embeddings,
    ):
        embedding_cache[
            product.id
        ] = embedding.tolist()

    print(
        "Embedding generation complete."
    )

    return embedding_cache


# ============================================================
# GENERIC METRIC CALCULATION
# ============================================================

def calculate_metrics(
    recommended_ids: list,
    relevant_ids: set,
) -> tuple[float, float, float]:

    hit = hit_rate_at_k(
        recommended_ids,
        relevant_ids,
        TOP_K,
    )

    precision = precision_at_k(
        recommended_ids,
        relevant_ids,
        TOP_K,
    )

    recall = recall_at_k(
        recommended_ids,
        relevant_ids,
        TOP_K,
    )

    return (
        hit,
        precision,
        recall,
    )


# ============================================================
# SEMANTIC BASELINE
# ============================================================

def semantic_baseline_recommendations(
    query_product: Product,
    products: list[Product],
    embedding_cache: dict,
) -> list:

    query_embedding = embedding_cache.get(
        query_product.id
    )

    if query_embedding is None:
        return []

    # --------------------------------------------------------
    # Calculate cosine similarity because embeddings are
    # normalized.
    #
    # cosine similarity = dot product.
    # --------------------------------------------------------

    scored_products = []

    for candidate in products:

        if candidate.id == query_product.id:
            continue

        candidate_embedding = (
            embedding_cache.get(
                candidate.id
            )
        )

        if candidate_embedding is None:
            continue

        similarity = sum(
            a * b
            for a, b in zip(
                query_embedding,
                candidate_embedding,
            )
        )

        scored_products.append(
            (
                candidate.id,
                similarity,
            )
        )

    scored_products.sort(
        key=lambda item: item[1],
        reverse=True,
    )

    return [
        product_id
        for product_id, _score
        in scored_products[:TOP_K]
    ]


# ============================================================
# EVALUATE SEMANTIC BASELINE
# ============================================================

def evaluate_semantic_baseline(
    cases: list[dict],
    products: list[Product],
    embedding_cache: dict,
    products_by_id: dict,
) -> dict[str, float]:

    hit_scores = []
    precision_scores = []
    recall_scores = []

    evaluated_cases = 0

    print()
    print(
        "Running semantic baseline..."
    )

    for case in cases:

        query_id = case[
            "query_product_id"
        ]

        relevant_ids = set(
            case[
                "relevant_product_ids"
            ]
        )

        query_product = (
            products_by_id.get(
                query_id
            )
        )

        if query_product is None:

            print(
                f"SKIP Product {query_id}: "
                "not found"
            )

            continue

        recommended_ids = (
            semantic_baseline_recommendations(
                query_product=query_product,
                products=products,
                embedding_cache=embedding_cache,
            )
        )

        hit, precision, recall = (
            calculate_metrics(
                recommended_ids,
                relevant_ids,
            )
        )

        hit_scores.append(hit)
        precision_scores.append(precision)
        recall_scores.append(recall)

        evaluated_cases += 1

        print(
            f"Product {query_id}: "
            f"recommended={recommended_ids} "
            f"relevant={sorted(relevant_ids)}"
        )

    if evaluated_cases == 0:
        raise RuntimeError(
            "No baseline cases could be evaluated."
        )

    return {
        "cases": float(
            evaluated_cases
        ),

        "hit_rate_at_5": (
            sum(hit_scores)
            / len(hit_scores)
        ),

        "precision_at_5": (
            sum(precision_scores)
            / len(precision_scores)
        ),

        "recall_at_5": (
            sum(recall_scores)
            / len(recall_scores)
        ),
    }


# ============================================================
# EVALUATE HYBRID MODEL
# ============================================================

def evaluate_hybrid(
    cases: list[dict],
    products: list[Product],
    embedding_cache: dict,
    products_by_id: dict,
) -> dict[str, float]:

    model = ProductEncoder()

    hit_scores = []
    precision_scores = []
    recall_scores = []

    evaluated_cases = 0

    print()
    print(
        "Running hybrid recommender..."
    )

    for case in cases:

        query_id = case[
            "query_product_id"
        ]

        relevant_ids = set(
            case[
                "relevant_product_ids"
            ]
        )

        query_product = (
            products_by_id.get(
                query_id
            )
        )

        if query_product is None:

            print(
                f"SKIP Product {query_id}: "
                "not found"
            )

            continue

        query_embedding = (
            embedding_cache.get(
                query_product.id
            )
        )

        if query_embedding is None:

            print(
                f"SKIP Product {query_id}: "
                "embedding unavailable"
            )

            continue

        results = (
            recommend_similar_products(
                query_product=query_product,
                candidate_products=products,
                model=model,
                query_embedding=query_embedding,
                candidate_embeddings=embedding_cache,
                top_k=TOP_K,
            )
        )

        recommended_ids = [
            result.product_id
            for result in results
        ]

        hit, precision, recall = (
            calculate_metrics(
                recommended_ids,
                relevant_ids,
            )
        )

        hit_scores.append(hit)
        precision_scores.append(precision)
        recall_scores.append(recall)

        evaluated_cases += 1

        print(
            f"Product {query_id}: "
            f"recommended={recommended_ids} "
            f"relevant={sorted(relevant_ids)}"
        )

    if evaluated_cases == 0:
        raise RuntimeError(
            "No hybrid cases could be evaluated."
        )

    return {
        "cases": float(
            evaluated_cases
        ),

        "hit_rate_at_5": (
            sum(hit_scores)
            / len(hit_scores)
        ),

        "precision_at_5": (
            sum(precision_scores)
            / len(precision_scores)
        ),

        "recall_at_5": (
            sum(recall_scores)
            / len(recall_scores)
        ),
    }


# ============================================================
# PRINT METRICS
# ============================================================

def print_metrics(
    title: str,
    results: dict[str, float],
) -> None:

    print()
    print(title)

    print(
        "-" * len(title)
    )

    print(
        f"Cases: "
        f"{int(results['cases'])}"
    )

    print(
        f"Hit Rate@5: "
        f"{results['hit_rate_at_5']:.4f}"
    )

    print(
        f"Precision@5: "
        f"{results['precision_at_5']:.4f}"
    )

    print(
        f"Recall@5: "
        f"{results['recall_at_5']:.4f}"
    )


# ============================================================
# IMPROVEMENT REPORT
# ============================================================

def print_improvement(
    baseline: dict[str, float],
    hybrid: dict[str, float],
) -> None:

    print()
    print(
        "HYBRID IMPROVEMENT"
    )

    print(
        "------------------"
    )

    metrics = [
        (
            "Hit Rate@5",
            "hit_rate_at_5",
        ),
        (
            "Precision@5",
            "precision_at_5",
        ),
        (
            "Recall@5",
            "recall_at_5",
        ),
    ]

    for label, key in metrics:

        baseline_value = baseline[key]
        hybrid_value = hybrid[key]

        absolute_change = (
            hybrid_value
            - baseline_value
        )

        if baseline_value != 0:

            relative_change = (
                absolute_change
                / baseline_value
                * 100
            )

            relative_text = (
                f"{relative_change:+.2f}%"
            )

        else:

            relative_text = (
                "N/A"
            )

        print(
            f"{label}: "
            f"{baseline_value:.4f} -> "
            f"{hybrid_value:.4f} "
            f"({absolute_change:+.4f}, "
            f"{relative_text})"
        )


# ============================================================
# MAIN EVALUATION
# ============================================================

def evaluate(
    baseline_only: bool = False,
) -> dict:

    cases = load_evaluation_cases()

    db = SessionLocal()

    try:

        # ----------------------------------------------------
        # LOAD PRODUCTS
        # ----------------------------------------------------

        products = (
            db.query(Product)
            .filter(
                Product.category.isnot(None)
            )
            .all()
        )

        if not products:
            raise RuntimeError(
                "No enriched products were found."
            )

        products_by_id = {
            product.id: product
            for product in products
        }

        print(
            f"Loaded {len(products)} enriched products."
        )

        # ----------------------------------------------------
        # EMBEDDINGS
        # ----------------------------------------------------

        embedding_cache = (
            build_embedding_cache(
                products
            )
        )

        # ----------------------------------------------------
        # BASELINE
        # ----------------------------------------------------

        baseline = (
            evaluate_semantic_baseline(
                cases=cases,
                products=products,
                embedding_cache=embedding_cache,
                products_by_id=products_by_id,
            )
        )

        print_metrics(
            "SEMANTIC BASELINE",
            baseline,
        )

        if baseline_only:
            return {
                "baseline": baseline,
            }

        # ----------------------------------------------------
        # HYBRID
        # ----------------------------------------------------

        hybrid = evaluate_hybrid(
            cases=cases,
            products=products,
            embedding_cache=embedding_cache,
            products_by_id=products_by_id,
        )

        print_metrics(
            "HYBRID RECOMMENDER",
            hybrid,
        )

        print()
        print(
            "Hybrid weights:"
        )

        print(
            f"Categorical: "
            f"{CATEGORY_WEIGHT:.0%}"
        )

        print(
            f"Use-case: "
            f"{USE_CASE_WEIGHT:.0%}"
        )

        print(
            f"Semantic: "
            f"{SEMANTIC_WEIGHT:.0%}"
        )

        print_improvement(
            baseline,
            hybrid,
        )

        return {
            "baseline": baseline,
            "hybrid": hybrid,
        }

    finally:

        db.close()


# ============================================================
# CLI
# ============================================================

def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Evaluate semantic baseline "
            "and hybrid recommendation models."
        )
    )

    parser.add_argument(
        "--baseline",
        action="store_true",
        help=(
            "Run only the semantic baseline."
        ),
    )

    args = parser.parse_args()

    evaluate(
        baseline_only=args.baseline
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()