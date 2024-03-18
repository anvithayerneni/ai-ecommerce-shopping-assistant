from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    id: int
    name: str
    brand: str | None = None
    category: str | None = None
    price: float
    rating: float | None = None
    score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]