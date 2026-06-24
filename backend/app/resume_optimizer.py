from app.gemini_service import generate_json
from app.adzuna_service import get_top_companies, search_jobs


def generate_optimized_resume_and_companies(
    resume_text: str,
    job_description: str,
    match_result: dict,
    location: str | None = None
) -> dict:
    target_role = match_result.get("target_role", "Software Engineer")

    live_top_companies = get_top_companies(
        role=target_role,
        location=location
    )

    live_jobs = search_jobs(
        role=target_role,
        location=location,
        results_per_page=5
    )

    prompt = f"""
You are an expert resume strategist and career advisor.

Return only valid JSON with this exact structure:

{{
  "optimized_resume_headline": "",
  "optimized_professional_summary": "",
  "optimized_skills_section": [],
  "optimized_experience_bullets": [],
  "optimized_project_bullets": [],
  "ats_keywords_to_include": [],
  "keywords_not_to_add_without_real_experience": [],
  "target_company_types": [],
  "recommended_companies": [
    {{
      "company_name": "",
      "why_suitable": "",
      "role_fit_reason": "",
      "search_keywords": []
    }}
  ],
  "similar_roles_to_apply": [
    {{
      "role_title": "",
      "why_it_matches": "",
      "skills_to_improve": []
    }}
  ],
  "linkedin_search_keywords": [],
  "final_resume_strategy": "",
  "company_data_note": ""
}}

Rules:
- Do not invent fake experience.
- Use live Adzuna job/company data if available.
- If Adzuna data is empty, give AI-generated strategic suggestions.
- Suggest company types and example companies based on the role.
- If location is provided, consider it.
- Keep suggestions practical.

Preferred Location:
{location or "Not provided"}

Target Role:
{target_role}

Resume:
{resume_text[:8000]}

Job Description:
{job_description[:8000]}

Match Result:
{match_result}

Live Adzuna Top Companies:
{live_top_companies}

Live Adzuna Job Listings:
{live_jobs}
"""

    result = generate_json(prompt)

    result["live_top_companies"] = live_top_companies
    result["live_jobs"] = live_jobs

    if live_top_companies or live_jobs:
        result["company_data_note"] = (
            "Company and job suggestions include live job-market data from Adzuna."
        )
    else:
        result["company_data_note"] = (
            "No live Adzuna data was available. Company suggestions are AI-generated strategic recommendations."
        )

    return result