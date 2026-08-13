import json

from scripts.export_products_for_embedding import export_products


def test_export_products_creates_valid_json(tmp_path, monkeypatch):
    output_file = tmp_path / "products_for_embedding.json"

    monkeypatch.setattr(
        "scripts.export_products_for_embedding.OUTPUT_FILE",
        output_file,
    )

    export_products()

    assert output_file.exists()

    with output_file.open("r", encoding="utf-8") as file:
        products = json.load(file)

    assert isinstance(products, list)
    assert len(products) > 0

    for product in products:
        assert product["product_id"] is not None
        assert product["name"]
        assert product["search_text"]
        assert product["category"]
        assert product["brand"]
        assert product["price"] >= 0