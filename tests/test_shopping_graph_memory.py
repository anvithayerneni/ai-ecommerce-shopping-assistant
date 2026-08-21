from unittest.mock import patch

from app.agents.shopping_graph import shopping_graph


def fake_run_shopping_agent(query: str):
    class FakeResult:
        content = f"Mock shopping response for: {query}"
        tool_calls = []

    return FakeResult()


def test_shopping_graph_preserves_conversation_memory():
    config = {
        "configurable": {
            "thread_id": "memory-test-user",
        }
    }

    with patch(
        "app.agents.agent_node.run_shopping_agent",
        side_effect=fake_run_shopping_agent,
    ):
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

        assert len(
            second_turn["conversation_history"]
        ) >= 3
