from app.ai_skill_matcher import analyze_resume_against_jd
from app.rag_semantic_analyzer import analyze_semantic_similarity


def calculate_match_score(resume_text: str, job_description: str) -> dict:
    """
    Combines:
    1. LLM-based skill and role analysis
    2. Embedding-based semantic vector similarity
    3. Basic RAG evidence from resume chunks
    """

    llm_result = analyze_resume_against_jd(
        resume_text=resume_text,
        job_description=job_description
    )

    semantic_result = analyze_semantic_similarity(
        resume_text=resume_text,
        job_description=job_description
    )

    vector_score = semantic_result.get("vector_semantic_score", 0)
    llm_semantic_score = llm_result.get("semantic_fit_score", 0)

    combined_semantic_score = round(
        (vector_score + llm_semantic_score) / 2
    )

    llm_result["vector_semantic_score"] = vector_score
    llm_result["semantic_fit_score"] = combined_semantic_score
    llm_result["rag_evidence"] = semantic_result.get("top_semantic_matches", [])
    llm_result["resume_chunk_count"] = semantic_result.get("resume_chunk_count", 0)
    llm_result["job_description_chunk_count"] = semantic_result.get(
        "job_description_chunk_count",
        0
    )

    return llm_result