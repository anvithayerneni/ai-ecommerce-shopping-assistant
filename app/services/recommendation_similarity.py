from __future__ import annotations

import math

import numpy as np


def cosine_similarity(
    vector_a: list[float] | np.ndarray,
    vector_b: list[float] | np.ndarray,
) -> float:
    """
    Calculate cosine similarity between two vectors.

    Returns a value between -1 and 1.
    Returns 0.0 for invalid or zero-length vectors.
    """

    try:
        a = np.asarray(vector_a, dtype=np.float32)
        b = np.asarray(vector_b, dtype=np.float32)
    except (TypeError, ValueError):
        return 0.0

    if a.ndim != 1 or b.ndim != 1:
        return 0.0

    if a.shape != b.shape:
        return 0.0

    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))

    if (
        norm_a == 0.0
        or norm_b == 0.0
        or not math.isfinite(norm_a)
        or not math.isfinite(norm_b)
    ):
        return 0.0

    similarity = float(
        np.dot(a, b) / (norm_a * norm_b)
    )

    if not math.isfinite(similarity):
        return 0.0

    return max(-1.0, min(1.0, similarity))


def semantic_similarity(
    embedding_a: list[float] | None,
    embedding_b: list[float] | None,
) -> float:
    """
    Calculate similarity between semantic product embeddings.

    Missing embeddings produce a neutral score of 0.0.
    """

    if embedding_a is None or embedding_b is None:
        return 0.0

    return cosine_similarity(
        embedding_a,
        embedding_b,
    )


def structured_similarity(
    representation_a: list[float] | None,
    representation_b: list[float] | None,
) -> float:
    """
    Calculate similarity between structured product representations.

    Missing representations produce a neutral score of 0.0.
    """

    if representation_a is None or representation_b is None:
        return 0.0

    return cosine_similarity(
        representation_a,
        representation_b,
    )


def hybrid_similarity(
    *,
    semantic_score: float,
    structured_score: float,
    semantic_weight: float = 0.7,
    structured_weight: float = 0.3,
) -> float:
    """
    Combine semantic and structured similarity scores.

    The default gives semantic similarity more influence because
    product text and semantic embeddings contain richer information
    for the current catalog.
    """

    if semantic_weight < 0 or structured_weight < 0:
        raise ValueError(
            "Similarity weights must be non-negative."
        )

    total_weight = semantic_weight + structured_weight

    if total_weight == 0:
        raise ValueError(
            "At least one similarity weight must be greater than zero."
        )

    score = (
        semantic_score * semantic_weight
        + structured_score * structured_weight
    ) / total_weight

    return max(-1.0, min(1.0, score))
