from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate


def build_search_text(product: Product) -> str:
    return " | ".join(
        value
        for value in [
            product.name,
            product.brand,
            product.category,
            product.subcategory,
            product.description,
            product.tags,
            product.features,
            product.target_audience,
            product.use_cases,
            product.color,
            product.material,
        ]
        if value
    )


def create_product(db: Session, product_data: ProductCreate) -> Product:
    product = Product(**product_data.model_dump(exclude={"search_text"}))

    product.search_text = build_search_text(product)

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_products(
    db: Session,
    category: str | None = None,
    brand: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    skip: int = 0,
    limit: int = 50,
    sort_by: str = "id",
    sort_order: str = "asc",
) -> list[Product]:
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)

    if brand:
        query = query.filter(Product.brand == brand)

    if min_price is not None:
        query = query.filter(Product.price >= min_price)

    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)

    sort_columns = {
    "id": Product.id,
    "name": Product.name,
    "price": Product.price,
    "rating": Product.rating,
}

    sort_column = sort_columns[sort_by]

    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
     query = query.order_by(sort_column.asc())

    return query.offset(skip).limit(limit).all()


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()