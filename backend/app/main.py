from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import Response
from app.resume_parser import extract_resume_text
from app.matcher import calculate_match_score
from app.ai_suggestions import generate_resume_feedback
from app.resume_optimizer import generate_optimized_resume_and_companies
from app.report_generator import generate_pdf_report

app = FastAPI(title="AI Job Application Copilot")


@app.get("/")
def home():
    return {
        "message": "AI Job Application Copilot API is running"
    }


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    location: str = Form(default="")
):
    resume_text = await extract_resume_text(resume)

    match_result = calculate_match_score(
        resume_text=resume_text,
        job_description=job_description
    )

    feedback = generate_resume_feedback(
        resume_text=resume_text,
        job_description=job_description,
        match_result=match_result
    )

    optimized_resume = generate_optimized_resume_and_companies(
        resume_text=resume_text,
        job_description=job_description,
        match_result=match_result,
        location=location if location else None
    )

    return {
        "match_result": match_result,
        "feedback": feedback,
        "optimized_resume": optimized_resume
    }


@app.post("/generate-report")
async def generate_report(report_data: dict):
    pdf_bytes = generate_pdf_report(report_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=resume_analysis_report.pdf"
        }
    )