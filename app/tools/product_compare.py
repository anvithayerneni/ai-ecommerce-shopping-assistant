from __future__ import annotations

from typing import Any


# ============================================================
# NORMALIZATION HELPERS
# ============================================================

def _normalize_list(
    value: Any,
) -> list[str]:
    """
    Convert a catalog field into a clean list of strings.

    Supported input:
    - comma-separated string
    - list
    - None

    This function does not infer missing information.
    """

    if not value:
        return []

    if isinstance(value, list):
        return [
            str(item).strip()
            for item in value
            if str(item).strip()
        ]

    return [
        item.strip()
        for item in str(value).split(",")
        if item.strip()
    ]


def _contains_use_case(
    use_cases: list[str],
    requested_use_case: str,
) -> bool:
    """
    Check whether a use case is explicitly present
    in the product's catalog data.
    """

    requested = requested_use_case.strip().lower()

    return any(
        requested == use_case.strip().lower()
        for use_case in use_cases
    )


# ============================================================
# PRODUCT COMPARISON
# ============================================================

def compare_products(
    products: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Compare multiple products using only explicit catalog data.

    This function is deterministic.

    It does NOT use an LLM.

    It does NOT infer product capabilities.

    In particular:
        - Missing use cases remain missing.
        - Missing features remain missing.
        - Products are evaluated independently.
        - A use case belonging to one product is never
          automatically assigned to another product.
    """

    # --------------------------------------------------------
    # Empty input
    # --------------------------------------------------------

    if not products:
        return {
            "products": [],
            "comparison": [],
            "cheapest": None,
            "highest_rated": None,
            "use_case_comparison": {},
            "grounding_rules": [
                "Only use explicitly listed catalog data.",
                "Do not infer missing use cases.",
                "Do not combine attributes between products.",
            ],
        }

    comparison: list[dict[str, Any]] = []

    # ========================================================
    # BUILD PRODUCT-SPECIFIC COMPARISON DATA
    # ========================================================

    for product in products:

        use_cases = _normalize_list(
            product.get("use_cases")
        )

        features = _normalize_list(
            product.get("features")
        )

        programming_supported = _contains_use_case(
            use_cases,
            "programming",
        )

        # ----------------------------------------------------
        # Explicit grounded statement
        # ----------------------------------------------------

        if programming_supported:
            programming_statement = (
                f"{product.get('name')} explicitly lists "
                "programming as a use case."
            )
        else:
            programming_statement = (
                f"{product.get('name')} does not explicitly "
                "list programming as a use case. The catalog "
                "does not confirm programming support."
            )

        comparison.append(
            {
                "id": product.get("id"),

                "name": product.get(
                    "name"
                ),

                "brand": product.get(
                    "brand"
                ),

                "category": product.get(
                    "category"
                ),

                "subcategory": product.get(
                    "subcategory"
                ),

                "price": product.get(
                    "price"
                ),

                "rating": product.get(
                    "rating"
                ),

                "stock": product.get(
                    "stock"
                ),

                "features": features,

                "target_audience": product.get(
                    "target_audience"
                ),

                "use_cases": use_cases,

                # ------------------------------------------------
                # Explicit capability flags
                # ------------------------------------------------

                "programming_supported": (
                    programming_supported
                ),

                "programming_support_confirmed": (
                    programming_supported
                ),

                "programming_support_status": (
                    "confirmed"
                    if programming_supported
                    else "not_confirmed"
                ),

                "grounded_use_case_statement": (
                    programming_statement
                ),
            }
        )

    # ========================================================
    # CHEAPEST PRODUCT
    # ========================================================

    priced_products: list[
        tuple[float, dict[str, Any]]
    ] = []

    for product in products:

        price = product.get(
            "price"
        )

        if price is None:
            continue

        try:
            numeric_price = float(
                price
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        priced_products.append(
            (
                numeric_price,
                product,
            )
        )

    cheapest = None

    if priced_products:

        _, cheapest_product = min(
            priced_products,
            key=lambda item: item[0],
        )

        cheapest = {
            "id": cheapest_product.get(
                "id"
            ),
            "name": cheapest_product.get(
                "name"
            ),
            "price": cheapest_product.get(
                "price"
            ),
        }

    # ========================================================
    # HIGHEST RATED PRODUCT
    # ========================================================

    rated_products: list[
        tuple[float, dict[str, Any]]
    ] = []

    for product in products:

        rating = product.get(
            "rating"
        )

        if rating is None:
            continue

        try:
            numeric_rating = float(
                rating
            )
        except (
            TypeError,
            ValueError,
        ):
            continue

        rated_products.append(
            (
                numeric_rating,
                product,
            )
        )

    highest_rated = None

    if rated_products:

        _, highest_rated_product = max(
            rated_products,
            key=lambda item: item[0],
        )

        highest_rated = {
            "id": highest_rated_product.get(
                "id"
            ),
            "name": highest_rated_product.get(
                "name"
            ),
            "rating": highest_rated_product.get(
                "rating"
            ),
        }

    # ========================================================
    # USE-CASE COMPARISON
    # ========================================================

    use_case_comparison: dict[
        str,
        list[dict[str, Any]],
    ] = {}

    # --------------------------------------------------------
    # Programming
    # --------------------------------------------------------

    programming_comparison = []

    for product in comparison:

        programming_comparison.append(
            {
                "id": product.get(
                    "id"
                ),

                "name": product.get(
                    "name"
                ),

                "programming_supported": (
                    product.get(
                        "programming_supported",
                        False,
                    )
                ),

                "status": product.get(
                    "programming_support_status"
                ),

                "statement": product.get(
                    "grounded_use_case_statement"
                ),
            }
        )

    use_case_comparison[
        "programming"
    ] = programming_comparison

    # ========================================================
    # EXPLICIT GROUNDING RULES
    # ========================================================

    grounding_rules = [
        (
            "Only use features explicitly listed "
            "for each individual product."
        ),
        (
            "Only use use cases explicitly listed "
            "for each individual product."
        ),
        (
            "Never combine use cases from different products."
        ),
        (
            "Never combine features from different products."
        ),
        (
            "A missing use case means the catalog "
            "does not confirm that capability."
        ),
        (
            "Do not infer capabilities from product category."
        ),
        (
            "Do not infer capabilities from product brand."
        ),
        (
            "Do not infer capabilities from product price."
        ),
        (
            "Do not infer capabilities from product rating."
        ),
        (
            "Do not infer capabilities from target audience."
        ),
        (
            "Do not infer capabilities from product name."
        ),
        (
            "If programming_supported is false, "
            "do not claim programming support."
        ),
    ]

    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {
        "products": comparison,

        # Kept for compatibility with existing callers.
        "comparison": comparison,

        "cheapest": cheapest,

        "highest_rated": highest_rated,

        "use_case_comparison": (
            use_case_comparison
        ),

        "grounding_rules": grounding_rules,
    }