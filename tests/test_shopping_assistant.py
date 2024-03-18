from app.services.shopping_assistant import get_recommendations


def test_get_recommendations_returns_expected_structure(monkeypatch):
    mock_results = [
        {
            "id": "5",
            "name": "Galaxy Book4",
            "brand": "Samsung",
            "category": "Laptops",
            "price": 849.99,
            "rating": 4.4,
            "rerank_score": 0.17,
            "match_reasons": [
                "Matches Laptops category",
                "Within $900 budget",
            ],
        }
    ]

    monkeypatch.setattr(
        "app.services.shopping_assistant.search_products",
        lambda query, top_k: mock_results,
    )

    result = get_recommendations(
        "laptop for programming under $900",
        top_k=5,
    )

    assert result["query"] == "laptop for programming under $900"
    assert len(result["recommendations"]) == 1

    recommendation = result["recommendations"][0]

    assert recommendation["product"]["id"] == "5"
    assert recommendation["product"]["name"] == "Galaxy Book4"
    assert recommendation["product"]["brand"] == "Samsung"
    assert recommendation["product"]["category"] == "Laptops"
    assert recommendation["product"]["price"] == 849.99
    assert recommendation["product"]["rating"] == 4.4

    assert recommendation["score"] == 0.17
    assert "Matches Laptops category" in recommendation["match_reasons"]
    assert "Within $900 budget" in recommendation["match_reasons"]