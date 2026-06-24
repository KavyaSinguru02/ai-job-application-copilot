import os
import logging

from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import Response

from app.resume_parser import extract_resume_text
from app.matcher import calculate_match_score
from app.ai_suggestions import generate_resume_feedback
from app.resume_optimizer import generate_optimized_resume_and_companies
from app.report_generator import generate_pdf_report
from app.auth import get_current_user
from app.analytics import save_analysis_event, get_admin_stats


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Job Application Copilot")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ALLOWED_TESTER_EMAILS = os.getenv("ALLOWED_TESTER_EMAILS", "").strip()


def is_allowed_tester(email: str) -> bool:
    """
    If ALLOWED_TESTER_EMAILS is empty, all logged-in users are allowed.
    If ALLOWED_TESTER_EMAILS has emails, only those users are allowed.
    """

    if not ALLOWED_TESTER_EMAILS:
        return True

    allowed_emails = [
        item.strip().lower()
        for item in ALLOWED_TESTER_EMAILS.split(",")
        if item.strip()
    ]

    return email.lower() in allowed_emails


@app.get("/")
def home():
    return {
        "message": "AI Job Application Copilot API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "AI Job Application Copilot Backend"
    }


@app.post("/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    location: str = Form(default=""),
    user: dict = Depends(get_current_user)
):
    try:
        user_email = user.get("email", "")

        if not is_allowed_tester(user_email):
            raise HTTPException(
                status_code=403,
                detail=(
                    "This app is currently in private beta. "
                    "Please contact the owner for access."
                )
            )

        if not resume.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF resumes are supported."
            )

        if not job_description.strip():
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty."
            )

        resume_text = await extract_resume_text(resume)

        if not resume_text or not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the uploaded resume PDF."
            )

        match_result = calculate_match_score(
            resume_text=resume_text,
            job_description=job_description,
            user_email=user_email or "anonymous"
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

        try:
            save_analysis_event(
                user=user,
                match_result=match_result,
                location=location
            )
        except Exception as analytics_error:
            logger.warning(
                "Analytics save failed: %s",
                str(analytics_error)
            )

        return {
            "user_email": user_email,
            "match_result": match_result,
            "feedback": feedback,
            "optimized_resume": optimized_resume
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Unexpected error during resume analysis")

        raise HTTPException(
            status_code=500,
            detail=f"Unexpected backend error: {str(e)}"
        )


@app.post("/generate-report")
async def generate_report(
    report_data: dict,
    user: dict = Depends(get_current_user)
):
    try:
        pdf_bytes = generate_pdf_report(report_data)

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=resume_analysis_report.pdf"
            }
        )

    except Exception as e:
        logger.exception("PDF report generation failed")

        raise HTTPException(
            status_code=500,
            detail=f"Could not generate PDF report: {str(e)}"
        )


@app.get("/admin/stats")
async def admin_stats(user: dict = Depends(get_current_user)):
    try:
        if user.get("email") != ADMIN_EMAIL:
            raise HTTPException(
                status_code=403,
                detail="You are not allowed to view admin stats."
            )

        stats = get_admin_stats()

        return {
            "total_analyses": len(stats),
            "events": stats
        }

    except HTTPException:
        raise

    except Exception as e:
        logger.exception("Admin stats fetch failed")

        raise HTTPException(
            status_code=500,
            detail=f"Could not fetch admin stats: {str(e)}"
        )