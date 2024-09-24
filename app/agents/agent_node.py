from __future__ import annotations

from app.agents.shopping_agent import (
    run_shopping_agent,
)


def run_agent_node(
    state: dict,
) -> dict:
    """
    Run the tool-calling shopping agent.

    Pass the existing conversation history so that
    follow-up questions can refer to products discussed
    in the previous turn.
    """

    query = state["query"].strip()

    conversation_history = state.get(
        "conversation_history",
        [],
    )

    try:
        result = run_shopping_agent(
            query=query,
            conversation_history=conversation_history,
        )
        agent_response = result.content
        agent_tool_calls = getattr(result, "tool_calls", [])
    except Exception:
        agent_response = None
        agent_tool_calls = []

    return {
        **state,
        "agent_response": agent_response,
        "agent_tool_calls": agent_tool_calls,
    }