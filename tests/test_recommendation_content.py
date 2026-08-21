import pytest

from app.models.product import Product
from app.services.recommendation_content import (
    categorical_similarity,
    content_similarity,
    use_case_similarity,
)


def create_product(
    category=None,
    subcategory=None,
    brand=None,
    use_cases=None,
    name="Test Product",
    description="Test product",
):
    return Product(
        name=name,
        description=description,
        category=category,
        subcategory=subcategory,
        brand=brand,
        use_cases=use_cases,
        price=100.0,
        rating=4.5,
        stock=10,
    )


def test_same_category_gets_similarity():
    product_a = create_product(
        category="Laptops",
    )

    product_b = create_product(
        category="Laptops",
    )

    score = categorical_similarity(
        product_a,
        product_b,
    )

    assert score == pytest.approx(0.6)


def test_same_subcategory_adds_similarity():
    product_a = create_product(
        category="Headphones",
        subcategory="Noise-Canceling Headphones",
    )

    product_b = create_product(
        category="Headphones",
        subcategory="Noise-Canceling Headphones",
    )

    score = categorical_similarity(
        product_a,
        product_b,
    )

    assert score == pytest.approx(0.8)


def test_same_brand_adds_similarity():
    product_a = create_product(
        name="Laptop",
        brand="Samsung",
        category="Furniture",
    )

    product_b = create_product(
        name="Chair",
        brand="Samsung",
        category="Furniture",
    )

    score = categorical_similarity(
        product_a,
        product_b,
    )

    assert score == pytest.approx(0.35)


def test_same_category_subcategory_and_brand():
    product_a = create_product(
        category="Laptops",
        subcategory="Ultrabook",
        brand="Apple",
    )

    product_b = create_product(
        category="Laptops",
        subcategory="Ultrabook",
        brand="Apple",
    )

    score = categorical_similarity(
        product_a,
        product_b,
    )

    assert score == pytest.approx(0.9)


def test_different_metadata_has_zero_similarity():
    product_a = create_product(
        category="Laptops",
        subcategory="Ultrabook",
        brand="Apple",
    )

    product_b = create_product(
        category="Headphones",
        subcategory="Noise-Canceling Headphones",
        brand="Sony",
    )

    score = categorical_similarity(
        product_a,
        product_b,
    )

    assert score == 0.0


def test_use_case_similarity():
    product_a = create_product(
        use_cases="travel, office work, studying",
    )

    product_b = create_product(
        use_cases="travel, office work, music",
    )

    score = use_case_similarity(
        product_a,
        product_b,
    )

    assert score == pytest.approx(3 / 5)


def test_use_case_similarity_with_no_data():
    product_a = create_product(
        use_cases=None,
    )

    product_b = create_product(
        use_cases="travel",
    )

    assert use_case_similarity(
        product_a,
        product_b,
    ) == 0.0


def test_content_similarity_with_embeddings():
    product_a = create_product(
        category="Laptops",
        subcategory="Ultrabook",
        brand="Apple",
        use_cases="programming, studying",
    )

    product_b = create_product(
        category="Laptops",
        subcategory="Productivity Laptop",
        brand="Samsung",
        use_cases="studying, office work",
    )

    score = content_similarity(
        product_a,
        product_b,
        embedding_a=[1.0, 0.0],
        embedding_b=[1.0, 0.0],
    )

    assert score > 0.0
    assert score <= 1.0


def test_content_similarity_rejects_negative_weight():
    product_a = create_product()
    product_b = create_product()

    with pytest.raises(ValueError):
        content_similarity(
            product_a,
            product_b,
            categorical_weight=-1.0,
        )


def test_content_similarity_rejects_zero_weights():
    product_a = create_product()
    product_b = create_product()

    with pytest.raises(ValueError):
        content_similarity(
            product_a,
            product_b,
            categorical_weight=0.0,
            use_case_weight=0.0,
            semantic_weight=0.0,
        )