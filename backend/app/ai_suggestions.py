import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_resume_feedback(resume_text, job_description):
    prompt = f"""
You are an AI career assistant.

Compare this resume with the job description.

Return:
1. Resume match summary
2. Missing skills
3. Resume improvement suggestions
4. Better bullet points
5. Interview preparation questions

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    return response.output_text