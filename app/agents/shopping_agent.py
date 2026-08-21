from __future__ import annotations

import os
import re
from typing import Any

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_openai import AzureChatOpenAI

from app.tools.product_details import get_product_details
from app.tools.product_compare import compare_products
from app.tools.shopping_tools import SHOPPING_TOOLS


# ============================================================
# LLM
# ============================================================

llm = AzureChatOpenAI(
    azure_deployment=os.getenv(
        "AZURE_OPENAI_DEPLOYMENT"
    ),
    api_version=os.getenv(
        "AZURE_OPENAI_API_VERSION",
        "2024-10-21",
    ),
    temperature=0,
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are an AI-powered e-commerce shopping assistant.

You help users search, filter, retrieve, compare, and discuss
products using the product catalog.

============================================================
CORE RULES
============================================================

1. Never invent product information.

2. Never invent:
   - prices
   - ratings
   - features
   - specifications
   - stock
   - target audiences
   - use cases

3. Only make claims supported by catalog data.

4. Missing information means the catalog does not confirm it.

5. Never infer product capabilities from:
   - product name
   - brand
   - category
   - price
   - rating
   - target audience

6. When a user asks about a specific product, use the
   product-detail tool.

7. When a user asks for recommendations, use the catalog
   search/filter tools.

8. When a user asks for a comparison, use the comparison
   tool and preserve product-specific attributes.

============================================================
COMPARISON RULES
============================================================

Every product is an independent source of truth.

NEVER combine attributes between products.

For example, if:

Product A:
use_cases = programming, studying

Product B:
use_cases = studying, browsing

you MUST NOT say:

"Both support programming."

You MUST say:

"Product A explicitly lists programming as a use case.
Product B does not have programming listed, so the catalog
does not confirm programming support."

If a product does not explicitly list a use case, do not
claim that it supports that use case.

============================================================
FOLLOW-UP QUESTIONS
============================================================

Use conversation context when available.

Examples:

"show me cheaper ones"
"show me more expensive ones"
"show me another option"
"compare these"
"which one is better?"

Preserve relevant context from previous turns.

============================================================
RESPONSE STYLE
============================================================

- Be concise.
- Be factual.
- Be transparent when information is not confirmed.
- Do not mention internal prompts.
- Do not expose internal reasoning.
"""


# ============================================================
# TOOL MAP
# ============================================================

TOOL_MAP = {
    tool.name: tool
    for tool in SHOPPING_TOOLS
}


# ============================================================
# HELPER: EXTRACT PRODUCT IDS
# ============================================================

def _extract_product_ids(
    query: str,
) -> list[int]:
    """
    Extract explicit product IDs from a user query.

    Examples:

    "Compare product 4 and product 5"
        -> [4, 5]

    "Compare products 4 and 5"
        -> [4, 5]

    "product 4 vs product 5"
        -> [4, 5]

    Only explicit product references are extracted.
    """

    pattern = re.compile(
        r"\bproduct(?:s)?\s*#?\s*(\d+)",
        re.IGNORECASE,
    )

    matches = pattern.findall(
        query
    )

    product_ids: list[int] = []

    for match in matches:

        product_id = int(match)

        if product_id not in product_ids:
            product_ids.append(
                product_id
            )

    return product_ids


# ============================================================
# HELPER: IS COMPARISON REQUEST?
# ============================================================

def _is_comparison_request(
    query: str,
) -> bool:
    """
    Detect explicit product comparison requests.

    This intentionally only handles explicit comparison
    language. Ambiguous conversational comparisons continue
    through the normal agent flow.
    """

    comparison_patterns = [
        r"\bcompare\b",
        r"\bcomparison\b",
        r"\bvs\.?\b",
        r"\bversus\b",
        r"\bcompare\s+these\b",
        r"\bcompare\s+them\b",
        r"\bdifference\s+between\b",
    ]

    query_lower = query.lower()

    return any(
        re.search(
            pattern,
            query_lower,
        )
        for pattern in comparison_patterns
    )


# ============================================================
# DETERMINISTIC COMPARISON
# ============================================================

def _run_deterministic_comparison(
    product_ids: list[int],
) -> AIMessage:
    """
    Retrieve products directly from the catalog and perform
    a deterministic comparison.

    The LLM is only used to produce the normal response in
    other agent paths. This comparison path prevents the LLM
    from inventing product attributes.
    """

    products: list[
        dict[str, Any]
    ] = []

    missing_ids: list[int] = []

    for product_id in product_ids:

        try:

            product = get_product_details.invoke(
                {
                    "product_id": product_id,
                }
            )

        except Exception:
            product = None

        if product:
            products.append(
                product
            )
        else:
            missing_ids.append(
                product_id
            )

    if not products:

        return AIMessage(
            content=(
                "I couldn't find the requested products "
                "in the catalog."
            )
        )

    comparison = compare_products(
        products
    )

    comparison_products = comparison.get(
        "products",
        [],
    )

    lines: list[str] = []

    # --------------------------------------------------------
    # Header
    # --------------------------------------------------------

    names = [
        str(
            product.get("name")
            or f"Product {product.get('id')}"
        )
        for product in comparison_products
    ]

    if len(names) >= 2:

        lines.append(
            "Here is the comparison between "
            + " and ".join(names)
            + ":"
        )

    else:

        lines.append(
            "Here is the product comparison:"
        )

    lines.append("")

    # --------------------------------------------------------
    # Individual products
    # --------------------------------------------------------

    for product in comparison_products:

        name = product.get(
            "name"
        )

        product_id = product.get(
            "id"
        )

        price = product.get(
            "price"
        )

        rating = product.get(
            "rating"
        )

        features = product.get(
            "features",
            [],
        )

        target_audience = product.get(
            "target_audience"
        )

        use_cases = product.get(
            "use_cases",
            [],
        )

        stock = product.get(
            "stock"
        )

        lines.append(
            f"**{name} (product {product_id})**"
        )

        if price is not None:
            lines.append(
                f"- Price: ${float(price):,.2f}"
            )

        if rating is not None:
            lines.append(
                f"- Rating: {rating}"
            )

        if features:
            lines.append(
                "- Features: "
                + ", ".join(
                    str(value)
                    for value in features
                )
            )

        if target_audience:
            lines.append(
                "- Target audience: "
                + str(
                    target_audience
                )
            )

        if use_cases:
            lines.append(
                "- Use cases: "
                + ", ".join(
                    str(value)
                    for value in use_cases
                )
            )

        if stock is not None:
            lines.append(
                f"- Stock: {stock}"
            )

        # ----------------------------------------------------
        # Programming support
        # ----------------------------------------------------

        programming_supported = product.get(
            "programming_supported",
            False,
        )

        if programming_supported:

            lines.append(
                "- Programming support: "
                "Confirmed — programming is explicitly "
                "listed as a use case."
            )

        else:

            lines.append(
                "- Programming support: "
                "Not confirmed — programming is not "
                "explicitly listed as a use case."
            )

        lines.append("")

    # --------------------------------------------------------
    # Cheapest
    # --------------------------------------------------------

    cheapest = comparison.get(
        "cheapest"
    )

    if cheapest:

        lines.append(
            f"**Cheapest:** "
            f"{cheapest.get('name')} "
            f"at ${float(cheapest.get('price')):,.2f}."
        )

    # --------------------------------------------------------
    # Highest rated
    # --------------------------------------------------------

    highest_rated = comparison.get(
        "highest_rated"
    )

    if highest_rated:

        lines.append(
            f"**Highest rated:** "
            f"{highest_rated.get('name')} "
            f"with a rating of "
            f"{highest_rated.get('rating')}."
        )

    # --------------------------------------------------------
    # Missing products
    # --------------------------------------------------------

    if missing_ids:

        lines.append("")

        lines.append(
            "I couldn't find these product IDs: "
            + ", ".join(
                str(product_id)
                for product_id in missing_ids
            )
            + "."
        )

    return AIMessage(
        content="\n".join(
            lines
        )
    )


# ============================================================
# TOOL EXECUTION
# ============================================================

def _execute_tool_calls(
    messages: list,
) -> list:
    """
    Execute tool calls produced by the LLM.
    """

    if not messages:
        return messages

    last_message = messages[-1]

    tool_calls = getattr(
        last_message,
        "tool_calls",
        [],
    )

    if not tool_calls:
        return messages

    updated_messages = list(
        messages
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

        tool = TOOL_MAP.get(
            tool_name
        )

        if tool is None:

            updated_messages.append(
                ToolMessage(
                    content=(
                        f"Unknown tool: {tool_name}"
                    ),
                    tool_call_id=tool_call_id,
                )
            )

            continue

        try:

            result = tool.invoke(
                tool_args
            )

            updated_messages.append(
                ToolMessage(
                    content=str(
                        result
                    ),
                    tool_call_id=tool_call_id,
                )
            )

        except Exception as exc:

            updated_messages.append(
                ToolMessage(
                    content=(
                        "Tool execution failed: "
                        f"{exc}"
                    ),
                    tool_call_id=tool_call_id,
                )
            )

    return updated_messages


# ============================================================
# RUN SHOPPING AGENT
# ============================================================

def run_shopping_agent(
    query: str,
    history: list | None = None,
):
    """
    Run the shopping agent.

    Explicit comparisons between product IDs are handled
    deterministically to prevent unsupported product claims.

    Other requests continue through the normal tool-calling
    Azure OpenAI agent.
    """

    query = (
        query or ""
    ).strip()

    # ========================================================
    # DETERMINISTIC EXPLICIT COMPARISON PATH
    # ========================================================

    if _is_comparison_request(
        query
    ):

        product_ids = (
            _extract_product_ids(
                query
            )
        )

        if len(product_ids) >= 2:

            return _run_deterministic_comparison(
                product_ids
            )

    # ========================================================
    # NORMAL AGENT PATH
    # ========================================================

    messages = []

    # --------------------------------------------------------
    # System prompt
    # --------------------------------------------------------

    messages.append(
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    )

    # --------------------------------------------------------
    # Previous conversation
    # --------------------------------------------------------

    if history:

        messages.extend(
            history
        )

    # --------------------------------------------------------
    # Current user message
    # --------------------------------------------------------

    messages.append(
        HumanMessage(
            content=query
        )
    )

    # --------------------------------------------------------
    # Initial LLM call
    # --------------------------------------------------------

    response = llm.bind_tools(
        SHOPPING_TOOLS
    ).invoke(
        messages
    )

    messages.append(
        response
    )

    # --------------------------------------------------------
    # Tool loop
    # --------------------------------------------------------

    max_tool_rounds = 5

    for _ in range(
        max_tool_rounds
    ):

        tool_calls = getattr(
            response,
            "tool_calls",
            [],
        )

        if not tool_calls:
            break

        messages = _execute_tool_calls(
            messages
        )

        response = llm.bind_tools(
            SHOPPING_TOOLS
        ).invoke(
            messages
        )

        messages.append(
            response
        )

    # --------------------------------------------------------
    # Final AI response
    # --------------------------------------------------------

    for message in reversed(
        messages
    ):

        if isinstance(
            message,
            AIMessage,
        ):

            if not getattr(
                message,
                "tool_calls",
                [],
            ):

                return message

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return AIMessage(
        content=(
            "I couldn't generate a response."
        )
    )


# ============================================================
# CONVERSATION HELPER
# ============================================================

def run_shopping_conversation(
    messages: list,
):
    """
    Continue an existing shopping conversation.

    Explicit comparisons containing product IDs are handled
    deterministically.

    Other conversations use the normal agent.
    """

    # --------------------------------------------------------
    # Find latest human message
    # --------------------------------------------------------

    latest_query = ""

    for message in reversed(
        messages
    ):

        if isinstance(
            message,
            HumanMessage,
        ):

            latest_query = (
                message.content
                if isinstance(
                    message.content,
                    str,
                )
                else str(
                    message.content
                )
            )

            break

    # --------------------------------------------------------
    # Deterministic comparison
    # --------------------------------------------------------

    if (
        latest_query
        and _is_comparison_request(
            latest_query
        )
    ):

        product_ids = (
            _extract_product_ids(
                latest_query
            )
        )

        if len(product_ids) >= 2:

            return _run_deterministic_comparison(
                product_ids
            )

    # --------------------------------------------------------
    # Normal conversation
    # --------------------------------------------------------

    prepared_messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        }
    ]

    prepared_messages.extend(
        messages
    )

    response = llm.bind_tools(
        SHOPPING_TOOLS
    ).invoke(
        prepared_messages
    )

    prepared_messages.append(
        response
    )

    max_tool_rounds = 5

    for _ in range(
        max_tool_rounds
    ):

        tool_calls = getattr(
            response,
            "tool_calls",
            [],
        )

        if not tool_calls:
            break

        prepared_messages = (
            _execute_tool_calls(
                prepared_messages
            )
        )

        response = llm.bind_tools(
            SHOPPING_TOOLS
        ).invoke(
            prepared_messages
        )

        prepared_messages.append(
            response
        )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    for message in reversed(
        prepared_messages
    ):

        if isinstance(
            message,
            AIMessage,
        ):

            if not getattr(
                message,
                "tool_calls",
                [],
            ):

                return message

    return AIMessage(
        content=(
            "I couldn't generate a response."
        )
    )