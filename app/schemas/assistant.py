from pydantic import BaseModel


class RecommendedProduct(BaseModel):
    id: int | str
    name: str
    brand: str | None = None
    category: str | None = None
    price: float
    rating: float | None = None
    tags: str | None = None
    features: str | None = None
    target_audience: str | None = None
    use_cases: str | None = None


class RecommendationItem(BaseModel):
    product: RecommendedProduct
    score: float | None = None
    match_reasons: list[str] = []


class RecommendationResponse(BaseModel):
    query: str
    assistant_response: str | None = None
    recommendations: list[RecommendationItem]