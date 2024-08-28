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

    The client is created only when the shopping agent runs.
    This allows tests to import the module without requiring
    Azure OpenAI credentials during import time.
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
- answer follow-up questions about products
- make shopping decisions

============================================================
CORE RULES
============================================================

1. NEVER invent product information.

2. Use only information returned by the available product
   tools.

3. If the user refers to a specific product ID, use the
   product-details tool.

4. If the user asks to compare specific products, use the
   deterministic compare_catalog_products tool whenever
   possible.

5. If the user provides product names instead of IDs, use the
   available catalog tools to identify the products.

6. Product names must be resolved against the actual catalog.
   Do not create fictional products.

7. When comparing products, use only catalog information
   returned by the tools.

============================================================
COMPARISON RULES
============================================================

8. A comparison should use the actual catalog products.

9. When available, comparison information may include:

   - Product name
   - Product ID
   - Price
   - Rating
   - Brand
   - Category
   - Subcategory
   - Features
   - Target audience
   - Use cases

10. If the user asks which product is cheaper, compare the
    actual catalog prices.

11. If the user asks which product is higher rated, compare
    the actual catalog ratings.

12. Do not assume that two products are equivalent merely
    because they have the same category.

============================================================
FOLLOW-UP QUESTION RULES
============================================================

13. The user may ask a follow-up after a comparison.

    Example:

        User:
        Compare MacBook Air M3 and Galaxy Book4.

        User:
        Which one is better for programming?

14. For a follow-up question such as:

        "Which one is better for programming?"

    interpret "which one" as referring to the products from
    the immediately preceding comparison context.

15. Do NOT search for unrelated products when the user is
    clearly referring to products from the previous comparison.

16. If one product explicitly lists the requested use case
    and another product does not explicitly list that use
    case, say exactly that.

    Example:

        MacBook Air M3:
        use_cases = programming, studying, office work, travel

        Galaxy Book4:
        use_cases = office work, studying, browsing, productivity

    Correct conclusion:

        "Programming is explicitly listed for MacBook Air M3.
         The catalog does not explicitly list programming for
         Galaxy Book4."

17. Do NOT assume that a product supports a use case merely
    because it:

    - is a laptop
    - is expensive
    - has a high rating
    - has a particular brand
    - has a particular feature
    - is marketed to professionals

18. Only claim that a product supports a requested use case
    when the catalog explicitly provides evidence for it.

============================================================
PRODUCT ATTRIBUTE RULES
============================================================

19. Do NOT invent:

    - operating systems
    - processors
    - RAM
    - storage
    - display specifications
    - battery specifications
    - performance
    - compatibility
    - software support
    - hardware specifications
    - benchmarks
    - technical capabilities

20. If the catalog does not contain the requested information,
    clearly say that the available catalog data does not
    confirm it.

============================================================
RESPONSE STYLE
============================================================

21. Keep responses concise and useful.

22. Answer the user's actual question directly.

23. Do not repeat the entire comparison when the user asks a
    narrow follow-up question.

24. For example, if the user asks:

        "Which one is better for programming?"

    do NOT respond with all ten comparison categories.

    Instead answer something like:

        "MacBook Air M3 is the better choice based on the
         catalog data. Programming is explicitly listed as
         one of its use cases. Galaxy Book4 does not have
         programming listed as a use case in the catalog."

25. Do not add unsupported explanations such as:

        "MacBook is better because macOS is good for developers."

    unless the catalog explicitly provides that information.

============================================================
TOOL USAGE
============================================================

26. Prefer deterministic catalog tools over model reasoning.

27. For explicit product IDs, use get_product_details.

28. For comparisons, prefer compare_catalog_products.

29. Always complete the required tool-call / ToolMessage
    sequence correctly before requesting another model response.

30. If a tool returns an error, clearly communicate the
    limitation instead of inventing an answer.
"""


# ============================================================
# TOOL CONFIGURATION
# ============================================================

TOOLS = [
    get_product_details,
    compare_catalog_products,
]


# ============================================================
# TOOL EXECUTION
# ============================================================

def _execute_tool(
    tool_name: str,
    tool_args: dict,
):
    """
    Execute one of the supported shopping tools.
    """

    if tool_name == "get_product_details":

        return get_product_details.invoke(
            tool_args
        )

    if tool_name == "compare_catalog_products":

        return compare_catalog_products.invoke(
            tool_args
        )

    return {
        "error": (
            f"Unknown tool requested: "
            f"{tool_name}"
        )
    }


# ============================================================
# SHOPPING AGENT
# ============================================================

def run_shopping_agent(
    query: str,
    conversation_history: list[dict] | None = None,
):
    """
    Run the tool-calling shopping agent.

    conversation_history allows LangGraph to provide the
    previous conversation context.

    This is important for follow-up questions such as:

        Compare MacBook Air M3 and Galaxy Book4.

        Which one is better for programming?

    Without conversation history, the second question is
    ambiguous to the model.

    Available tools:

        - get_product_details
        - compare_catalog_products
    """

    llm = get_llm()

    llm_with_tools = llm.bind_tools(
        TOOLS
    )

    # --------------------------------------------------------
    # Build conversation
    # --------------------------------------------------------

    messages = [
        (
            "system",
            SYSTEM_PROMPT,
        )
    ]

    # --------------------------------------------------------
    # Add previous conversation
    # --------------------------------------------------------

    if conversation_history:

        for item in conversation_history:

            role = item.get(
                "role"
            )

            content = item.get(
                "content"
            )

            if not content:
                continue

            if role == "user":

                messages.append(
                    (
                        "human",
                        content,
                    )
                )

            elif role == "assistant":

                messages.append(
                    (
                        "assistant",
                        content,
                    )
                )

    # --------------------------------------------------------
    # Add current user query
    # --------------------------------------------------------

    messages.append(
        (
            "human",
            query,
        )
    )

    # --------------------------------------------------------
    # Tool-calling loop
    # --------------------------------------------------------

    max_tool_rounds = 5

    result = None

    for _ in range(max_tool_rounds):

        try:
            result = llm_with_tools.invoke(
                messages
            )

        except Exception as exc:
            error_text = str(exc)

            if (
                "429" in error_text
                or "rate_limit" in error_text
                or "Too Many Requests" in error_text
            ):
                raise RuntimeError(
                    "Azure OpenAI is temporarily rate limited. "
                    "Please wait a few minutes and try again."
                ) from exc

            raise

        tool_calls = getattr(
            result,
            "tool_calls",
            [],
        )

        # ----------------------------------------------------
        # Final answer
        # ----------------------------------------------------

        if not tool_calls:

            return result

        # ----------------------------------------------------
        # Add assistant message containing tool calls.
        #
        # This MUST happen before ToolMessages.
        # ----------------------------------------------------

        messages.append(
            result
        )

        # ----------------------------------------------------
        # Execute every requested tool.
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

            try:

                tool_result = _execute_tool(
                    tool_name,
                    tool_args,
                )

            except Exception as exc:

                tool_result = {
                    "error": (
                        f"Tool execution failed: "
                        f"{exc}"
                    )
                }

            # ------------------------------------------------
            # Return the tool result using the exact
            # tool_call_id generated by the model.
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