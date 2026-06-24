import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field
from app.company_recommender import get_live_top_companies

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


class TargetCompany(BaseModel):
    company_name: str
    why_suitable: str
    role_fit_reason: str
    search_keywords: List[str]


class SimilarRole(BaseModel):
    role_title: str
    why_it_matches: str
    missing_skills_to_improve: List[str]


class OptimizedResumeResult(BaseModel):
    optimized_resume_headline: str
    optimized_professional_summary: str
    optimized_skills_section: List[str]
    optimized_project_bullets: List[str]
    optimized_experience_bullets: List[str]
    ats_keywords_to_include: List[str]
    keywords_not_to_add_without_real_experience: List[str]
    target_company_types: List[str]
    recommended_companies: List[TargetCompany]
    similar_roles_to_apply: List[SimilarRole]
    linkedin_search_keywords: List[str]
    naukri_search_keywords: List[str]
    indeed_search_keywords: List[str]
    final_resume_strategy: str


def generate_optimized_resume_and_companies(
    resume_text: str,
    job_description: str,
    match_result: dict,
    location: str | None = None
) -> dict:
    target_role = match_result.get("target_role", "the target role")

    live_companies = get_live_top_companies(
        role=target_role,
        location=location
    )

    prompt = f"""
You are an expert resume strategist, ATS optimization expert, and AI career advisor.

The user wants to create a job-specific resume and find companies where this role is commonly hired.

Important rules:
- Do not invent fake experience.
- Do not tell the candidate to add skills they do not actually have.
- Suggest keywords only if they are supported by the resume or can be learned honestly.
- Generate a resume strategy suitable for the given job description.
- Suggest target company types and example companies.
- If live company data is provided, prioritize those companies.
- If live company data is empty, provide general company recommendations based on the role, industry, and skills.
- Include search keywords for LinkedIn, Naukri, Indeed, and similar job portals.
- Suggest similar roles the candidate can apply for.

Resume:
{resume_text[:12000]}

Job Description:
{job_description[:12000]}

Match Result:
{match_result}

Live Company Data:
{live_companies}
"""

    response = client.responses.parse(
        model=MODEL_NAME,
        input=[
            {
                "role": "system",
                "content": "You generate optimized resume guidance and target company recommendations using structured output."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        text_format=OptimizedResumeResult,
    )

    result = response.output_parsed.model_dump()

    result["live_top_companies"] = live_companies
    result["company_data_note"] = (
        "Live company data is from Adzuna."
        if live_companies
        else "No live company API data was available. Company recommendations are AI-generated strategic suggestions, not live vacancy counts."
    )

    return result