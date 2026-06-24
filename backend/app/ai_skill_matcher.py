from app.gemini_service import generate_json


def analyze_resume_against_jd(resume_text: str, job_description: str) -> dict:
    prompt = f"""
You are an expert resume screening system and technical recruiter.

Analyze the resume against the job description.

Return only valid JSON with this exact structure:

{{
  "target_role": "",
  "match_percentage": 0,
  "ats_keyword_score": 0,
  "semantic_fit_score": 0,
  "resume_skills": [
    {{
      "name": "",
      "category": "",
      "importance": "",
      "evidence": ""
    }}
  ],
  "job_required_skills": [
    {{
      "name": "",
      "category": "",
      "importance": "",
      "evidence": ""
    }}
  ],
  "matched_skills": [
    {{
      "job_skill": "",
      "resume_skill": "",
      "match_type": "",
      "explanation": ""
    }}
  ],
  "missing_skills": [
    {{
      "skill": "",
      "category": "",
      "importance": "",
      "why_it_matters": "",
      "resume_edit_suggestion": ""
    }}
  ],
  "strengths": [],
  "improvement_areas": [],
  "resume_summary": "",
  "job_summary": ""
}}

Rules:
- Do not use a fixed skill list.
- Dynamically extract all skills from the resume and job description.
- Do not invent fake experience.
- Give realistic scores.
- Prioritize must-have job requirements.

Resume:
{resume_text[:10000]}

Job Description:
{job_description[:10000]}
"""

    return generate_json(prompt)