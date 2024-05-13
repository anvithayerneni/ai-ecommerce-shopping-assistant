import pytest

from app.services.recommendation_features import (
    RecommendationFeatures,
)
from app.services.recommendation_representation import (
    build_product_representation,
)


def test_build_product_representation():
    features = RecommendationFeatures(
        product_id=5,
        normalized_price=0.5,
        normalized_rating=0.9,
        text="Test Laptop programming portable",
        embedding=[0.6, 0.8],
    )

    representation = build_product_representation(
        features,
    )

    assert representation.product_id == 5
    assert len(representation.vector) == 5

    assert representation.vector[0] == pytest.approx(0.5)
    assert representation.vector[1] == pytest.approx(0.9)

    assert representation.semantic_embedding == [0.6, 0.8]


def test_product_representation_contains_text_statistics():
    features = RecommendationFeatures(
        product_id=1,
        normalized_price=0.2,
        normalized_rating=0.8,
        text="running shoes lightweight",
        embedding=None,
    )

    representation = build_product_representation(
        features,
    )

    # price + rating + 3 text statistics
    assert len(representation.vector) == 5

    assert representation.vector[2] > 0
    assert representation.vector[3] == 3
    assert representation.vector[4] == 3


def test_product_representation_handles_empty_text():
    features = RecommendationFeatures(
        product_id=2,
        normalized_price=0.4,
        normalized_rating=0.7,
        text="",
        embedding=None,
    )

    representation = build_product_representation(
        features,
    )

    assert representation.vector[0] == pytest.approx(0.4)
    assert representation.vector[1] == pytest.approx(0.7)

    assert representation.vector[2:] == [
        0.0,
        0.0,
        0.0,
    ]