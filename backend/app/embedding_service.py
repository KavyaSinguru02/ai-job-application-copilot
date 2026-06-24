import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = os.getenv(
    "OPENAI_EMBEDDING_MODEL",
    "text-embedding-3-small"
)


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Converts text chunks into embedding vectors.
    """

    clean_texts = [
        text.strip()
        for text in texts
        if text and text.strip()
    ]

    if not clean_texts:
        return []

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=clean_texts
    )

    return [
        item.embedding
        for item in response.data
    ]