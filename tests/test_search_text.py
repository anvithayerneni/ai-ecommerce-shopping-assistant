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

def test_semantic_product_search(client):
    response = client.get(
        "/products/search?q=running%20shoes%20for%20training&top_k=3"
    )

    assert response.status_code == 200

    results = response.json()

    assert len(results) == 3
    assert results[0]["product_id"] in {1, 3}
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