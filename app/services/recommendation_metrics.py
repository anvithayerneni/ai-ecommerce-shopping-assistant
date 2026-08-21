from __future__ import annotations


def hit_rate_at_k(
    recommended_ids: list[int | str],
    relevant_ids: set[int | str],
    k: int,
) -> float:
    """
    Return 1.0 when at least one relevant item appears in the
    top-k recommendations, otherwise 0.0.
    """

    if k < 1:
        raise ValueError("k must be at least 1")

    if not relevant_ids:
        return 0.0

    top_k = recommended_ids[:k]

    return float(
        any(product_id in relevant_ids for product_id in top_k)
    )


def precision_at_k(
    recommended_ids: list[int | str],
    relevant_ids: set[int | str],
    k: int,
) -> float:
    """
    Calculate Precision@K.

    Precision@K = relevant recommendations in top-k / k.
    """

    if k < 1:
        raise ValueError("k must be at least 1")

    if not relevant_ids:
        return 0.0

    top_k = recommended_ids[:k]

    relevant_count = sum(
        product_id in relevant_ids
        for product_id in top_k
    )

    return relevant_count / len(top_k) if top_k else 0.0


def recall_at_k(
    recommended_ids: list[int | str],
    relevant_ids: set[int | str],
    k: int,
) -> float:
    """
    Calculate Recall@K.

    Recall@K = relevant recommendations retrieved in top-k /
               total relevant products.
    """

    if k < 1:
        raise ValueError("k must be at least 1")

    if not relevant_ids:
        return 0.0

    top_k = recommended_ids[:k]

    relevant_count = sum(
        product_id in relevant_ids
        for product_id in top_k
    )

    return relevant_count / len(relevant_ids)
