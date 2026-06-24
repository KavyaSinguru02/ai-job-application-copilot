import uuid
from app.text_chunker import chunk_text
from app.embedding_service import create_embeddings
from app.qdrant_service import upsert_resume_chunks, search_resume_chunks


def calculate_vector_score(matches: list[dict]) -> int:
    """
    Converts average Qdrant similarity into percentage score.
    """

    if not matches:
        return 0

    avg_score = sum(
        item.get("similarity_score", 0)
        for item in matches
    ) / len(matches)

    score = round(avg_score * 100)

    if score < 0:
        return 0

    if score > 100:
        return 100

    return score


def remove_duplicate_matches(matches: list[dict]) -> list[dict]:
    """
    Removes duplicate resume evidence chunks.
    """

    seen = set()
    unique_matches = []

    for item in matches:
        evidence = item.get("matching_resume_evidence", "")

        if evidence not in seen:
            seen.add(evidence)
            unique_matches.append(item)

    return unique_matches


def analyze_with_qdrant_rag(
    resume_text: str,
    job_description: str,
    user_email: str
) -> dict:
    """
    Production-style RAG flow using Qdrant.

    1. Chunk resume
    2. Embed resume chunks
    3. Store resume vectors in Qdrant
    4. Chunk job description
    5. Embed job description chunks
    6. Search Qdrant for relevant resume chunks
    """

    analysis_id = str(uuid.uuid4())

    resume_chunks = chunk_text(resume_text)
    jd_chunks = chunk_text(job_description)

    resume_embeddings = create_embeddings(resume_chunks)
    jd_embeddings = create_embeddings(jd_chunks)

    upsert_resume_chunks(
        analysis_id=analysis_id,
        user_email=user_email,
        chunks=resume_chunks,
        embeddings=resume_embeddings
    )

    all_matches = []

    for jd_chunk, jd_embedding in zip(jd_chunks, jd_embeddings):
        matches = search_resume_chunks(
            analysis_id=analysis_id,
            query_embedding=jd_embedding,
            top_k=3
        )

        for match in matches:
            match["job_requirement"] = jd_chunk
            all_matches.append(match)

    all_matches = sorted(
        all_matches,
        key=lambda item: item.get("similarity_score", 0),
        reverse=True
    )

    top_matches = remove_duplicate_matches(all_matches)[:8]

    vector_score = calculate_vector_score(top_matches)

    return {
        "analysis_id": analysis_id,
        "vector_semantic_score": vector_score,
        "resume_chunk_count": len(resume_chunks),
        "job_description_chunk_count": len(jd_chunks),
        "top_semantic_matches": top_matches,
        "vector_database": "Qdrant"
    }