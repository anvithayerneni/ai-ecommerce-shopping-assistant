import pytest

from app.models.product import Product
from app.services.recommendation_model import ProductEncoder
from app.services.recommendation_service import (
    ProductRecommendation,
    recommend_similar_products,
    score_product_pair,
)


def create_product(
    product_id: int,
    name: str,
    category: str,
    price: float,
    rating: float,
) -> Product:
    return Product(
        id=product_id,
        name=name,
        brand="TestBrand",
        category=category,
        description=f"{name} product",
        price=price,
        rating=rating,
        stock=10,
    )


def test_score_product_pair_returns_valid_score():
    model = ProductEncoder()

    product_a = create_product(
        1,
        "Running Shoes",
        "Running Shoes",
        90.0,
        4.5,
    )

    product_b = create_product(
        2,
        "Training Shoes",
        "Running Shoes",
        85.0,
        4.4,
    )

    score = score_product_pair(
        product_a,
        product_b,
        model,
    )

    assert 0.0 <= score <= 1.0


def test_score_product_pair_with_embeddings():
    model = ProductEncoder()

    product_a = create_product(
        1,
        "Running Shoes",
        "Running Shoes",
        90.0,
        4.5,
    )

    product_b = create_product(
        2,
        "Training Shoes",
        "Running Shoes",
        85.0,
        4.4,
    )

    score = score_product_pair(
        product_a,
        product_b,
        model,
        embedding_a=[1.0, 0.0],
        embedding_b=[1.0, 0.0],
    )

    assert score > 0.0


def test_recommend_similar_products_excludes_query_product():
    model = ProductEncoder()

    query_product = create_product(
        1,
        "Running Shoes",
        "Running Shoes",
        90.0,
        4.5,
    )

    candidate_products = [
        query_product,
        create_product(
            2,
            "Training Shoes",
            "Running Shoes",
            85.0,
            4.4,
        ),
        create_product(
            3,
            "Laptop",
            "Laptops",
            900.0,
            4.7,
        ),
    ]

    results = recommend_similar_products(
        query_product,
        candidate_products,
        model,
        top_k=5,
    )

    result_ids = [
        result.product_id
        for result in results
    ]

    assert 1 not in result_ids
    assert 2 in result_ids
    assert 3 in result_ids


def test_recommend_similar_products_respects_top_k():
    model = ProductEncoder()

    query_product = create_product(
        1,
        "Running Shoes",
        "Running Shoes",
        90.0,
        4.5,
    )

    candidates = [
        create_product(
            product_id,
            f"Product {product_id}",
            "Running Shoes",
            80.0 + product_id,
            4.0,
        )
        for product_id in range(2, 10)
    ]

    results = recommend_similar_products(
        query_product,
        candidates,
        model,
        top_k=3,
    )

    assert len(results) == 3


def test_recommendations_are_sorted_by_score():
    model = ProductEncoder()

    query_product = create_product(
        1,
        "Running Shoes",
        "Running Shoes",
        90.0,
        4.5,
    )

    candidates = [
        create_product(
            2,
            "Training Shoes",
            "Running Shoes",
            85.0,
            4.4,
        ),
        create_product(
            3,
            "Laptop",
            "Laptops",
            900.0,
            4.7,
        ),
    ]

    results = recommend_similar_products(
        query_product,
        candidates,
        model,
        top_k=2,
    )

    assert results[0].score >= results[1].score


def test_recommend_similar_products_rejects_invalid_top_k():
    model = ProductEncoder()

    product = create_product(
        1,
        "Product",
        "Testing",
        50.0,
        4.0,
    )

    with pytest.raises(ValueError):
        recommend_similar_products(
            product,
            [],
            model,
            top_k=0,
        )


def test_product_recommendation_structure():
    recommendation = ProductRecommendation(
        product_id=10,
        score=0.85,
    )

    assert recommendation.product_id == 10
    assert recommendation.score == pytest.approx(0.85)
