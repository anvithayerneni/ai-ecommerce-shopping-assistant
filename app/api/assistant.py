from fastapi import APIRouter, Query

from app.schemas.assistant import RecommendationResponse
from app.agents.shopping_graph import shopping_graph


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
    top_k: int = Query(
        default=5,
        ge=1,
        le=20,
    ),
):
    """
    Run the LangGraph-powered shopping assistant.
    """

    initial_state = {
        "query": q.strip(),
        "top_k": top_k,
        "conversation_history": [],
        "previous_recommendations": [],
    }

    # LangGraph checkpointer requires a thread_id.
    config = {
        "configurable": {
            "thread_id": "shopping-assistant-demo"
        }
    }

    result = shopping_graph.invoke(
        initial_state,
        config=config,
    )

    recommendations = result.get(
        "recommendations",
        [],
    )

    return {
        "query": q,
        "assistant_response": result.get(
            "response"
        ),
        "recommendations": recommendations,
    }