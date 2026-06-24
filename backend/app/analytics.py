import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


def save_analysis_event(
    user: dict,
    match_result: dict,
    location: str
):
    data = {
        "user_id": user.get("user_id"),
        "email": user.get("email"),
        "target_role": match_result.get("target_role"),
        "location": location,
        "match_percentage": match_result.get("match_percentage"),
        "ats_keyword_score": match_result.get("ats_keyword_score"),
        "semantic_fit_score": match_result.get("semantic_fit_score")
    }

    supabase.table("analysis_events").insert(data).execute()


def get_admin_stats():
    response = (
        supabase
        .table("analysis_events")
        .select("*")
        .order("created_at", desc=True)
        .execute()
    )

    return response.data