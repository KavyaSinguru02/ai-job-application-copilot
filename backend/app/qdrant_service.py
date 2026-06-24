import os
import uuid
from typing import List

from dotenv import load_dotenv
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY") or None
QDRANT_COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION_NAME",
    "resume_rag_chunks_gemini"
)
VECTOR_SIZE = int(os.getenv("GEMINI_EMBEDDING_DIMENSION", "768"))

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)


def ensure_collection_exists():
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

    ensure_payload_indexes()


def ensure_payload_indexes():
    """
    Qdrant Cloud strict mode requires payload indexes for filtered search.
    We filter by analysis_id, so analysis_id must be indexed as keyword.
    """

    index_fields = [
        ("analysis_id", models.PayloadSchemaType.KEYWORD),
        ("user_email", models.PayloadSchemaType.KEYWORD),
        ("source", models.PayloadSchemaType.KEYWORD),
    ]

    for field_name, field_schema in index_fields:
        try:
            qdrant_client.create_payload_index(
                collection_name=QDRANT_COLLECTION_NAME,
                field_name=field_name,
                field_schema=field_schema,
                wait=True
            )
        except UnexpectedResponse as e:
            error_text = str(e).lower()

            if (
                "already exists" in error_text
                or "already has an index" in error_text
                or "conflict" in error_text
            ):
                continue

            raise e
        except Exception as e:
            error_text = str(e).lower()

            if (
                "already exists" in error_text
                or "already has an index" in error_text
                or "conflict" in error_text
            ):
                continue

            raise e


def upsert_resume_chunks(
    analysis_id: str,
    user_email: str,
    chunks: List[str],
    embeddings: List[List[float]]
):
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
            points=points,
            wait=True
        )


def search_resume_chunks(
    analysis_id: str,
    query_embedding: List[float],
    top_k: int = 5
) -> List[dict]:
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