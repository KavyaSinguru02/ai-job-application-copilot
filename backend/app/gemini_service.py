import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_EMBEDDING_MODEL = os.getenv(
    "GEMINI_EMBEDDING_MODEL",
    "gemini-embedding-001"
)

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_text(prompt: str) -> str:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )

    return response.text or ""


def generate_json(prompt: str) -> dict:
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
    response = client.models.embed_content(
        model=GEMINI_EMBEDDING_MODEL,
        contents=text
    )

    return response.embeddings[0].values


def create_embeddings(texts: list[str]) -> list[list[float]]:
    embeddings = []

    for text in texts:
        if text and text.strip():
            embeddings.append(create_embedding(text.strip()))

    return embeddings