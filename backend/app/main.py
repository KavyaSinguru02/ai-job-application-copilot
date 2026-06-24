import os
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import Response
from dotenv import load_dotenv

from app.resume_parser import extract_resume_text
from app.matcher import calculate_match_score
from app.ai_suggestions import generate_resume_feedback
from app.resume_optimizer import generate_optimized_resume_and_companies
from app.report_generator import generate_pdf_report
from app.auth import get_current_user
from app.analytics import save_analysis_event, get_admin_stats

load_dotenv()

app = FastAPI(title="AI Job Application Copilot")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")


@app.get("/")
def home():
    return {
        "message": "AI Job Application Copilot API is running"
    }


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    location: str = Form(default=""),
    user: dict = Depends(get_current_user)
):
    resume_text = await extract_resume_text(resume)

    match_result = calculate_match_score(
        resume_text=resume_text,
        job_description=job_description,
        user_email=user.get("email", "anonymous")
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

    save_analysis_event(
        user=user,
        match_result=match_result,
        location=location
    )

    return {
        "user_email": user.get("email"),
        "match_result": match_result,
        "feedback": feedback,
        "optimized_resume": optimized_resume
    }


@app.post("/generate-report")
async def generate_report(
    report_data: dict,
    user: dict = Depends(get_current_user)
):
    pdf_bytes = generate_pdf_report(report_data)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=resume_analysis_report.pdf"
        }
    )


@app.get("/admin/stats")
async def admin_stats(user: dict = Depends(get_current_user)):
    if user.get("email") != ADMIN_EMAIL:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to view admin stats"
        )

    stats = get_admin_stats()

    return {
        "total_analyses": len(stats),
        "events": stats
    }