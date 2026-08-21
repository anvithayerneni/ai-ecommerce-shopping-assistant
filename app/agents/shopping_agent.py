from __future__ import annotations

import os

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import ToolMessage

from app.tools.product_details import (
    get_product_details,
)

from app.tools.shopping_tools import (
    compare_catalog_products,
)


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

    endpoint = os.getenv(
        "AZURE_OPENAI_ENDPOINT"
    )

    api_key = os.getenv(
        "AZURE_OPENAI_API_KEY"
    )

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

You help users:

- search for products
- compare products
- understand product differences
- identify cheaper products
- identify higher-rated products
- make shopping decisions

IMPORTANT RULES:

1. Use the available product tools whenever the user refers
   to specific product IDs.

2. If the user asks to compare specific products, use the
   compare_catalog_products tool whenever possible.

3. If the user provides product names instead of product IDs,
   use the available product search/recommendation system to
   identify the relevant products before comparing them.

4. Never invent product information.

5. Base comparisons only on information returned by the tools.

6. When comparing products, clearly mention when available:

   - Product name
   - Price
   - Rating
   - Brand
   - Category
   - Features
   - Target audience
   - Use cases

7. If the user asks which product is cheaper, identify the
   lower-priced product using the actual catalog prices.

8. If the user asks which product is better rated, identify
   the product with the higher catalog rating.

9. If a requested product cannot be found, clearly say so.

10. Do not assume that two products are equivalent merely
    because they belong to the same category.

11. Do not invent specifications, operating systems,
    processors, display specifications, battery life,
    performance claims, or other product attributes.

12. Keep responses concise but useful.

13. When product IDs are mentioned, interpret them as database
    product IDs and use the product-details or comparison tool.

14. For product comparisons, prefer the deterministic
    compare_catalog_products tool because it retrieves
    authoritative catalog information.
"""


# ============================================================
# TOOL CONFIGURATION
# ============================================================

TOOLS = [
    get_product_details,
    compare_catalog_products,
]


# ============================================================
# SHOPPING AGENT
# ============================================================

def run_shopping_agent(
    query: str,
):
    """
    Run the tool-calling shopping agent.

    Available tools:

        - get_product_details
        - compare_catalog_products

    The tool loop guarantees that every assistant tool call
    receives exactly one corresponding ToolMessage before
    another LLM request is made.

    This is required by the OpenAI tool-calling protocol.
    """

    llm = get_llm()

    # --------------------------------------------------------
    # Bind tools to the model
    # --------------------------------------------------------

    llm_with_tools = llm.bind_tools(
        TOOLS
    )

    # --------------------------------------------------------
    # Initial conversation
    # --------------------------------------------------------

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
    # Tool-calling loop
    # --------------------------------------------------------

    max_tool_rounds = 5

    result = None

    for _ in range(max_tool_rounds):

        # ----------------------------------------------------
        # Ask the model what to do
        # ----------------------------------------------------

        result = llm_with_tools.invoke(
            messages
        )

        # ----------------------------------------------------
        # Check whether the model requested tools
        # ----------------------------------------------------

        tool_calls = getattr(
            result,
            "tool_calls",
            [],
        )

        # ----------------------------------------------------
        # No tools requested.
        #
        # The model has produced the final answer.
        # ----------------------------------------------------

        if not tool_calls:
            return result

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # Add the assistant message containing ALL tool calls
        # before adding the ToolMessages.
        # ----------------------------------------------------

        messages.append(
            result
        )

        # ----------------------------------------------------
        # Execute EVERY tool call.
        #
        # If the model requests two tools, both must receive
        # a ToolMessage with their exact tool_call_id.
        # ----------------------------------------------------

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
            # Execute the requested tool
            # ------------------------------------------------

            try:

                if tool_name == "get_product_details":

                    tool_result = (
                        get_product_details.invoke(
                            tool_args
                        )
                    )

                elif tool_name == "compare_catalog_products":

                    tool_result = (
                        compare_catalog_products.invoke(
                            tool_args
                        )
                    )

                else:

                    tool_result = {
                        "error": (
                            f"Unknown tool requested: "
                            f"{tool_name}"
                        )
                    }

            except Exception as exc:

                tool_result = {
                    "error": (
                        f"Tool execution failed: "
                        f"{exc}"
                    )
                }

            # ------------------------------------------------
            # Send the result back to the model.
            #
            # CRITICAL:
            #
            # tool_call_id MUST exactly match the ID from
            # the assistant tool call.
            # ------------------------------------------------

            messages.append(
                ToolMessage(
                    content=str(
                        tool_result
                    ),
                    tool_call_id=tool_call_id,
                )
            )

    # --------------------------------------------------------
    # Safety fallback
    # --------------------------------------------------------

    if result is not None:
        return result

    raise RuntimeError(
        "Shopping agent did not produce a result."
    )