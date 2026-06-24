import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-2.5-flash"
)

GEMINI_FALLBACK_MODELS = os.getenv(
    "GEMINI_FALLBACK_MODELS",
    "gemini-2.5-flash-lite"
)

GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001"
)

GEMINI_EMBEDDING_DIMENSION = int(
    os.getenv("GEMINI_EMBEDDING_DIMENSION", "768")
)

client = genai.Client(api_key=GEMINI_API_KEY)


class AIServiceUnavailableError(Exception):
    pass


def get_model_list() -> list[str]:
    models = [GEMINI_MODEL]

    fallback_models = [
        item.strip()
        for item in GEMINI_FALLBACK_MODELS.split(",")
        if item.strip()
    ]

    for model in fallback_models:
        if model not in models:
            models.append(model)

    return models


def is_temporary_gemini_error(error: Exception) -> bool:
    message = str(error)

    temporary_error_keywords = [
        "503",
        "UNAVAILABLE",
        "high demand",
        "overloaded",
        "temporarily"
    ]

    return any(keyword.lower() in message.lower() for keyword in temporary_error_keywords)


def generate_text(prompt: str) -> str:
    """
    Generates text using Gemini.
    Tries primary model first, then fallback models.
    Retries temporary 503/high-demand errors.
    """

    last_error = None
    models_to_try = get_model_list()

    for model_name in models_to_try:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.2,
                        max_output_tokens=4096
                    )
                )

                return response.text or ""

            except Exception as e:
                last_error = e

                if is_temporary_gemini_error(e):
                    wait_seconds = 4 * (attempt + 1)
                    time.sleep(wait_seconds)
                    continue

                raise e

    raise AIServiceUnavailableError(
        "Gemini service is temporarily unavailable or overloaded. Please try again later."
    ) from last_error


def generate_json(prompt: str) -> dict:
    """
    Generates JSON using Gemini.
    Cleans markdown JSON blocks if Gemini returns them.
    """

    json_prompt = f"""
Return only valid JSON.
Do not include markdown.
Do not include explanation outside JSON.

{prompt}
"""

    text = generate_text(json_prompt)

    try:
        return json.loads(text)

    except json.JSONDecodeError:
        cleaned = (
            text.replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(cleaned)


def create_embedding(text: str) -> list[float]:
    """
    Creates one Gemini embedding with fixed output dimension.
    This must match Qdrant collection dimension.
    """

    response = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            output_dimensionality=GEMINI_EMBEDDING_DIMENSION,
            task_type="SEMANTIC_SIMILARITY"
        )
    )

    return response.embeddings[0].values


def create_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = []

    for text in texts:
        if text and text.strip():
            embeddings.append(create_embedding(text.strip()))

    return embeddings