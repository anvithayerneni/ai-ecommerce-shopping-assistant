from openai import OpenAI

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
)


def _get_client():
    if not AZURE_OPENAI_API_KEY or not AZURE_OPENAI_ENDPOINT:
        return None
    try:
        return OpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            base_url=f"{AZURE_OPENAI_ENDPOINT}/openai/v1/",
            max_retries=0,
            timeout=30.0,
        )
    except Exception:
        return None


def generate_response(
    prompt: str,
    max_output_tokens: int = 300,
) -> str:
    client = _get_client()
    if client is None:
        return (
            "Here are the top product recommendations tailored to your query, "
            "matched using semantic search and deterministic catalog filtering."
        )

    try:
        response = client.responses.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            input=prompt,
            max_output_tokens=max_output_tokens,
        )

        return response.output_text

    except Exception as exc:
        print(
            f"Azure OpenAI response generation failed: {exc}"
        )

        return (
            "I’m temporarily unable to generate the "
            "shopping response because the AI service "
            "is rate-limited. Please try again shortly."
        )