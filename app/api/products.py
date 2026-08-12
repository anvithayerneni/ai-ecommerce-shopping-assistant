from fastapi import APIRouter, Depends, HTTPException, status
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
    return create_product(db, product_data)


@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products_endpoint(
    db: Session = Depends(get_db),
):
    return get_products(db)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product_endpoint(
    product_id: int,
    db: Session = Depends(get_db),
):
    product = get_product(db, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found",
        )

    return product