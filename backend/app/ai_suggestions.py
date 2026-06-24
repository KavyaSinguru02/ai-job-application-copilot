from app.gemini_service import generate_text


def generate_resume_feedback(
    resume_text: str,
    job_description: str,
    match_result: dict
) -> str:
    prompt = f"""
You are an expert AI career coach and resume optimization assistant.

Analyze the resume and job description using the match result.

Match result:
{match_result}

Resume:
{resume_text[:8000]}

Job Description:
{job_description[:8000]}

Return the response in this structure:

1. Overall Match Summary
2. Why This Match Percentage Was Given
3. Strongest Matching Skills
4. Missing or Weak Skills
5. Resume Evidence Found
6. Resume Improvement Suggestions
7. Improved Resume Bullet Points
8. Keywords to Add
9. Interview Preparation Questions
10. Learning Roadmap

Important:
- Do not invent fake experience.
- Suggest keywords only if the candidate truly has experience or can learn them.
"""

    return generate_text(prompt)