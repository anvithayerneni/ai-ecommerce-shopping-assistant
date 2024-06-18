from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

from app.tools.product_details import get_product_details


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# AZURE OPENAI
# ============================================================

def get_llm() -> AzureChatOpenAI:
    """
    Lazily create the Azure OpenAI client.

    The client is NOT created during module import.
    This is important because GitHub Actions runs tests without
    the local Azure OpenAI credentials.
    """

    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    api_version = os.getenv(
        "AZURE_OPENAI_API_VERSION",
        "2024-02-15-preview",
    )
    deployment = os.getenv(
        "AZURE_OPENAI_DEPLOYMENT"
    )

    missing = []

    if not endpoint:
        missing.append(
            "AZURE_OPENAI_ENDPOINT"
        )

    if not api_key:
        missing.append(
            "AZURE_OPENAI_API_KEY"
        )

    if not deployment:
        missing.append(
            "AZURE_OPENAI_DEPLOYMENT"
        )

    if missing:
        raise RuntimeError(
            "Azure OpenAI configuration is missing: "
            + ", ".join(missing)
            + ". "
            "Set these environment variables before "
            "running the shopping agent."
        )

    return AzureChatOpenAI(
        azure_endpoint=endpoint,
        api_key=api_key,
        api_version=api_version,
        azure_deployment=deployment,
        temperature=0,
    )


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI-powered e-commerce shopping assistant.

You help users search for products, compare products,
understand product differences, and make shopping decisions.

IMPORTANT RULES:

1. Use the available product tools whenever the user refers
   to specific product IDs.

2. If the user asks to compare products, retrieve the actual
   product details before answering.

3. Never invent product information.

4. Base comparisons on information returned by the tools.

5. When comparing products, clearly mention:
   - Product name
   - Price
   - Rating
   - Brand
   - Category
   - Features
   - Target audience
   - Use cases
   - Stock when relevant

6. If the user asks which product is cheaper, identify the
   lower-priced product.

7. If the user asks which product is better rated, identify
   the product with the higher rating.

8. If a requested product cannot be found, clearly say so.

9. Keep responses concise but useful.

10. When product IDs are mentioned, interpret them as database
    product IDs and use the product-details tool.
"""


# ============================================================
# TOOL CONFIGURATION
# ============================================================

TOOLS = [
    get_product_details,
]


# ============================================================
# SHOPPING AGENT
# ============================================================

def run_shopping_agent(
    query: str,
):
    """
    Run the tool-calling shopping agent.

    The Azure client is created lazily so importing this module
    does not require Azure credentials.

    The returned object is the final LangChain AIMessage.

    agent_node.py expects:

        result.content
        result.tool_calls
    """

    llm = get_llm()

    # Bind the product tools to the model.
    llm_with_tools = llm.bind_tools(
        TOOLS
    )

    messages = [
        (
            "system",
            SYSTEM_PROMPT,
        ),
        (
            "human",
            query,
        ),
    ]

    # --------------------------------------------------------
    # First model call
    # --------------------------------------------------------

    result = llm_with_tools.invoke(
        messages
    )

    # --------------------------------------------------------
    # Tool-calling loop
    #
    # The model may request one or more tools.
    # Execute them and send the results back to the model.
    # --------------------------------------------------------

    max_tool_rounds = 5

    for _ in range(max_tool_rounds):

        tool_calls = getattr(
            result,
            "tool_calls",
            [],
        )

        if not tool_calls:
            break

        messages.append(
            result
        )

        for tool_call in tool_calls:

            tool_name = tool_call.get(
                "name"
            )

            tool_args = tool_call.get(
                "args",
                {},
            )

            tool_call_id = tool_call.get(
                "id"
            )

            # ------------------------------------------------
            # PRODUCT DETAILS TOOL
            # ------------------------------------------------

            if tool_name == "get_product_details":

                tool_result = (
                    get_product_details.invoke(
                        tool_args
                    )
                )

                from langchain_core.messages import (
                    ToolMessage,
                )

                messages.append(
                    ToolMessage(
                        content=str(
                            tool_result
                        ),
                        tool_call_id=(
                            tool_call_id
                        ),
                    )
                )

            else:

                from langchain_core.messages import (
                    ToolMessage,
                )

                messages.append(
                    ToolMessage(
                        content=(
                            f"Unknown tool: "
                            f"{tool_name}"
                        ),
                        tool_call_id=(
                            tool_call_id
                        ),
                    )
                )

        # ----------------------------------------------------
        # Ask the model to produce the final answer
        # using the retrieved tool information.
        # ----------------------------------------------------

        result = llm_with_tools.invoke(
            messages
        )

    return result