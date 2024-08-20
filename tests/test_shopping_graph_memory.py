from unittest.mock import patch

from app.agents.shopping_graph import shopping_graph


def fake_run_shopping_agent(query: str):
    class FakeResult:
        content = f"Mock shopping response for: {query}"
        tool_calls = []

    return FakeResult()


def fake_search_products(
    query: str,
    top_k: int = 5,
):
    """
    Deterministic product data for the memory test.

    This prevents the test from calling Azure AI Search.
    """

    query_lower = query.lower()

    macbook = {
        "id": "4",
        "name": "MacBook Air M3",
        "brand": "Apple",
        "category": "Laptops",
        "price": 999.99,
        "rating": 4.8,
        "tags": (
            "laptop, productivity, portable, programming"
        ),
        "features": (
            "Apple silicon, long battery life, "
            "lightweight design"
        ),
        "target_audience": (
            "students, developers, professionals"
        ),
        "use_cases": (
            "programming, studying, office work, travel"
        ),
        "rerank_score": 0.32,
        "match_reasons": [
            "Matches Laptops category",
            "Supports programming",
            "Within $1,000 budget",
        ],
    }

    galaxy = {
        "id": "5",
        "name": "Galaxy Book4",
        "brand": "Samsung",
        "category": "Laptops",
        "price": 849.99,
        "rating": 4.4,
        "tags": (
            "laptop, windows, productivity, portable"
        ),
        "features": (
            "portable design, high-resolution display, "
            "multitasking"
        ),
        "target_audience": (
            "students, professionals, business users"
        ),
        "use_cases": (
            "office work, studying, browsing, productivity"
        ),
        "rerank_score": 0.17,
        "match_reasons": [
            "Matches Laptops category",
            "Within $1,000 budget",
        ],
    }

    if "cheaper" in query_lower:
        return [galaxy]

    return [
        macbook,
        galaxy,
    ]


def fake_generate_response(
    prompt: str,
    max_output_tokens: int = 200,
):
    """
    Deterministic response for the memory test.

    This prevents the test from calling OpenAI/Azure OpenAI.
    """

    return "Mock grounded shopping response."


def test_shopping_graph_preserves_conversation_memory():
    config = {
        "configurable": {
            "thread_id": "memory-test-user",
        }
    }

    with (
        patch(
            "app.agents.agent_node.run_shopping_agent",
            side_effect=fake_run_shopping_agent,
        ),
        patch(
            "app.agents.shopping_graph.search_products",
            side_effect=fake_search_products,
        ),
        patch(
            "app.agents.shopping_graph.generate_response",
            side_effect=fake_generate_response,
        ),
    ):
        # ----------------------------------------------------
        # FIRST TURN
        # ----------------------------------------------------

        first_turn = shopping_graph.invoke(
            {
                "query": "laptop under $1000 for programming",
                "top_k": 5,
            },
            config,
        )

        assert first_turn["query"] == (
            "laptop under $1000 for programming"
        )

        assert first_turn["recommendations"]

        # ----------------------------------------------------
        # SECOND TURN
        # ----------------------------------------------------

        second_turn = shopping_graph.invoke(
            {
                "query": "show me cheaper ones",
                "top_k": 5,
            },
            config,
        )

        assert second_turn["query"] == (
            "show me cheaper ones"
        )

        assert second_turn["resolved_query"]

        assert second_turn["followup_type"] == "cheaper"

        assert second_turn["recommendations"]

        # The cheaper follow-up should return Galaxy Book4.
        assert (
            second_turn["recommendations"][0]["product"]["name"]
            == "Galaxy Book4"
        )

        # Conversation memory should contain the previous
        # user/assistant interaction and the current turn.
        assert len(
            second_turn["conversation_history"]
        ) >= 3
