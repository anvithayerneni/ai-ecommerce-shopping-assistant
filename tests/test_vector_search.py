from app.services.vector_search import search_products


def test_running_shoes_semantic_search():
    results = search_products(
        "running shoes for training",
        top_k=3,
    )

    assert len(results) == 3
    assert results[0]["product_id"] in {1, 3}


def test_headphones_semantic_search():
    results = search_products(
        "wireless noise cancelling headphones",
        top_k=3,
    )

    assert len(results) == 3
    assert results[0]["product_id"] in {6, 7}


def test_laptop_semantic_search():
    results = search_products(
        "laptop for work",
        top_k=3,
    )

    assert len(results) == 3
    assert results[0]["product_id"] in {4, 5}