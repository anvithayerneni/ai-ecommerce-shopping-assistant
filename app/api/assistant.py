from fastapi import APIRouter, Query

from app.schemas.assistant import RecommendationResponse
from app.services.shopping_assistant import get_recommendations


router = APIRouter(
    prefix="/assistant",
    tags=["Shopping Assistant"],
)


@router.get(
    "/recommend",
    response_model=RecommendationResponse,
)
def recommend_products(
    q: str = Query(..., min_length=2),
    top_k: int = Query(default=5, ge=1, le=20),
):
    return get_recommendations(
        query=q,
        top_k=top_k,
    )