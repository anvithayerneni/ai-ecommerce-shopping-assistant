#


from openai import OpenAI

from app.core.config import (
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_DEPLOYMENT,
)


client = OpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    base_url=f"{AZURE_OPENAI_ENDPOINT}/openai/v1/",
)


def generate_response(
    prompt: str,
    max_output_tokens: int = 300,
) -> str:
    response = client.responses.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        input=prompt,
        max_output_tokens=max_output_tokens,
    )

    return response.output_text