from app.ai_skill_matcher import analyze_resume_against_jd


def calculate_match_score(resume_text: str, job_description: str) -> dict:
    return analyze_resume_against_jd(
        resume_text=resume_text,
        job_description=job_description
    )