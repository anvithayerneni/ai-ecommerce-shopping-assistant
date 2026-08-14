from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductResponse
from app.services.product_service import (
    create_product,
    get_product,
    get_products,
)


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


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


@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products_endpoint(
    category: str | None = Query(default=None),
    brand: str | None = Query(default=None),
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
    from app.services.search_service import search_products

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
                "match_reasons": result["match_reasons"],
            }
            for result in results
        ],
    }


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