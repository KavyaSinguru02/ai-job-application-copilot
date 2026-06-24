import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "gb")


def get_live_top_companies(role: str, location: str | None = None) -> list[dict]:
    """
    Optional live job-market feature using Adzuna.
    Returns companies with high vacancy counts for a role.
    If API keys are missing, returns an empty list.
    """

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/top_companies"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": role,
        "content-type": "application/json"
    }

    if location:
        params["where"] = location

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()
        leaderboard = data.get("leaderboard", [])

        companies = []

        for item in leaderboard:
            companies.append(
                {
                    "company_name": item.get("canonical_name"),
                    "vacancy_count": item.get("count"),
                    "average_salary": item.get("average_salary"),
                    "source": "Adzuna"
                }
            )

        return companies

    except Exception:
        return []