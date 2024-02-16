from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


def create_product(db: Session, product_data: ProductCreate) -> Product:
    product = Product(**product_data.model_dump())

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_products(db: Session) -> list[Product]:
    result = db.execute(select(Product))
    return list(result.scalars().all())


def get_product(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)