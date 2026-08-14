import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv

from app.services.embedding_service import embedding_service
from app.services.query_understanding import understand_query
from app.services.product_ranking import rerank_products

load_dotenv()

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
api_key = os.environ["AZURE_SEARCH_API_KEY"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]


search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(api_key),
)


SELECT_FIELDS = [
    "id",
    "external_id",
    "name",
    "brand",
    "category",
    "subcategory",
    "price",
    "rating",
    "stock",
    "tags",
    "features",
    "target_audience",
    "use_cases",
    "color",
    "material",
]


def build_category_filter(category: str | None) -> str | None:
    if not category:
        return None

    escaped_category = category.replace("'", "''")

    return f"category eq '{escaped_category}'"


def search_hybrid_filtered(
    query: str,
    top_k: int = 5,
):
    intent = understand_query(query)

    query_vector = embedding_service.embed_text(query)

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    category_filter = build_category_filter(
        intent.category
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        filter=category_filter,
        select=SELECT_FIELDS,
        top=top_k,
    )

    return intent, list(results)


def print_results(query: str, top_k: int = 5):
    intent, results = search_hybrid_filtered(
        query,
        top_k,
    )

    ranked_results = rerank_products(
        results,
        intent,
    )

    print()
    print("=" * 80)
    print(f"QUERY: {query}")
    print(f"DETECTED CATEGORY: {intent.category}")
    print(f"DETECTED USE CASE: {intent.use_case}")
    print("=" * 80)

    for result in ranked_results:
        print(
            f"{result['name']} | "
            f"brand={result.get('brand')} | "
            f"category={result.get('category')} | "
            f"use_cases={result.get('use_cases')} | "
            f"price=${result.get('price')} | "
            f"azure_score={result['@search.score']:.4f} | "
            f"rerank_score={result['rerank_score']:.4f}"
        )


if __name__ == "__main__":
    print_results(
        "comfortable running shoes for training",
        5,
    )

    print_results(
        "wireless noise cancelling headphones",
        5,
    )

    print_results(
        "laptop for programming work",
        5,
    )

    print_results(
        "something nice for travel",
        5,
    )