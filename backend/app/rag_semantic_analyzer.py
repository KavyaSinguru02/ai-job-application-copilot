from app.text_chunker import chunk_text
from app.embedding_service import create_embeddings
from app.vector_similarity import find_top_matches


def calculate_vector_score(top_matches: list[dict]) -> int:
    """
    Converts vector similarity into a percentage score.
    """

    if not top_matches:
        return 0

    avg_similarity = sum(
        item["similarity_score"]
        for item in top_matches
    ) / len(top_matches)

    score = round(avg_similarity * 100)

    if score < 0:
        return 0

    if score > 100:
        return 100

    return score


def analyze_semantic_similarity(
    resume_text: str,
    job_description: str
) -> dict:
    """
    Builds a simple RAG-style semantic analysis.

    It retrieves the most relevant resume chunks for the job description.
    """

    resume_chunks = chunk_text(resume_text)
    jd_chunks = chunk_text(job_description)

    resume_embeddings = create_embeddings(resume_chunks)
    jd_embeddings = create_embeddings(jd_chunks)

    top_matches = find_top_matches(
        query_chunks=jd_chunks,
        query_embeddings=jd_embeddings,
        document_chunks=resume_chunks,
        document_embeddings=resume_embeddings,
        top_k=6
    )

    vector_score = calculate_vector_score(top_matches)

    rag_context = []

    for match in top_matches:
        rag_context.append(
            {
                "similarity_score": match["similarity_score"],
                "job_requirement": match["job_description_chunk"],
                "matching_resume_evidence": match["resume_chunk"]
            }
        )

    return {
        "vector_semantic_score": vector_score,
        "resume_chunk_count": len(resume_chunks),
        "job_description_chunk_count": len(jd_chunks),
        "top_semantic_matches": rag_context
    }