import json
import math
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from dotenv import load_dotenv

from app.services.embedding_service import embedding_service
from app.services.product_ranking import rerank_products
from app.services.query_understanding import understand_query

load_dotenv()

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
api_key = os.environ["AZURE_SEARCH_API_KEY"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]

search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(api_key),
)

EVAL_FILE = Path("data/retrieval_eval.json")


def load_test_cases():
    with EVAL_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def vector_search(query: str, top_k: int = 5):
    query_vector = embedding_service.embed_text(query)

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        select=[
            "id",
            "name",
            "category",
            "brand",
            "price",
        ],
        top=top_k,
    )

    return list(results)


def hybrid_search(query: str, top_k: int = 5):
    query_vector = embedding_service.embed_text(query)

    vector_query = VectorizedQuery(
        vector=query_vector,
        k_nearest_neighbors=top_k,
        fields="embedding",
    )

    results = search_client.search(
        search_text=query,
        vector_queries=[vector_query],
        select=[
            "id",
            "name",
            "category",
            "brand",
            "price",
        ],
        top=top_k,
    )

    return list(results)

def reranked_hybrid_search(query: str, top_k: int = 5):
    results = hybrid_search(query, top_k)

    intent = understand_query(query)

    return rerank_products(
        results,
        intent,
    )


def get_product_ids(results):
    return [int(result["id"]) for result in results]


def precision_at_k(results, relevant_ids, k):
    retrieved_ids = get_product_ids(results[:k])

    if not retrieved_ids:
        return 0.0

    relevant_count = sum(
        product_id in relevant_ids
        for product_id in retrieved_ids
    )

    return relevant_count / len(retrieved_ids)


def hit_rate_at_k(results, relevant_ids, k):
    retrieved_ids = get_product_ids(results[:k])

    return float(
        any(
            product_id in relevant_ids
            for product_id in retrieved_ids
        )
    )


def reciprocal_rank(results, relevant_ids):
    retrieved_ids = get_product_ids(results)

    for rank, product_id in enumerate(retrieved_ids, start=1):
        if product_id in relevant_ids:
            return 1.0 / rank

    return 0.0





def ndcg_at_k(results, relevant_ids, k):
    retrieved_ids = get_product_ids(results[:k])

    dcg = 0.0

    for rank, product_id in enumerate(retrieved_ids, start=1):
        if product_id in relevant_ids:
            dcg += 1.0 / math.log2(rank + 1)

    ideal_relevances = [
        1.0
        for _ in range(min(len(relevant_ids), k))
    ]

    idcg = sum(
        relevance / math.log2(rank + 1)
        for rank, relevance in enumerate(
            ideal_relevances,
            start=1,
        )
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg


def evaluate_method(search_function, name, test_cases):
    precision_3_scores = []
    precision_5_scores = []
    hit_3_scores = []
    hit_5_scores = []
    mrr_scores = []
    ndcg_scores = []

    print()
    print("=" * 80)
    print(name)
    print("=" * 80)

    for case in test_cases:
        query = case["query"]
        relevant_ids = set(case["relevant_product_ids"])

        results = search_function(query, 5)

        p3 = precision_at_k(results, relevant_ids, 3)
        p5 = precision_at_k(results, relevant_ids, 5)
        h3 = hit_rate_at_k(results, relevant_ids, 3)
        h5 = hit_rate_at_k(results, relevant_ids, 5)
        rr = reciprocal_rank(results, relevant_ids)
        ndcg = ndcg_at_k(
            results,
            relevant_ids,
            5,
)

        precision_3_scores.append(p3)
        precision_5_scores.append(p5)
        hit_3_scores.append(h3)
        hit_5_scores.append(h5)
        mrr_scores.append(rr)
        ndcg_scores.append(ndcg)

        print()
        print(f"Query: {query}")
        print(f"Expected IDs: {sorted(relevant_ids)}")
        print(f"Precision@3: {p3:.2f}")
        print(f"Precision@5: {p5:.2f}")
        print(f"Hit@3:       {h3:.0f}")
        print(f"Hit@5:       {h5:.0f}")
        print(f"Reciprocal Rank: {rr:.2f}")
        print(f"NDCG@5:          {ndcg:.2f}")

    print()
    print("-" * 80)
    print("AVERAGE")
    print("-" * 80)

    print(
        f"Precision@3: {sum(precision_3_scores) / len(precision_3_scores):.2f}"
    )
    print(
        f"Precision@5: {sum(precision_5_scores) / len(precision_5_scores):.2f}"
    )
    print(
        f"Hit@3:       {sum(hit_3_scores) / len(hit_3_scores):.2f}"
    )
    print(
        f"Hit@5:       {sum(hit_5_scores) / len(hit_5_scores):.2f}"
    )
    print(
        f"MRR:         {sum(mrr_scores) / len(mrr_scores):.2f}"
    )
    print(
    f"NDCG@5:      {sum(ndcg_scores) / len(ndcg_scores):.2f}"
    )

def evaluate():
    test_cases = load_test_cases()

    evaluate_method(
        vector_search,
        "VECTOR SEARCH",
        test_cases,
    )

    evaluate_method(
        reranked_hybrid_search,
        "HYBRID + QUERY-AWARE RERANKING",
        test_cases,
    )


if __name__ == "__main__":
    evaluate()