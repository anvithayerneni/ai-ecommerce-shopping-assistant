from __future__ import annotations

from dataclasses import dataclass

from app.services.recommendation_content import (
    categorical_similarity,
    content_similarity,
    use_case_similarity,
)
from app.services.recommendation_similarity import (
    semantic_similarity,
)
from app.services.recommendation_model import (
    ProductEncoder,
)


@dataclass(frozen=True)
class ProductRecommendation:
    product_id: int | str
    score: float
    categorical_score: float = 0.0
    use_case_score: float = 0.0
    semantic_score: float = 0.0
    explanation: str = ""


def score_product_pair(
    product_a,
    product_b,
    model: ProductEncoder | None = None,
    *,
    embedding_a=None,
    embedding_b=None,
    categorical_weight: float = 0.60,
    use_case_weight: float = 0.15,
    semantic_weight: float = 0.25,
) -> float:
    """
    Calculate content-aware similarity between two products.

    The optional model argument is retained for API compatibility
    with the existing recommendation pipeline. The current scorer
    intentionally uses explicit product metadata and semantic
    embeddings rather than untrained neural representations.
    """

    del model

    return content_similarity(
        product_a,
        product_b,
        embedding_a=embedding_a,
        embedding_b=embedding_b,
        categorical_weight=categorical_weight,
        use_case_weight=use_case_weight,
        semantic_weight=semantic_weight,
    )


def recommend_similar_products(
    query_product,
    candidate_products,
    model: ProductEncoder | None = None,
    *,
    query_embedding=None,
    candidate_embeddings: dict[int | str, list[float]] | None = None,
    top_k: int = 5,
) -> list[ProductRecommendation]:
    """
    Recommend products similar to query_product.

    The query product itself is excluded from the results.
    """

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    candidate_embeddings = candidate_embeddings or {}

    recommendations: list[ProductRecommendation] = []

    for product in candidate_products:
        if product.id == query_product.id:
            continue

        # score = score_product_pair(
        #     query_product,
        #     product,
        #     model,
        #     embedding_a=query_embedding,
        #     embedding_b=candidate_embeddings.get(
        #         product.id
        #     ),
        # )

        # recommendations.append(
        #     ProductRecommendation(
        #         product_id=product.id,
        #         score=score,
        #     )
        # )

        candidate_embedding = candidate_embeddings.get(
            product.id
        )

        categorical_score = categorical_similarity(
            query_product,
            product,
        )

        use_case_score = use_case_similarity(
            query_product,
            product,
        )

        semantic_score = 0.0

        if (
            query_embedding is not None
            and candidate_embedding is not None
        ):
            semantic_score = semantic_similarity(
                query_embedding,
                candidate_embedding,
            )

        score = (
            0.40 * categorical_score
            + 0.20 * use_case_score
            + 0.40 * semantic_score
        )

        reasons = []

        if categorical_score >= 0.60:
            reasons.append(
                "strong product/category similarity"
            )
        elif categorical_score >= 0.30:
            reasons.append(
                "related product category"
            )

        if use_case_score >= 0.75:
            reasons.append(
                "matching use cases"
            )
        elif use_case_score >= 0.40:
            reasons.append(
                "some overlapping use cases"
            )

        if semantic_score >= 0.60:
            reasons.append(
                "strong semantic similarity"
            )
        elif semantic_score >= 0.40:
            reasons.append(
                "similar product descriptions"
            )

        if not reasons:
            reasons.append(
                "overall product similarity"
            )

        explanation = (
            "Recommended because of "
            + ", ".join(reasons)
            + "."
        )

        recommendations.append(
            ProductRecommendation(
                product_id=product.id,
                score=score,
                categorical_score=categorical_score,
                use_case_score=use_case_score,
                semantic_score=semantic_score,
                explanation=explanation,
            )
        )

    recommendations.sort(
        key=lambda recommendation: (
            -recommendation.score,
            str(recommendation.product_id),
        )
    )

    return recommendations[:top_k]