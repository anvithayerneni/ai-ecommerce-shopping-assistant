from app.services.product_ranking import rerank_products
from app.services.query_understanding import understand_query
from app.services.embedding_service import embedding_service

import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv


load_dotenv()

azure_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
azure_index_name = os.getenv("AZURE_SEARCH_INDEX_NAME")
azure_api_key = os.getenv("AZURE_SEARCH_API_KEY")

if azure_endpoint and azure_index_name and azure_api_key:
    search_client = SearchClient(
        endpoint=azure_endpoint,
        index_name=azure_index_name,
        credential=AzureKeyCredential(azure_api_key),
    )
else:
    search_client = None


def _local_search_fallback(query: str, intent, top_k: int = 5) -> list[dict]:
    from app.db.session import SessionLocal
    from app.models.product import Product

    raw_items = []
    try:
        db = SessionLocal()
        products = db.query(Product).all()
        if not products:
            from scripts.seed_products import PRODUCTS, seed_products
            try:
                seed_products()
                products = db.query(Product).all()
            except Exception:
                products = []

        raw_items = [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "subcategory": p.subcategory,
                "price": p.price,
                "rating": p.rating,
                "stock": p.stock,
                "tags": p.tags,
                "features": p.features,
                "target_audience": p.target_audience,
                "use_cases": p.use_cases,
                "color": p.color,
                "material": p.material,
            }
            for p in products
        ]
        db.close()
    except Exception:
        from scripts.seed_products import PRODUCTS
        raw_items = [
            {"id": i + 1, **p} for i, p in enumerate(PRODUCTS)
        ]

    query_vector = embedding_service.embed_text(query)
    results = []
    for item in raw_items:
        prod_id = item.get("id")
        prod_emb = embedding_service.get_product_embedding(prod_id) if prod_id else None
        score = 0.5
        if prod_emb and query_vector:
            import numpy as np
            q = np.array(query_vector)
            p = np.array(prod_emb)
            norm = np.linalg.norm(q) * np.linalg.norm(p)
            if norm > 0:
                score = float(np.dot(q, p) / norm)

        # Apply category filter
        if intent.category and item.get("category"):
            if intent.category.lower() not in item.get("category", "").lower():
                continue

        # Apply price and rating filters
        if intent.min_price is not None and item.get("price") is not None and item["price"] < intent.min_price:
            continue
        if intent.max_price is not None and item.get("price") is not None and item["price"] > intent.max_price:
            continue
        if intent.min_rating is not None and item.get("rating") is not None and item["rating"] < intent.min_rating:
            continue

        item_copy = dict(item)
        item_copy["@search.score"] = max(0.0, min(1.0, score))
        results.append(item_copy)

    return rerank_products(results, intent)[:top_k]


def search_products(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    intent = understand_query(query)

    query_vector = embedding_service.embed_text(query)

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    filters = []

    if intent.category:
        escaped_category = intent.category.replace(
            "'",
            "''",
        )
        filters.append(
            f"category eq '{escaped_category}'"
        )

    if intent.min_price is not None:
        filters.append(
            f"price ge {intent.min_price}"
        )

    if intent.max_price is not None:
        filters.append(
            f"price le {intent.max_price}"
        )

    if intent.min_rating is not None:
        filters.append(
            f"rating ge {intent.min_rating}"
        )

    search_filter = (
        " and ".join(filters)
        if filters
        else None
    )

    if search_client is None:
        return _local_search_fallback(query, intent, top_k)

    try:
        results = search_client.search(
            search_text=query,
            vector_queries=[vector_query],
            filter=search_filter,
            select=[
                "id",
                "name",
                "brand",
                "category",
                "price",
                "rating",
                "tags",
                "features",
                "target_audience",
                "use_cases",
            ],
            top=top_k,
        )

        results = list(results)
    except Exception:
        return _local_search_fallback(query, intent, top_k)

    ranked_results = rerank_products(
        results,
        intent,
    )

    return ranked_results