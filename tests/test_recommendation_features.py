from app.models.product import Product
from app.services.recommendation_features import (
    build_recommendation_features,
    build_recommendation_text,
    normalize_embedding,
    normalize_price,
    normalize_rating,
)


def test_normalize_price():
    assert normalize_price(500) == 0.5


def test_normalize_price_clips_extreme_values():
    assert normalize_price(1_160_000) == 1.0


def test_normalize_price_handles_missing_values():
    assert normalize_price(None) == 0.0
    assert normalize_price(0) == 0.0


def test_normalize_rating():
    assert normalize_rating(4.5) == 0.9


def test_normalize_rating_clips_values():
    assert normalize_rating(10) == 1.0
    assert normalize_rating(-1) == 0.0


def test_build_recommendation_text():
    product = Product(
        id=1,
        name="Test Laptop",
        brand="TestBrand",
        category="Laptops",
        subcategory="Ultrabook",
        description="Laptop for programming",
        tags="programming, portable",
        features="long battery life",
        target_audience="developers",
        use_cases="programming",
        color="Silver",
        material="Aluminum",
        price=999.99,
        rating=4.5,
        stock=10,
    )

    text = build_recommendation_text(product)

    assert "Test Laptop" in text
    assert "TestBrand" in text
    assert "Laptops" in text
    assert "Ultrabook" in text
    assert "Laptop for programming" in text
    assert "programming, portable" in text
    assert "long battery life" in text
    assert "developers" in text
    assert "Silver" in text
    assert "Aluminum" in text


def test_normalize_embedding():
    embedding = [3.0, 4.0]

    normalized = normalize_embedding(embedding)

    assert normalized is not None
    assert len(normalized) == 2
    assert abs(normalized[0] - 0.6) < 1e-6
    assert abs(normalized[1] - 0.8) < 1e-6


def test_normalize_embedding_handles_missing_values():
    assert normalize_embedding(None) is None
    assert normalize_embedding([]) is None


def test_build_recommendation_features():
    product = Product(
        id=1,
        name="Test Laptop",
        brand="TestBrand",
        category="Laptops",
        description="Laptop for programming",
        price=500,
        rating=4.5,
        stock=10,
    )

    features = build_recommendation_features(
        product,
        source_embedding=[3.0, 4.0],
    )

    assert features.product_id == 1
    assert features.normalized_price == 0.5
    assert features.normalized_rating == 0.9
    assert "Test Laptop" in features.text
    assert features.embedding is not None
    assert len(features.embedding) == 2