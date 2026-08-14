from scripts.normalize_real_products import (
    extract_price,
    normalize_product,
)


def test_extract_price():
    assert extract_price("Product costs $43.99") == 43.99


def test_extract_price_with_comma():
    assert extract_price("Product costs $1,299.99") == 1299.99


def test_extract_price_missing():
    assert extract_price("Product has no listed price") is None


def test_normalize_product():
    product = {
        "uid": "test-123",
        "vendor": "Test Brand",
        "title": "Test Product",
        "paragraph": "Test Product by Test Brand - $49.99",
        "embedding": [0.1] * 384,
    }

    result = normalize_product(product)

    assert result["external_id"] == "test-123"
    assert result["name"] == "Test Product"
    assert result["brand"] == "Test Brand"
    assert result["price"] == 49.99
    assert result["description"] == product["paragraph"]
    assert len(result["source_embedding"]) == 384