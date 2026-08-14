from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    external_id: str | None = None
    description: str | None = None
    brand: str | None = None
    category: str | None = None
    subcategory: str | None = None
    price: float
    rating: float | None = None
    stock: int = 0

    tags: str | None = None
    features: str | None = None
    target_audience: str | None = None
    use_cases: str | None = None
    color: str | None = None
    material: str | None = None
    search_text: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)