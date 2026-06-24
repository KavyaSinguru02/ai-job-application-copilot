import os
import uuid
from typing import List
from dotenv import load_dotenv
from qdrant_client import QdrantClient, models

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
QDRANT_COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION_NAME",
    "resume_rag_chunks"
)

VECTOR_SIZE = int(os.getenv("OPENAI_EMBEDDING_DIMENSION", "1536"))

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


def ensure_collection_exists():
    """
    Creates the Qdrant collection if it does not already exist.
    """

    collection_exists = qdrant_client.collection_exists(
        collection_name=QDRANT_COLLECTION_NAME
    )

    if not collection_exists:
        qdrant_client.create_collection(
            collection_name=QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )


def upsert_resume_chunks(
    analysis_id: str,
    user_email: str,
    chunks: List[str],
    embeddings: List[List[float]]
):
    """
    Stores resume chunks and their vectors in Qdrant.

    Payload is metadata attached to each vector.
    """

    ensure_collection_exists()

    points = []

    for chunk, embedding in zip(chunks, embeddings):
        points.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "analysis_id": analysis_id,
                    "user_email": user_email,
                    "source": "resume",
                    "chunk_text": chunk
                }
            )
        )

    if points:
        qdrant_client.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=points
        )


def search_resume_chunks(
    analysis_id: str,
    query_embedding: List[float],
    top_k: int = 5
) -> List[dict]:
    """
    Searches Qdrant for resume chunks related to the job description query.
    """

    ensure_collection_exists()

    search_result = qdrant_client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_embedding,
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="analysis_id",
                    match=models.MatchValue(value=analysis_id)
                )
            ]
        ),
        limit=top_k,
        with_payload=True
    )

    matches = []

    for point in search_result.points:
        payload = point.payload or {}

        matches.append(
            {
                "similarity_score": round(point.score, 4),
                "matching_resume_evidence": payload.get("chunk_text", ""),
                "analysis_id": payload.get("analysis_id", ""),
                "source": payload.get("source", "")
            }
        )

    return matches