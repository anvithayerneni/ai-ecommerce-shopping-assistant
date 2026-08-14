from app.services.query_understanding import QueryIntent


SEMANTIC_WEIGHT = 0.70
CATEGORY_WEIGHT = 0.15
USE_CASE_WEIGHT = 0.10
METADATA_WEIGHT = 0.05


def _contains(
    value: str | None,
    target: str | None,
) -> bool:
    if not value or not target:
        return False

    return target.lower() in value.lower()


def rerank_products(
    results: list[dict],
    intent: QueryIntent,
) -> list[dict]:
    ranked = []

    for result in results:
        # Azure's score is already a ranking signal.
        semantic_score = float(
            result.get("@search.score", 0.0)
        )

        # Normalize it gently into a 0-1 range.
        # Azure scores in our current result set are around 0.0-1.0.
        semantic_score = min(
            max(semantic_score, 0.0),
            1.0,
        )

        category_score = 0.0

        if intent.category:
            category_score = float(
                result.get("category") == intent.category
            )

        use_case_score = 0.0

        if intent.use_case:
            use_case_score = float(
                _contains(
                    result.get("use_cases"),
                    intent.use_case,
                )
            )

        metadata_score = 0.0

        if intent.use_case:
            metadata_score = max(
                float(
                    _contains(
                        result.get("tags"),
                        intent.use_case,
                    )
                ),
                float(
                    _contains(
                        result.get("target_audience"),
                        intent.use_case,
                    )
                ),
            )

        final_score = (
            SEMANTIC_WEIGHT * semantic_score
            + CATEGORY_WEIGHT * category_score
            + USE_CASE_WEIGHT * use_case_score
            + METADATA_WEIGHT * metadata_score
        )

        match_reasons = []

        if (
            intent.category
            and result.get("category") == intent.category
        ):
            match_reasons.append(
                f"Matches {intent.category} category"
            )

        if intent.use_case and _contains(
            result.get("use_cases"),
            intent.use_case,
        ):
            match_reasons.append(
                f"Supports {intent.use_case}"
            )

        # Price matching
        if (
            intent.min_price is not None
            or intent.max_price is not None
        ):
            price = result.get("price")

            if price is not None:
                # Both minimum and maximum price
                if (
                    intent.min_price is not None
                    and intent.max_price is not None
                    and intent.min_price <= price <= intent.max_price
                ):
                    match_reasons.append(
                        f"Within ${intent.min_price:,.0f}"
                        f"–${intent.max_price:,.0f} price range"
                    )

                # Minimum price only
                elif (
                    intent.min_price is not None
                    and price >= intent.min_price
                ):
                    match_reasons.append(
                        f"Above ${intent.min_price:,.0f}"
                        " minimum price"
                    )

                # Maximum price only
                elif (
                    intent.max_price is not None
                    and price <= intent.max_price
                ):
                    match_reasons.append(
                        f"Within ${intent.max_price:,.0f} budget"
                    )

        if intent.min_rating is not None:
            rating = result.get("rating")

            if (
                rating is not None
                and rating >= intent.min_rating
            ):
                match_reasons.append(
                    f"Rating {rating} meets "
                    f"{intent.min_rating}+ requirement"
                )

        ranked.append(
            {
                **result,
                "semantic_score": semantic_score,
                "category_score": category_score,
                "use_case_score": use_case_score,
                "metadata_score": metadata_score,
                "rerank_score": final_score,
                "match_reasons": match_reasons,
            }
        )

    return sorted(
        ranked,
        key=lambda product: product["rerank_score"],
        reverse=True,
    )