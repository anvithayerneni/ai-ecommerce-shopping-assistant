from app.services.query_understanding import understand_query


def test_running_shoes_query():
    intent = understand_query(
        "comfortable running shoes for training"
    )

    assert intent.category == "Running Shoes"
    assert intent.use_case == "training"
    assert intent.max_price is None
    assert intent.min_rating is None


def test_laptop_programming_budget():
    intent = understand_query(
        "laptop for programming under $900"
    )

    assert intent.category == "Laptops"
    assert intent.use_case == "programming"
    assert intent.max_price == 900.0
    assert intent.min_rating is None


def test_laptop_rating_filter():
    intent = understand_query(
        "laptop under $1,000 with rating above 4.5"
    )

    assert intent.category == "Laptops"
    assert intent.max_price == 1000.0
    assert intent.min_rating == 4.5


def test_travel_query():
    intent = understand_query(
        "something nice for travel"
    )

    assert intent.category is None
    assert intent.use_case == "travel"


def test_no_filters():
    intent = understand_query(
        "something nice"
    )

    assert intent.category is None
    assert intent.use_case is None
    assert intent.max_price is None
    assert intent.min_rating is None

def test_laptop_price_range():
    intent = understand_query(
        "laptop between $700 and $1,000"
    )

    assert intent.category == "Laptops"
    assert intent.min_price == 700.0
    assert intent.max_price == 1000.0
    assert intent.use_case is None
    assert intent.min_rating is None