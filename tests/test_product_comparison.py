from app.tools.product_compare import compare_products


def make_product(
    product_id,
    name,
    brand,
    price,
    rating,
    features,
    target_audience,
    use_cases,
):
    return {
        "id": product_id,
        "name": name,
        "brand": brand,
        "category": "Laptops",
        "subcategory": "Laptop",
        "price": price,
        "rating": rating,
        "stock": 10,
        "features": features,
        "target_audience": target_audience,
        "use_cases": use_cases,
    }


def test_comparison_returns_both_products():
    products = [
        make_product(
            4,
            "MacBook Air M3",
            "Apple",
            999.99,
            4.8,
            "Apple silicon, long battery life, lightweight design",
            "students, developers, professionals",
            "programming, studying, office work, productivity",
        ),
        make_product(
            5,
            "Galaxy Book4",
            "Samsung",
            849.99,
            4.4,
            "portable design, high-resolution display, multitasking",
            "students, professionals, business users",
            "office work, studying, browsing, productivity",
        ),
    ]

    result = compare_products(products)

    names = [
        product["name"]
        for product in result["comparison"]
    ]

    assert names == [
        "MacBook Air M3",
        "Galaxy Book4",
    ]


def test_cheapest_product_is_galaxy_book4():
    products = [
        make_product(
            4,
            "MacBook Air M3",
            "Apple",
            999.99,
            4.8,
            "Apple silicon, long battery life, lightweight design",
            "students, developers, professionals",
            "programming, studying, office work, productivity",
        ),
        make_product(
            5,
            "Galaxy Book4",
            "Samsung",
            849.99,
            4.4,
            "portable design, high-resolution display, multitasking",
            "students, professionals, business users",
            "office work, studying, browsing, productivity",
        ),
    ]

    result = compare_products(products)

    assert result["cheapest"]["name"] == "Galaxy Book4"
    assert result["cheapest"]["price"] == 849.99


def test_highest_rated_product_is_macbook_air_m3():
    products = [
        make_product(
            4,
            "MacBook Air M3",
            "Apple",
            999.99,
            4.8,
            "Apple silicon, long battery life, lightweight design",
            "students, developers, professionals",
            "programming, studying, office work, productivity",
        ),
        make_product(
            5,
            "Galaxy Book4",
            "Samsung",
            849.99,
            4.4,
            "portable design, high-resolution display, multitasking",
            "students, professionals, business users",
            "office work, studying, browsing, productivity",
        ),
    ]

    result = compare_products(products)

    assert result["highest_rated"]["name"] == "MacBook Air M3"
    assert result["highest_rated"]["rating"] == 4.8


def test_programming_support_is_product_specific():
    products = [
        make_product(
            4,
            "MacBook Air M3",
            "Apple",
            999.99,
            4.8,
            "Apple silicon, long battery life, lightweight design",
            "students, developers, professionals",
            "programming, studying, office work, productivity",
        ),
        make_product(
            5,
            "Galaxy Book4",
            "Samsung",
            849.99,
            4.4,
            "portable design, high-resolution display, multitasking",
            "students, professionals, business users",
            "office work, studying, browsing, productivity",
        ),
    ]

    result = compare_products(products)

    comparison = result["comparison"]

    macbook = comparison[0]
    galaxy = comparison[1]

    assert macbook["programming_supported"] is True
    assert macbook["programming_support_status"] == "confirmed"

    assert galaxy["programming_supported"] is False
    assert galaxy["programming_support_status"] == "not_confirmed"


def test_missing_use_case_is_not_inferred():
    products = [
        make_product(
            5,
            "Galaxy Book4",
            "Samsung",
            849.99,
            4.4,
            "portable design, high-resolution display, multitasking",
            "students, professionals, business users",
            "office work, studying, browsing, productivity",
        ),
    ]

    result = compare_products(products)

    galaxy = result["comparison"][0]

    assert galaxy["programming_supported"] is False
    assert (
        "does not explicitly list programming"
        in galaxy["grounded_use_case_statement"]
    )


def test_empty_comparison_is_safe():
    result = compare_products([])

    assert result["products"] == []
    assert result["comparison"] == []
    assert result["cheapest"] is None
    assert result["highest_rated"] is None
    assert result["use_case_comparison"] == {}
