from __future__ import annotations

from app.agents.shopping_agent import run_shopping_agent


def run_agent_node(
    state: dict,
) -> dict:
    """
    Run the tool-calling shopping agent using the
    current user query.
    """

    query = state["query"].strip()

    result = run_shopping_agent(query)

    return {
        **state,
        "agent_response": result.content,
        "agent_tool_calls": result.tool_calls,
    }
