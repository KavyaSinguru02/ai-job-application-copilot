import numpy as np


def cosine_similarity(vector_a: list[float], vector_b: list[float]) -> float:
    """
    Calculates cosine similarity between two vectors.
    Score range:
    - 1.0 means very similar
    - 0.0 means unrelated
    """

    a = np.array(vector_a)
    b = np.array(vector_b)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def find_top_matches(
    query_chunks: list[str],
    query_embeddings: list[list[float]],
    document_chunks: list[str],
    document_embeddings: list[list[float]],
    top_k: int = 5
) -> list[dict]:
    """
    For each job description chunk, find the most relevant resume chunk.
    """

    matches = []

    for query_index, query_embedding in enumerate(query_embeddings):
        for doc_index, doc_embedding in enumerate(document_embeddings):
            score = cosine_similarity(query_embedding, doc_embedding)

            matches.append(
                {
                    "job_description_chunk": query_chunks[query_index],
                    "resume_chunk": document_chunks[doc_index],
                    "similarity_score": round(score, 4)
                }
            )

    matches = sorted(
        matches,
        key=lambda item: item["similarity_score"],
        reverse=True
    )

    return matches[:top_k]