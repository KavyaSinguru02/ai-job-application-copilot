import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "gb")


def is_adzuna_configured() -> bool:
    return bool(ADZUNA_APP_ID and ADZUNA_APP_KEY)


def get_top_companies(role: str, location: str | None = None) -> list[dict]:
    """
    Fetches top employers by vacancy count from Adzuna.
    """

    if not is_adzuna_configured():
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
                    "company_name": item.get("canonical_name", "Unknown"),
                    "vacancy_count": item.get("count", 0),
                    "average_salary": item.get("average_salary"),
                    "source": "Adzuna"
                }
            )

        return companies

    except Exception as e:
        print(f"Adzuna top companies error: {str(e)}")
        return []


def search_jobs(role: str, location: str | None = None, results_per_page: int = 5) -> list[dict]:
    """
    Fetches live job listings from Adzuna.
    """

    if not is_adzuna_configured():
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": role,
        "results_per_page": results_per_page,
        "content-type": "application/json"
    }

    if location:
        params["where"] = location

    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()

        data = response.json()
        results = data.get("results", [])

        jobs = []

        for item in results:
            company = item.get("company", {}) or {}

            jobs.append(
                {
                    "title": item.get("title", ""),
                    "company": company.get("display_name", "Unknown"),
                    "location": item.get("location", {}).get("display_name", ""),
                    "redirect_url": item.get("redirect_url", ""),
                    "description": item.get("description", "")[:500],
                    "salary_min": item.get("salary_min"),
                    "salary_max": item.get("salary_max"),
                    "source": "Adzuna"
                }
            )

        return jobs

    except Exception as e:
        print(f"Adzuna job search error: {str(e)}")
        return []