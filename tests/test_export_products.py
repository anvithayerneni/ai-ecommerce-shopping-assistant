import json

from app.models.product import Product
from scripts.export_products_for_embedding import export_products


def test_export_products_creates_valid_json(
    test_db,
    tmp_path,
    monkeypatch,
):
    output_file = tmp_path / "products_for_embedding.json"

    product = Product(
        name="Test Laptop",
        description="Portable laptop for programming.",
        brand="TestBrand",
        category="Laptops",
        subcategory="Ultrabook",
        price=899.99,
        rating=4.5,
        stock=10,
        tags="laptop, programming, portable",
        features="long battery life, lightweight",
        target_audience="developers, students",
        use_cases="programming, studying",
        color="Silver",
        material="Aluminum",
        search_text=(
            "Test Laptop TestBrand Laptops Ultrabook "
            "Portable laptop for programming."
        ),
    )

    test_db.add(product)
    test_db.commit()

    monkeypatch.setattr(
        "scripts.export_products_for_embedding.SessionLocal",
        lambda: test_db,
    )

    monkeypatch.setattr(
        "scripts.export_products_for_embedding.OUTPUT_FILE",
        output_file,
    )

    export_products()

    assert output_file.exists()

    with output_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        products = json.load(file)

    assert isinstance(products, list)
    assert len(products) == 1

    exported_product = products[0]

    assert exported_product["product_id"] == product.id
    assert exported_product["name"] == "Test Laptop"
    assert exported_product["search_text"]
    assert exported_product["category"] == "Laptops"
    assert exported_product["brand"] == "TestBrand"
    assert exported_product["price"] == 899.99