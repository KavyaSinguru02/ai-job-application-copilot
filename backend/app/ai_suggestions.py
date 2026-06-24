import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")


def generate_resume_feedback(resume_text: str, job_description: str, match_result: dict) -> str:
    prompt = f"""
You are an expert AI career coach and resume optimization assistant.

The system already analyzed the resume and job description.

Match result:
{match_result}

Resume:
{resume_text[:10000]}

Job Description:
{job_description[:10000]}

Return the response in this exact structure:

1. Overall Match Summary
Explain how suitable the candidate is for this role.

2. Why This Match Percentage Was Given
Explain the score clearly.

3. Strongest Matching Skills
Mention the strongest skills already present in the resume.

4. Missing or Weak Skills
Mention important missing or weak skills.

5. Resume Improvement Suggestions
Give practical edits to improve the resume for this job.

6. Improved Resume Bullet Points
Rewrite 5 stronger, ATS-friendly bullet points.

7. Keywords to Add
List keywords from the job description that should be added only if the candidate truly has experience.

8. Interview Preparation Questions
Generate 10 likely interview questions.

9. Learning Roadmap
Suggest a short roadmap for the missing skills.
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt
    )

    return response.output_text