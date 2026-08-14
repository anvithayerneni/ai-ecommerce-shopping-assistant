import os

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from dotenv import load_dotenv

from app.db.session import SessionLocal
from app.models.product import Product
from app.services.embedding_service import embedding_service
from app.services.product_service import build_search_text


load_dotenv()

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
api_key = os.environ["AZURE_SEARCH_API_KEY"]
index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]


search_client = SearchClient(
    endpoint=endpoint,
    index_name=index_name,
    credential=AzureKeyCredential(api_key),
)


def product_to_document(product: Product) -> dict:
    search_text = build_search_text(product)

    embedding = embedding_service.embed_text(search_text)

    return {
        "id": str(product.id),
        "external_id": product.external_id,
        "name": product.name,
        "description": product.description,
        "brand": product.brand,
        "category": product.category,
        "subcategory": product.subcategory,
        "price": product.price,
        "rating": product.rating,
        "stock": product.stock,
        "tags": product.tags,
        "features": product.features,
        "target_audience": product.target_audience,
        "use_cases": product.use_cases,
        "color": product.color,
        "material": product.material,
        "search_text": search_text,
        "embedding": embedding,
    }


def index_products(batch_size: int = 50) -> None:
    db = SessionLocal()

    try:
        products = db.query(Product).order_by(Product.id).all()

        print(f"Products found: {len(products)}")

        total_indexed = 0

        for start in range(0, len(products), batch_size):
            batch = products[start : start + batch_size]

            documents = [
                product_to_document(product)
                for product in batch
            ]

            results = search_client.merge_or_upload_documents(
                documents=documents
            )

            failed = [
                result
                for result in results
                if not result.succeeded
            ]

            if failed:
                print(
                    f"Batch failed: {len(failed)} documents"
                )

                for result in failed[:5]:
                    print(
                        f"Key: {result.key} | "
                        f"Error: {result.error_message}"
                    )

                raise RuntimeError(
                    "Azure AI Search indexing failed."
                )

            total_indexed += len(documents)

            print(
                f"Indexed: {total_indexed}/{len(products)}"
            )

        print()
        print("Indexing complete.")
        print(f"Total indexed: {total_indexed}")

    finally:
        db.close()


if __name__ == "__main__":
    index_products()