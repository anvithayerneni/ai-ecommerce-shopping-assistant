from app.services.product_ranking import rerank_products
from app.services.query_understanding import understand_query
from app.services.embedding_service import embedding_service

import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv


load_dotenv()

search_client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name=os.environ["AZURE_SEARCH_INDEX_NAME"],
    credential=AzureKeyCredential(
        os.environ["AZURE_SEARCH_API_KEY"]
    ),
)


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

    # category_filter = None

    # if intent.category:
    #     escaped_category = intent.category.replace(
    #         "'",
    #         "''",
    #     )

    #     category_filter = (
    #         f"category eq '{escaped_category}'"
    #     )

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

    ranked_results = rerank_products(
        results,
        intent,
    )

    return ranked_results