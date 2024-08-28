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

    Uses a persistent LangGraph thread so follow-up
    questions can access previous conversation state.
    """

    initial_state = {
        "query": q.strip(),
        "top_k": top_k,
    }

    config = {
        "configurable": {
            "thread_id": "shopping-assistant-demo"
        }
    }

    try:
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

    except RuntimeError as exc:
        error_message = str(exc)

        if "rate limited" in error_message.lower():
            return {
                "query": q,
                "assistant_response": (
                    "The shopping assistant is temporarily "
                    "rate limited by Azure OpenAI. "
                    "Please wait a few minutes and try again."
                ),
                "recommendations": [],
            }

        raise