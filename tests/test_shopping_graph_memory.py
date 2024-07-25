from app.agents import shopping_graph as shopping_graph_module


def test_shopping_graph_preserves_conversation_memory(
    monkeypatch,
):
    """
    Verify that the shopping graph preserves conversation
    history and resolves a follow-up request using the
    previous turn.

    The LLM-backed agent is mocked because this is a graph
    memory test, not an Azure OpenAI integration test.
    """

    def mock_agent_node(state):
        """
        Mock the LLM agent so CI does not require Azure
        OpenAI credentials.
        """

        return {
            **state,
            "agent_response": "Mock shopping agent response.",
            "agent_tool_calls": [],
        }

    monkeypatch.setattr(
        shopping_graph_module,
        "agent_node",
        mock_agent_node,
    )

    config = {
        "configurable": {
            "thread_id": "memory-test-user",
        }
    }

    # --------------------------------------------------------
    # First turn
    # --------------------------------------------------------

    first_turn = shopping_graph_module.shopping_graph.invoke(
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

    # --------------------------------------------------------
    # Second turn
    # --------------------------------------------------------

    second_turn = shopping_graph_module.shopping_graph.invoke(
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

    # User + assistant messages from both turns
    # should be preserved.
    assert len(
        second_turn["conversation_history"]
    ) >= 3