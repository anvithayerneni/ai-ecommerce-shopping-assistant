from langchain_core.tools import tool

from app.services.search_service import search_products


@tool
def search_product_catalog(
    query: str,
    top_k: int = 5,
) -> list[dict]:
    """
    Search the product catalog using the existing
    semantic search and reranking pipeline.
    """

    return search_products(
        query=query,
        top_k=top_k,
    )
