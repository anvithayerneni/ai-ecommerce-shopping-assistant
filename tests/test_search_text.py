from app.models.product import Product
from app.services.product_service import build_search_text


def test_build_search_text_contains_product_information():
    product = Product(
        name="Test Laptop",
        description="Portable laptop for programming.",
        brand="TestBrand",
        category="Laptops",
        subcategory="Ultrabook",
        price=999.99,
        rating=4.5,
        stock=10,
        tags="laptop, programming, portable",
        features="long battery life, lightweight",
        target_audience="developers, students",
        use_cases="programming, studying",
        color="Silver",
        material="Aluminum",
    )

    search_text = build_search_text(product)

    assert "Test Laptop" in search_text
    assert "TestBrand" in search_text
    assert "Laptops" in search_text
    assert "Ultrabook" in search_text
    assert "Portable laptop for programming." in search_text
    assert "laptop, programming, portable" in search_text
    assert "long battery life, lightweight" in search_text
    assert "developers, students" in search_text
    assert "programming, studying" in search_text
    assert "Silver" in search_text
    assert "Aluminum" in search_text


def test_semantic_product_search(client, monkeypatch):
    from app.services import search_service

    mock_results = [
        {
            "id": "1",
            "name": "Running Shoe A",
            "brand": "TestBrand",
            "category": "Running Shoes",
            "price": 79.99,
            "rating": 4.5,
            "rerank_score": 0.9,
            "match_reasons": [
                "Matches Running Shoes category",
                "Supports training",
            ],
        },
        {
            "id": "3",
            "name": "Running Shoe B",
            "brand": "TestBrand",
            "category": "Running Shoes",
            "price": 89.99,
            "rating": 4.4,
            "rerank_score": 0.8,
            "match_reasons": [
                "Matches Running Shoes category",
                "Supports training",
            ],
        },
    ]

    monkeypatch.setattr(
        search_service,
        "search_products",
        lambda query, top_k: mock_results,
    )

    response = client.get(
        "/products/search?q=running%20shoes%20for%20training&top_k=3"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "running shoes for training"

    results = data["results"]

    assert len(results) == 2
    assert int(results[0]["id"]) in {1, 3}
    assert "score" in results[0]


def test_semantic_product_search_validation(client):
    response = client.get(
        "/products/search?q=a&top_k=3"
    )

    assert response.status_code == 422

    response = client.get(
        "/products/search?q=running%20shoes&top_k=0"
    )

    assert response.status_code == 422


def test_semantic_search_price_range_filter(monkeypatch):
    from app.services import search_service

    captured = {}

    class FakeSearchClient:
        def search(self, **kwargs):
            captured.update(kwargs)
            return []

    monkeypatch.setattr(
        search_service,
        "search_client",
        FakeSearchClient(),
    )

    search_service.search_products(
        query="laptop between $700 and $1,000",
        top_k=5,
    )

    assert captured["filter"] == (
        "category eq 'Laptops' "
        "and price ge 700.0 "
        "and price le 1000.0"
    )