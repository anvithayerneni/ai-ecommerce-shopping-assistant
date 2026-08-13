import json
from pathlib import Path

import numpy as np

from app.services.embedding_service import embedding_service


EMBEDDINGS_FILE = Path("data/product_embeddings.json")


def cosine_similarity(
    query_vector: list[float],
    product_vector: list[float],
) -> float:
    query = np.array(query_vector)
    product = np.array(product_vector)

    return float(
        np.dot(query, product)
        / (np.linalg.norm(query) * np.linalg.norm(product))
    )


def search_products(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    query_vector = embedding_service.embed_text(query)

    with EMBEDDINGS_FILE.open("r", encoding="utf-8") as file:
        products = json.load(file)

    results = []

    for product in products:
        score = cosine_similarity(
            query_vector,
            product["embedding"],
        )

        results.append(
            {
                "product_id": product["product_id"],
                "name": product["name"],
                "score": score,
            }
        )

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return results[:top_k]