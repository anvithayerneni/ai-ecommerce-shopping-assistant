import pytest
from fastapi.testclient import TestClient

from app.db.session import get_db
from app.main import app


@pytest.fixture
def client(test_db):
    def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_product(client):
    response = client.post(
        "/products",
        json={
            "name": "Test Running Shoes",
            "description": "Lightweight test shoes",
            "brand": "TestBrand",
            "category": "Running Shoes",
            "price": 79.99,
            "rating": 4.2,
            "stock": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Running Shoes"
    assert data["brand"] == "TestBrand"
    assert data["price"] == 79.99


def test_get_products(client):
    response = client.get("/products")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_product_not_found(client):
    response = client.get("/products/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product not found"


def test_create_product_validation_error(client):
    response = client.post(
        "/products",
        json={
            "name": "Invalid Product",
            "price": "not-a-number",
            "stock": 10,
        },
    )

    assert response.status_code == 422