from app.models.product import Product
from scripts.enrich_products import build_search_text


def test_product_search_text_contains_metadata(test_db):
    product = Product(
        name="Test Running Shoes",
        description="Lightweight shoes for daily running.",
        brand="TestBrand",
        category="Running Shoes",
        subcategory="Road Running",
        price=89.99,
        tags="running, fitness, lightweight",
        features="cushioned sole, breathable mesh",
        target_audience="runners, athletes",
        use_cases="daily running, training",
        color="Black",
        material="Mesh",
    )

    product.search_text = build_search_text(product)

    test_db.add(product)
    test_db.commit()
    test_db.refresh(product)

    assert product.search_text
    assert product.name in product.search_text
    assert product.brand in product.search_text
    assert product.category in product.search_text
    assert product.subcategory in product.search_text
    assert product.tags in product.search_text
    assert product.features in product.search_text
    assert product.use_cases in product.search_text


def test_search_text_changes_when_product_metadata_changes(test_db):
    product = Product(
        name="Test Laptop",
        description="Portable laptop for productivity.",
        brand="TestBrand",
        category="Laptops",
        subcategory="Ultrabook",
        price=999.99,
        tags="laptop, productivity",
        features="lightweight, long battery life",
        target_audience="students, professionals",
        use_cases="programming, studying",
        color="Silver",
        material="Aluminum",
    )

    product.search_text = build_search_text(product)

    assert "Test Laptop" in product.search_text
    assert "Laptops" in product.search_text
    assert "programming, studying" in product.search_text
