from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_search_endpoint_requires_query():
    response = client.get("/products/search")

    assert response.status_code == 422


def test_search_endpoint_validates_top_k():
    response = client.get(
        "/products/search?q=laptop&top_k=0"
    )

    assert response.status_code == 422


def test_search_endpoint_validates_query_length():
    response = client.get(
        "/products/search?q=a"
    )

    assert response.status_code == 422