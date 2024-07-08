from app.tools.product_compare import compare_products


def test_compare_products_identifies_cheapest_and_highest_rated():
    products = [
        {
            "id": "1",
            "name": "MacBook Air M3",
            "brand": "Apple",
            "category": "Laptops",
            "price": 999.99,
            "rating": 4.8,
            "features": "Apple silicon, long battery life",
            "use_cases": "programming, studying",
        },
        {
            "id": "2",
            "name": "Galaxy Book4",
            "brand": "Samsung",
            "category": "Laptops",
            "price": 849.99,
            "rating": 4.4,
            "features": "portable design, multitasking",
            "use_cases": "studying, office work",
        },
    ]

    result = compare_products(products)

    assert result["cheapest"]["name"] == "Galaxy Book4"
    assert result["cheapest"]["price"] == 849.99

    assert result["highest_rated"]["name"] == "MacBook Air M3"
    assert result["highest_rated"]["rating"] == 4.8


def test_compare_products_does_not_infer_programming_support():
    products = [
        {
            "id": "1",
            "name": "MacBook Air M3",
            "category": "Laptops",
            "price": 999.99,
            "rating": 4.8,
            "use_cases": "programming, studying",
        },
        {
            "id": "2",
            "name": "Galaxy Book4",
            "category": "Laptops",
            "price": 849.99,
            "rating": 4.4,
            "use_cases": "studying, office work",
        },
    ]

    result = compare_products(products)

    comparison = result["comparison"]

    macbook = next(
        item for item in comparison
        if item["name"] == "MacBook Air M3"
    )

    galaxy = next(
        item for item in comparison
        if item["name"] == "Galaxy Book4"
    )

    assert macbook["programming_supported"] is True
    assert macbook["programming_support_status"] == "confirmed"

    assert galaxy["programming_supported"] is False
    assert galaxy["programming_support_status"] == "not_confirmed"


def test_compare_products_keeps_product_attributes_separate():
    products = [
        {
            "id": "1",
            "name": "Programming Laptop",
            "category": "Laptops",
            "price": 999.99,
            "use_cases": "programming",
            "features": "long battery life",
        },
        {
            "id": "2",
            "name": "Office Laptop",
            "category": "Laptops",
            "price": 799.99,
            "use_cases": "office work",
            "features": "large display",
        },
    ]

    result = compare_products(products)

    first = result["comparison"][0]
    second = result["comparison"][1]

    assert "programming" in first["use_cases"]
    assert "programming" not in second["use_cases"]

    assert "long battery life" in first["features"]
    assert "long battery life" not in second["features"]

    assert second["programming_supported"] is False


def test_compare_products_handles_missing_data():
    products = [
        {
            "id": "1",
            "name": "Unknown Laptop",
            "category": "Laptops",
            "price": 700.00,
            "rating": None,
            "use_cases": None,
            "features": None,
        }
    ]

    result = compare_products(products)

    product = result["comparison"][0]

    assert product["use_cases"] == []
    assert product["features"] == []

    assert product["programming_supported"] is False
    assert product["programming_support_status"] == "not_confirmed"

    assert result["cheapest"]["name"] == "Unknown Laptop"
    assert result["highest_rated"] is None


def test_compare_products_handles_empty_input():
    result = compare_products([])

    assert result["products"] == []
    assert result["comparison"] == []
    assert result["cheapest"] is None
    assert result["highest_rated"] is None
    assert result["use_case_comparison"] == {}
