from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)

from sqlalchemy.orm import Session

from app.db.session import get_db

from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductRecommendationsResponse,
    RecommendationResponse,
)

from app.services.product_service import (
    create_product,
    get_product,
    get_products,
)

from app.services.embedding_service import (
    embedding_service,
)

from app.services.recommendation_service import (
    recommend_similar_products,
)

from app.services.recommendation_model import (
    ProductEncoder,
)

from scripts.enrich_product_metadata import (
    product_text,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


# ============================================================
# CREATE PRODUCT
# ============================================================

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_endpoint(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
):
    return create_product(
        db,
        product_data,
    )


# ============================================================
# GET PRODUCTS
# ============================================================

@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products_endpoint(
    category: str | None = Query(
        default=None,
    ),
    brand: str | None = Query(
        default=None,
    ),
    min_price: float | None = Query(
        default=None,
        ge=0,
    ),
    max_price: float | None = Query(
        default=None,
        ge=0,
    ),
    min_rating: float | None = Query(
        default=None,
        ge=0,
        le=5,
    ),
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=50,
        ge=1,
        le=100,
    ),
    sort_by: str = Query(
        default="id",
        pattern="^(id|name|price|rating)$",
    ),
    sort_order: str = Query(
        default="asc",
        pattern="^(asc|desc)$",
    ),
    db: Session = Depends(get_db),
):
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="min_price cannot be greater than max_price",
        )

    return get_products(
        db,
        category=category,
        brand=brand,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
    )


# ============================================================
# SEARCH PRODUCTS
# ============================================================

@router.get(
    "/search",
)
def search_products_endpoint(
    q: str = Query(
        ...,
        min_length=2,
    ),
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
):
    from app.services.search_service import (
        search_products,
    )

    results = search_products(
        query=q,
        top_k=top_k,
    )

    return {
        "query": q,
        "results": [
            {
                "id": int(result["id"]),
                "name": result["name"],
                "brand": result.get("brand"),
                "category": result.get("category"),
                "price": result.get("price"),
                "rating": result.get("rating"),
                "score": result["rerank_score"],
                "match_reasons": result[
                    "match_reasons"
                ],
            }
            for result in results
        ],
    }


# ============================================================
# PRODUCT RECOMMENDATIONS
# ============================================================

@router.get(
    "/{product_id}/recommendations",
    response_model=ProductRecommendationsResponse,
)
def get_product_recommendations_endpoint(
    product_id: int,
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
    db: Session = Depends(get_db),
):
    """
    Return products similar to the requested product.

    Recommendation score combines:

        40% categorical similarity
        20% use-case similarity
        40% semantic embedding similarity
    """

    # --------------------------------------------------------
    # Query product
    # --------------------------------------------------------

    query_product = get_product(
        db,
        product_id,
    )

    if query_product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    # --------------------------------------------------------
    # Ensure product is enriched
    # --------------------------------------------------------

    if query_product.category is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                "Product metadata has not been enriched "
                "for recommendations."
            ),
        )

    # --------------------------------------------------------
    # Load enriched products
    # --------------------------------------------------------

    products = (
        db.query(
            type(query_product)
        )
        .filter(
            type(query_product).category.isnot(None)
        )
        .all()
    )

    # --------------------------------------------------------
    # Generate query embedding
    # --------------------------------------------------------

    query_embedding = (
        embedding_service.embed_text(
            product_text(
                query_product
            )
        )
    )

    # --------------------------------------------------------
    # Generate candidate embeddings
    #
    # For now these are generated at request time.
    # Later we can cache/store them for production.
    # --------------------------------------------------------

    candidate_embeddings = {}

    for product in products:

        candidate_embeddings[
            product.id
        ] = embedding_service.embed_text(
            product_text(product)
        )

    # --------------------------------------------------------
    # Recommendation model
    # --------------------------------------------------------

    model = ProductEncoder()

    recommendations = (
        recommend_similar_products(
            query_product=query_product,
            candidate_products=products,
            model=model,
            query_embedding=query_embedding,
            candidate_embeddings=candidate_embeddings,
            top_k=top_k,
        )
    )

    # --------------------------------------------------------
    # Product lookup
    # --------------------------------------------------------

    products_by_id = {
        product.id: product
        for product in products
    }

    # --------------------------------------------------------
    # Build response
    # --------------------------------------------------------

    response_recommendations = []

    for recommendation in recommendations:

        product = products_by_id.get(
            recommendation.product_id
        )

        if product is None:
            continue

        response_recommendations.append(
            RecommendationResponse(
                product=product,
                score=round(
                    recommendation.score,
                    4,
                ),
                categorical_score=round(
                    recommendation.categorical_score,
                    4,
                ),
                use_case_score=round(
                    recommendation.use_case_score,
                    4,
                ),
                semantic_score=round(
                    recommendation.semantic_score,
                    4,
                ),
                explanation=recommendation.explanation,
            )
        )

    return ProductRecommendationsResponse(
        query_product=query_product,
        recommendations=response_recommendations,
    )


# ============================================================
# GET SINGLE PRODUCT
# ============================================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = get_product(
        db,
        product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product