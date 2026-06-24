import os
from typing import List
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


class SkillItem(BaseModel):
    name: str = Field(description="Skill, tool, framework, concept, or domain knowledge")
    category: str = Field(description="Example: programming, backend, cloud, database, AI, soft skill, domain")
    importance: str = Field(description="must_have, nice_to_have, preferred, or unknown")
    evidence: str = Field(description="Short text showing where this skill was found")


class MatchedSkill(BaseModel):
    job_skill: str
    resume_skill: str
    match_type: str = Field(description="exact, similar, inferred, or partial")
    explanation: str


class MissingSkill(BaseModel):
    skill: str
    category: str
    importance: str
    why_it_matters: str
    resume_edit_suggestion: str


class ResumeJDMatchResult(BaseModel):
    target_role: str
    match_percentage: int
    ats_keyword_score: int
    semantic_fit_score: int

    resume_skills: List[SkillItem]
    job_required_skills: List[SkillItem]

    matched_skills: List[MatchedSkill]
    missing_skills: List[MissingSkill]

    strengths: List[str]
    improvement_areas: List[str]
    resume_summary: str
    job_summary: str


def analyze_resume_against_jd(resume_text: str, job_description: str) -> dict:
    """
    Dynamically extracts skills from resume and job description.
    Does not depend on predefined skill lists.
    """

    prompt = f"""
You are an expert AI resume screening system and technical recruiter.

Analyze the resume against the job description.

Important rules:
- Do NOT use a fixed skill list.
- Dynamically extract all skills from the given resume and job description.
- Include programming languages, frameworks, tools, databases, cloud platforms, AI/ML skills,
  certifications, methodologies, domain skills, soft skills, and experience requirements.
- Treat similar skills intelligently.
  Example: "REST APIs" and "API development" are related.
  Example: "AWS EKS" and "Kubernetes" are related but not identical.
- Do not falsely claim a match if the resume does not show enough evidence.
- Give a realistic match percentage.
- Prioritize must-have job requirements more than nice-to-have skills.

Resume:
{resume_text[:12000]}

Job Description:
{job_description[:12000]}
"""

    response = client.responses.parse(
        model=MODEL_NAME,
        input=[
            {
                "role": "system",
                "content": "You extract and compare resume and job description skills using structured output."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        text_format=ResumeJDMatchResult,
    )

    result = response.output_parsed
    return result.model_dump()