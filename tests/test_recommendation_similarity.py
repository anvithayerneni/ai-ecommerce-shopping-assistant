import pytest

from app.services.recommendation_similarity import (
    cosine_similarity,
    hybrid_similarity,
    semantic_similarity,
    structured_similarity,
)


def test_cosine_similarity_identical_vectors():
    score = cosine_similarity(
        [1.0, 0.0],
        [1.0, 0.0],
    )

    assert score == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    score = cosine_similarity(
        [1.0, 0.0],
        [0.0, 1.0],
    )

    assert score == pytest.approx(0.0)


def test_cosine_similarity_opposite_vectors():
    score = cosine_similarity(
        [1.0, 0.0],
        [-1.0, 0.0],
    )

    assert score == pytest.approx(-1.0)


def test_cosine_similarity_zero_vector():
    score = cosine_similarity(
        [0.0, 0.0],
        [1.0, 0.0],
    )

    assert score == 0.0


def test_cosine_similarity_dimension_mismatch():
    score = cosine_similarity(
        [1.0, 0.0],
        [1.0, 0.0, 0.0],
    )

    assert score == 0.0


def test_semantic_similarity_missing_embedding():
    assert semantic_similarity(
        None,
        [1.0, 0.0],
    ) == 0.0


def test_structured_similarity_missing_representation():
    assert structured_similarity(
        [1.0, 0.0],
        None,
    ) == 0.0


def test_hybrid_similarity_default_weights():
    score = hybrid_similarity(
        semantic_score=1.0,
        structured_score=0.0,
    )

    assert score == pytest.approx(0.7)


def test_hybrid_similarity_combines_scores():
    score = hybrid_similarity(
        semantic_score=0.8,
        structured_score=0.6,
        semantic_weight=0.7,
        structured_weight=0.3,
    )

    assert score == pytest.approx(0.74)


def test_hybrid_similarity_normalizes_weights():
    score = hybrid_similarity(
        semantic_score=1.0,
        structured_score=0.0,
        semantic_weight=7.0,
        structured_weight=3.0,
    )

    assert score == pytest.approx(0.7)


def test_hybrid_similarity_rejects_zero_weights():
    with pytest.raises(ValueError):
        hybrid_similarity(
            semantic_score=0.5,
            structured_score=0.5,
            semantic_weight=0.0,
            structured_weight=0.0,
        )


def test_hybrid_similarity_rejects_negative_weights():
    with pytest.raises(ValueError):
        hybrid_similarity(
            semantic_score=0.5,
            structured_score=0.5,
            semantic_weight=-1.0,
            structured_weight=1.0,
        )
