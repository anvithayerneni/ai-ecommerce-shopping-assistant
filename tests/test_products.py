import pytest




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

    assert data["search_text"]
    assert "Test Running Shoes" in data["search_text"]
    assert "TestBrand" in data["search_text"]
    assert "Running Shoes" in data["search_text"]
    assert "Lightweight test shoes" in data["search_text"]


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

def test_get_products_with_category_filter(client):
    client.post(
        "/products",
        json={
            "name": "Test Laptop",
            "description": "Portable laptop",
            "brand": "TestBrand",
            "category": "Laptops",
            "price": 999.99,
            "rating": 4.5,
            "stock": 10,
        },
    )

    client.post(
        "/products",
        json={
            "name": "Test Shoes",
            "description": "Running shoes",
            "brand": "TestBrand",
            "category": "Running Shoes",
            "price": 79.99,
            "rating": 4.2,
            "stock": 10,
        },
    )

    response = client.get("/products?category=Laptops")

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 1
    assert products[0]["name"] == "Test Laptop"


def test_get_products_with_price_and_rating_filters(client):
    client.post(
        "/products",
        json={
            "name": "Premium Laptop",
            "description": "High-end laptop",
            "brand": "TestBrand",
            "category": "Laptops",
            "price": 1200.00,
            "rating": 4.8,
            "stock": 5,
        },
    )

    client.post(
        "/products",
        json={
            "name": "Budget Laptop",
            "description": "Affordable laptop",
            "brand": "TestBrand",
            "category": "Laptops",
            "price": 400.00,
            "rating": 4.6,
            "stock": 20,
        },
    )

    response = client.get(
        "/products?max_price=1000&min_rating=4.5"
    )

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 1
    assert products[0]["name"] == "Budget Laptop"

def test_get_products_with_pagination(client):
    for i in range(5):
        client.post(
            "/products",
            json={
                "name": f"Pagination Product {i}",
                "description": "Test product",
                "brand": "TestBrand",
                "category": "Testing",
                "price": 50.00 + i,
                "rating": 4.0,
                "stock": 10,
            },
        )

    response = client.get("/products?skip=0&limit=2")

    assert response.status_code == 200

    products = response.json()

    assert len(products) == 2


def test_get_products_pagination_validation(client):
    response = client.get("/products?skip=-1")

    assert response.status_code == 422

    response = client.get("/products?limit=101")

    assert response.status_code == 422

def test_get_products_sorted_by_price_ascending(client):
    client.post(
        "/products",
        json={
            "name": "Expensive Product",
            "description": "Expensive test product",
            "brand": "TestBrand",
            "category": "Testing",
            "price": 200.00,
            "rating": 4.0,
            "stock": 10,
        },
    )

    client.post(
        "/products",
        json={
            "name": "Cheap Product",
            "description": "Cheap test product",
            "brand": "TestBrand",
            "category": "Testing",
            "price": 50.00,
            "rating": 4.0,
            "stock": 10,
        },
    )

    response = client.get(
        "/products?sort_by=price&sort_order=asc"
    )

    assert response.status_code == 200

    products = response.json()

    assert products[0]["name"] == "Cheap Product"


def test_get_products_sorted_by_rating_descending(client):
    client.post(
        "/products",
        json={
            "name": "Low Rated Product",
            "description": "Lower rated test product",
            "brand": "TestBrand",
            "category": "Testing",
            "price": 100.00,
            "rating": 3.5,
            "stock": 10,
        },
    )

    client.post(
        "/products",
        json={
            "name": "Highly Rated Product",
            "description": "Highly rated test product",
            "brand": "TestBrand",
            "category": "Testing",
            "price": 100.00,
            "rating": 4.9,
            "stock": 10,
        },
    )

    response = client.get(
        "/products?sort_by=rating&sort_order=desc"
    )

    assert response.status_code == 200

    products = response.json()

    assert products[0]["name"] == "Highly Rated Product"


def test_get_products_invalid_sort_parameters(client):
    response = client.get(
        "/products?sort_by=banana"
    )

    assert response.status_code == 422

    response = client.get(
        "/products?sort_order=sideways"
    )

    assert response.status_code == 422

def test_create_product_database_error(client, monkeypatch):
    from app.api import products

    def mock_create_product(db, product_data):
        raise RuntimeError("Database connection failed")

    monkeypatch.setattr(
        products,
        "create_product",
        mock_create_product,
    )

    response = client.post(
        "/products",
        json={
            "name": "Failure Product",
            "description": "Test failure handling",
            "brand": "TestBrand",
            "category": "Testing",
            "price": 50.00,
            "rating": 4.0,
            "stock": 10,
        },
    )

    assert response.status_code == 500


def test_get_products_invalid_price_range(client):
    response = client.get(
        "/products?min_price=1000&max_price=500"
    )

    assert response.status_code == 422