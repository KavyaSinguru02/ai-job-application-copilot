from app.ai_skill_matcher import analyze_resume_against_jd
from app.qdrant_rag_analyzer import analyze_with_qdrant_rag


def calculate_match_score(
    resume_text: str,
    job_description: str,
    user_email: str = "anonymous"
) -> dict:
    """
    Combines:
    1. LLM-based skill analysis
    2. Qdrant vector database retrieval
    3. RAG evidence
    """

    llm_result = analyze_resume_against_jd(
        resume_text=resume_text,
        job_description=job_description
    )

    rag_result = analyze_with_qdrant_rag(
        resume_text=resume_text,
        job_description=job_description,
        user_email=user_email
    )

    vector_score = rag_result.get("vector_semantic_score", 0)
    llm_semantic_score = llm_result.get("semantic_fit_score", 0)

    combined_semantic_score = round(
        (vector_score + llm_semantic_score) / 2
    )

    llm_result["analysis_id"] = rag_result.get("analysis_id")
    llm_result["vector_database"] = rag_result.get("vector_database")
    llm_result["vector_semantic_score"] = vector_score
    llm_result["semantic_fit_score"] = combined_semantic_score
    llm_result["rag_evidence"] = rag_result.get("top_semantic_matches", [])
    llm_result["resume_chunk_count"] = rag_result.get("resume_chunk_count", 0)
    llm_result["job_description_chunk_count"] = rag_result.get(
        "job_description_chunk_count",
        0
    )

    return llm_result