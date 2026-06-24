import os
import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001"
)

GEMINI_EMBEDDING_DIMENSION = int(
    os.getenv("GEMINI_EMBEDDING_DIMENSION", "768")
)

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_text(prompt: str) -> str:
    """
    Generates text using Gemini.
    Includes small retry logic for temporary 503 high-demand errors.
    """

    last_error = None

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            return response.text or ""

        except Exception as e:
            last_error = e
            error_message = str(e)

            if "503" in error_message or "UNAVAILABLE" in error_message:
                time.sleep(3 * (attempt + 1))
                continue

            raise e

    raise last_error


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
    """
    Creates embeddings one by one.
    Keeps output dimension fixed at GEMINI_EMBEDDING_DIMENSION.
    """

    embeddings = []

    for text in texts:
        if text and text.strip():
            embedding = create_embedding(text.strip())
            embeddings.append(embedding)

    return embeddings