import pytest

from app.services.recommendation_metrics import (
    hit_rate_at_k,
    precision_at_k,
    recall_at_k,
)


def test_hit_rate_at_k_when_relevant_item_is_present():
    score = hit_rate_at_k(
        recommended_ids=[1, 2, 3],
        relevant_ids={2},
        k=3,
    )

    assert score == 1.0


def test_hit_rate_at_k_when_no_relevant_item_is_present():
    score = hit_rate_at_k(
        recommended_ids=[1, 2, 3],
        relevant_ids={5},
        k=3,
    )

    assert score == 0.0


def test_hit_rate_at_k_respects_k():
    score = hit_rate_at_k(
        recommended_ids=[1, 2, 3],
        relevant_ids={3},
        k=2,
    )

    assert score == 0.0


def test_precision_at_k():
    score = precision_at_k(
        recommended_ids=[1, 2, 3, 4],
        relevant_ids={2, 4},
        k=4,
    )

    assert score == pytest.approx(0.5)


def test_precision_at_k_respects_k():
    score = precision_at_k(
        recommended_ids=[1, 2, 3, 4],
        relevant_ids={4},
        k=2,
    )

    assert score == 0.0


def test_recall_at_k():
    score = recall_at_k(
        recommended_ids=[1, 2, 3, 4],
        relevant_ids={2, 4},
        k=4,
    )

    assert score == pytest.approx(1.0)


def test_recall_at_k_partial():
    score = recall_at_k(
        recommended_ids=[1, 2, 3, 4],
        relevant_ids={3, 4, 5},
        k=3,
    )

    assert score == pytest.approx(1 / 3)


def test_empty_relevant_set():
    assert hit_rate_at_k([1, 2], set(), 2) == 0.0
    assert precision_at_k([1, 2], set(), 2) == 0.0
    assert recall_at_k([1, 2], set(), 2) == 0.0


def test_invalid_k():
    with pytest.raises(ValueError):
        hit_rate_at_k([1], {1}, 0)

    with pytest.raises(ValueError):
        precision_at_k([1], {1}, 0)

    with pytest.raises(ValueError):
        recall_at_k([1], {1}, 0)
