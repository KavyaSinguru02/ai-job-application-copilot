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

Match result including semantic vector score and RAG evidence:
{match_result}

Use the rag_evidence field to explain which resume sections are most relevant to the job description.
If the evidence is weak, say that clearly.

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

5. Resume Evidence Found
Explain which resume sections matched the job description based on RAG evidence.

6. Resume Improvement Suggestions
Give practical edits to improve the resume for this job.

7. Improved Resume Bullet Points
Rewrite 5 stronger, ATS-friendly bullet points.

8. Keywords to Add
List keywords from the job description that should be added only if the candidate truly has experience.

9. Interview Preparation Questions
Generate 10 likely interview questions.

10. Learning Roadmap
Suggest a short roadmap for the missing skills.
"""

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt
    )

    return response.output_text