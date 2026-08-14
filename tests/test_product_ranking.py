from app.services.product_ranking import rerank_products
from app.services.query_understanding import understand_query


def test_category_and_use_case_reranking():
    intent = understand_query(
        "laptop for programming"
    )

    results = [
        {
            "id": "5",
            "name": "Galaxy Book4",
            "category": "Laptops",
            "use_cases": "office work, studying, browsing",
            "tags": "laptop, windows, productivity",
            "target_audience": "students, professionals",
            "@search.score": 0.0333,
        },
        {
            "id": "4",
            "name": "MacBook Air M3",
            "category": "Laptops",
            "use_cases": "programming, studying, office work",
            "tags": "laptop, productivity, portable, programming",
            "target_audience": "students, developers, professionals",
            "@search.score": 0.0328,
        },
    ]

    ranked = rerank_products(
        results,
        intent,
    )

    assert ranked[0]["id"] == "4"
    assert ranked[0]["use_case_score"] == 1.0


def test_category_match_is_applied():
    intent = understand_query(
        "laptop"
    )

    results = [
        {
            "id": "1",
            "name": "Random Product",
            "category": "Backpacks",
            "use_cases": None,
            "tags": None,
            "target_audience": None,
            "@search.score": 0.03,
        },
        {
            "id": "2",
            "name": "Laptop Product",
            "category": "Laptops",
            "use_cases": "office work",
            "tags": "laptop",
            "target_audience": "professionals",
            "@search.score": 0.02,
        },
    ]

    ranked = rerank_products(
        results,
        intent,
    )

    assert ranked[0]["id"] == "2"
    assert ranked[0]["category_score"] == 1.0


def test_travel_use_case_ranking():
    intent = understand_query(
        "something nice for travel"
    )

    results = [
        {
            "id": "10",
            "name": "Travel Backpack",
            "category": "Backpacks",
            "use_cases": "commuting, travel, school, office",
            "tags": "travel, backpack",
            "target_audience": "travelers",
            "@search.score": 0.03,
        },
        {
            "id": "20",
            "name": "Random Product",
            "category": "Books",
            "use_cases": "reading",
            "tags": "books",
            "target_audience": "readers",
            "@search.score": 0.03,
        },
    ]

    ranked = rerank_products(
        results,
        intent,
    )

    assert ranked[0]["id"] == "10"
    assert ranked[0]["use_case_score"] == 1.0

def test_price_range_match_reason():
    intent = understand_query(
        "laptop between $700 and $1,000"
    )

    results = [
        {
            "id": "5",
            "name": "Galaxy Book4",
            "category": "Laptops",
            "price": 849.99,
            "use_cases": "office work, studying",
            "tags": "laptop, windows",
            "target_audience": "students, professionals",
            "@search.score": 0.03,
        },
        {
            "id": "6",
            "name": "Expensive Laptop",
            "category": "Laptops",
            "price": 1299.99,
            "use_cases": "programming",
            "tags": "laptop",
            "target_audience": "developers",
            "@search.score": 0.03,
        },
    ]

    ranked = rerank_products(
        results,
        intent,
    )

    assert ranked[0]["id"] == "5"

    assert (
        "Within $700–$1,000 price range"
        in ranked[0]["match_reasons"]
    )

    assert (
        "Within $700–$1,000 price range"
        not in ranked[1]["match_reasons"]
    )