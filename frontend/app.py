import requests
import streamlit as st
from supabase import create_client


st.set_page_config(
    page_title="AI Job Application Copilot",
    page_icon="🤖",
    layout="wide"
)


def get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets[key]
    except Exception:
        return default


SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_ANON_KEY = get_secret("SUPABASE_ANON_KEY")
ADMIN_EMAIL = get_secret("ADMIN_EMAIL")
LINKEDIN_URL = get_secret("LINKEDIN_URL")
GITHUB_URL = get_secret("GITHUB_URL")
BACKEND_URL = get_secret("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

API_URL = f"{BACKEND_URL}/analyze"
REPORT_API_URL = f"{BACKEND_URL}/generate-report"
ADMIN_STATS_URL = f"{BACKEND_URL}/admin/stats"


if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    st.error(
        "Supabase secrets are missing. Please add SUPABASE_URL and SUPABASE_ANON_KEY "
        "in Streamlit secrets."
    )
    st.stop()


supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def init_session_state():
    default_values = {
        "access_token": None,
        "user_email": None,
        "analysis_result": None,
        "is_logged_in": False,
    }

    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_session_state()


def login_user(email: str, password: str):
    response = supabase.auth.sign_in_with_password(
        {
            "email": email,
            "password": password,
        }
    )

    if response.session:
        st.session_state.access_token = response.session.access_token
        st.session_state.user_email = response.user.email
        st.session_state.is_logged_in = True
        st.success("Login successful.")
        st.rerun()
    else:
        st.error("Login failed. Please check your email and password.")


def signup_user(email: str, password: str):
    response = supabase.auth.sign_up(
        {
            "email": email,
            "password": password,
        }
    )

    if response.user:
        if response.session:
            st.session_state.access_token = response.session.access_token
            st.session_state.user_email = response.user.email
            st.session_state.is_logged_in = True
            st.success("Signup successful.")
            st.rerun()
        else:
            st.success(
                "Signup successful. Please check your email and confirm your account if required."
            )
    else:
        st.error("Signup failed. Please try again.")


def logout_user():
    try:
        supabase.auth.sign_out()
    except Exception:
        pass

    st.session_state.access_token = None
    st.session_state.user_email = None
    st.session_state.analysis_result = None
    st.session_state.is_logged_in = False
    st.success("Logged out successfully.")
    st.rerun()


def auth_headers() -> dict:
    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }


def show_login_page():
    st.title("🤖 AI Job Application Copilot")
    st.caption(
        "Upload your resume, paste a job description, and get AI-powered resume insights."
    )

    st.info(
        "This is a beta version. Please avoid uploading highly sensitive personal information."
    )

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        st.subheader("Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if not email or not password:
                st.warning("Please enter both email and password.")
            else:
                try:
                    login_user(email, password)
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

    with tab2:
        st.subheader("Create Account")

        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Sign Up"):
            if not email or not password:
                st.warning("Please enter both email and password.")
            elif len(password) < 6:
                st.warning("Password should be at least 6 characters.")
            else:
                try:
                    signup_user(email, password)
                except Exception as e:
                    st.error(f"Signup failed: {str(e)}")


def show_sidebar():
    with st.sidebar:
        st.title("AI Job Copilot")

        if st.session_state.user_email:
            st.write(f"Logged in as: **{st.session_state.user_email}**")

        st.divider()

        if LINKEDIN_URL:
            st.link_button("LinkedIn", LINKEDIN_URL)

        if GITHUB_URL:
            st.link_button("GitHub Repo", GITHUB_URL)

        st.divider()

        st.caption("Beta app built using Streamlit, FastAPI, Gemini, Qdrant, Supabase, Render, and Adzuna.")

        if st.button("Logout"):
            logout_user()


def safe_get_list(data: dict, key: str) -> list:
    value = data.get(key, [])
    if isinstance(value, list):
        return value
    return []


def show_score_metrics(match_result: dict):
    st.subheader("Match Scores")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Overall Match",
            f"{match_result.get('match_percentage', 0)}%"
        )

    with col2:
        st.metric(
            "ATS Score",
            f"{match_result.get('ats_keyword_score', 0)}%"
        )

    with col3:
        st.metric(
            "Semantic Fit",
            f"{match_result.get('semantic_fit_score', 0)}%"
        )

    with col4:
        st.metric(
            "Vector Score",
            f"{match_result.get('vector_semantic_score', 0)}%"
        )

    st.caption(
        f"Vector database: {match_result.get('vector_database', 'Not available')}"
    )


def show_summary_tab(match_result: dict):
    st.subheader("Overall Summary")

    st.write("**Target Role:**", match_result.get("target_role", "Not detected"))

    st.markdown("### Resume Summary")
    st.write(match_result.get("resume_summary", "Not available"))

    st.markdown("### Job Description Summary")
    st.write(match_result.get("job_summary", "Not available"))

    st.markdown("### Strengths")
    strengths = safe_get_list(match_result, "strengths")

    if strengths:
        for item in strengths:
            st.write(f"- {item}")
    else:
        st.write("No strengths found.")

    st.markdown("### Improvement Areas")
    improvement_areas = safe_get_list(match_result, "improvement_areas")

    if improvement_areas:
        for item in improvement_areas:
            st.write(f"- {item}")
    else:
        st.write("No improvement areas found.")


def show_matched_skills_tab(match_result: dict):
    st.subheader("Matched Skills")

    matched_skills = safe_get_list(match_result, "matched_skills")

    if not matched_skills:
        st.write("No matched skills found.")
        return

    for skill in matched_skills:
        st.markdown(f"**Job Skill:** {skill.get('job_skill', '')}")
        st.write(f"Resume Skill: {skill.get('resume_skill', '')}")
        st.write(f"Match Type: {skill.get('match_type', '')}")
        st.write(f"Explanation: {skill.get('explanation', '')}")
        st.divider()


def show_missing_skills_tab(match_result: dict):
    st.subheader("Missing or Weak Skills")

    missing_skills = safe_get_list(match_result, "missing_skills")

    if not missing_skills:
        st.success("No major missing skills found.")
        return

    for skill in missing_skills:
        st.markdown(f"**{skill.get('skill', '')}**")
        st.write(f"Category: {skill.get('category', '')}")
        st.write(f"Importance: {skill.get('importance', '')}")
        st.write(f"Why it matters: {skill.get('why_it_matters', '')}")
        st.write(f"Resume suggestion: {skill.get('resume_edit_suggestion', '')}")
        st.divider()


def show_rag_tab(match_result: dict):
    st.subheader("RAG Evidence")

    st.write(
        "These are resume sections retrieved from the vector database as evidence "
        "against the job description."
    )

    st.metric(
        "Vector Semantic Score",
        f"{match_result.get('vector_semantic_score', 0)}%"
    )

    st.write(f"Resume Chunks: {match_result.get('resume_chunk_count', 0)}")
    st.write(f"Job Description Chunks: {match_result.get('job_description_chunk_count', 0)}")

    rag_evidence = safe_get_list(match_result, "rag_evidence")

    if not rag_evidence:
        st.write("No RAG evidence available.")
        return

    for item in rag_evidence:
        st.markdown(f"**Similarity Score:** {item.get('similarity_score', '')}")
        st.markdown("**Job Requirement:**")
        st.write(item.get("job_requirement", ""))

        st.markdown("**Matching Resume Evidence:**")
        st.write(item.get("matching_resume_evidence", ""))

        st.divider()


def show_feedback_tab(feedback: str):
    st.subheader("AI Resume Feedback")

    if feedback:
        st.markdown(feedback)
    else:
        st.write("No feedback available.")


def show_optimized_resume_tab(optimized: dict):
    st.subheader("Optimized Resume Suggestions")

    st.caption(
        optimized.get(
            "company_data_note",
            "Company suggestions may include AI-generated recommendations and live job data when available."
        )
    )

    st.markdown("### Optimized Resume Headline")
    st.write(optimized.get("optimized_resume_headline", ""))

    st.markdown("### Optimized Professional Summary")
    st.write(optimized.get("optimized_professional_summary", ""))

    st.markdown("### Skills to Highlight")
    skills = optimized.get("optimized_skills_section", [])

    if skills:
        for skill in skills:
            st.write(f"- {skill}")
    else:
        st.write("No skills suggested.")

    st.markdown("### Improved Experience Bullets")
    bullets = optimized.get("optimized_experience_bullets", [])

    if bullets:
        for bullet in bullets:
            st.write(f"- {bullet}")
    else:
        st.write("No experience bullets suggested.")

    st.markdown("### Project Bullet Suggestions")
    project_bullets = optimized.get("optimized_project_bullets", [])

    if project_bullets:
        for bullet in project_bullets:
            st.write(f"- {bullet}")
    else:
        st.write("No project bullets suggested.")

    st.markdown("### ATS Keywords to Include")
    keywords = optimized.get("ats_keywords_to_include", [])

    if keywords:
        st.write(", ".join(keywords))
    else:
        st.write("No ATS keywords suggested.")

    st.markdown("### Keywords Not to Add Without Real Experience")
    risky_keywords = optimized.get("keywords_not_to_add_without_real_experience", [])

    if risky_keywords:
        for keyword in risky_keywords:
            st.write(f"- {keyword}")
    else:
        st.write("No warning keywords found.")

    st.markdown("### Similar Roles to Apply")
    similar_roles = optimized.get("similar_roles_to_apply", [])

    if similar_roles:
        for role in similar_roles:
            st.markdown(f"**{role.get('role_title', '')}**")
            st.write(role.get("why_it_matches", ""))

            skills_to_improve = role.get("skills_to_improve", [])
            if skills_to_improve:
                st.write("Skills to improve:")
                for skill in skills_to_improve:
                    st.write(f"- {skill}")

            st.divider()
    else:
        st.write("No similar roles suggested.")

    st.markdown("### Final Resume Strategy")
    st.write(optimized.get("final_resume_strategy", ""))


def show_companies_and_jobs_tab(optimized: dict):
    st.subheader("Companies and Live Jobs")

    st.caption(
        optimized.get(
            "company_data_note",
            "Live job data is shown when available."
        )
    )

    live_top_companies = optimized.get("live_top_companies", [])

    st.markdown("### Live Top Companies from Adzuna")

    if live_top_companies:
        for company in live_top_companies:
            company_name = company.get("company_name", "Unknown")
            vacancy_count = company.get("vacancy_count", 0)
            average_salary = company.get("average_salary")

            st.markdown(f"**{company_name}**")
            st.write(f"Vacancies: {vacancy_count}")

            if average_salary:
                st.write(f"Average Salary: {average_salary}")

            st.caption("Source: Adzuna")
            st.divider()
    else:
        st.write("No live top companies available from Adzuna.")

    recommended_companies = optimized.get("recommended_companies", [])

    st.markdown("### AI Recommended Companies")

    if recommended_companies:
        for company in recommended_companies:
            st.markdown(f"**{company.get('company_name', '')}**")
            st.write(company.get("why_suitable", ""))
            st.write(company.get("role_fit_reason", ""))

            search_keywords = company.get("search_keywords", [])
            if search_keywords:
                st.write("Search keywords:")
                st.write(", ".join(search_keywords))

            st.divider()
    else:
        st.write("No recommended companies available.")

    live_jobs = optimized.get("live_jobs", [])

    st.markdown("### Live Job Listings from Adzuna")

    if live_jobs:
        for job in live_jobs:
            title = job.get("title", "")
            company = job.get("company", "")
            location = job.get("location", "")
            redirect_url = job.get("redirect_url", "")
            description = job.get("description", "")
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")

            st.markdown(f"**{title}**")
            st.write(f"Company: {company}")
            st.write(f"Location: {location}")

            if salary_min or salary_max:
                st.write(f"Salary Range: {salary_min or 'N/A'} - {salary_max or 'N/A'}")

            if description:
                with st.expander("View job description preview"):
                    st.write(description)

            if redirect_url:
                st.link_button("View Job", redirect_url)

            st.caption("Source: Adzuna")
            st.divider()
    else:
        st.write("No live job listings available from Adzuna.")


def show_raw_json_tab(result: dict):
    st.subheader("Raw JSON Response")
    st.json(result)


def show_download_report(result: dict):
    st.subheader("Download Report")

    if st.button("Generate PDF Report"):
        try:
            response = requests.post(
                REPORT_API_URL,
                json=result,
                headers=auth_headers(),
                timeout=120
            )

            if response.status_code == 200:
                st.download_button(
                    label="Download Resume Analysis Report",
                    data=response.content,
                    file_name="resume_analysis_report.pdf",
                    mime="application/pdf"
                )
            else:
                try:
                    error_detail = response.json().get("detail", response.text)
                except Exception:
                    error_detail = response.text

                st.error(f"Report generation failed: {error_detail}")

        except Exception as e:
            st.error(f"Could not generate report: {str(e)}")


def show_analysis_result():
    result = st.session_state.analysis_result

    if not result:
        return

    match_result = result.get("match_result", {})
    feedback = result.get("feedback", "")
    optimized = result.get("optimized_resume", {})

    st.success("Analysis completed successfully.")

    show_score_metrics(match_result)

    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(
        [
            "Summary",
            "Skills",
            "Gaps",
            "RAG",
            "Feedback",
            "Resume",
            "Jobs",
            "JSON",
        ]
    )

    with tab1:
        show_summary_tab(match_result)

    with tab2:
        show_matched_skills_tab(match_result)

    with tab3:
        show_missing_skills_tab(match_result)

    with tab4:
        show_rag_tab(match_result)

    with tab5:
        show_feedback_tab(feedback)

    with tab6:
        show_optimized_resume_tab(optimized)

    with tab7:
        show_companies_and_jobs_tab(optimized)

    with tab8:
        show_raw_json_tab(result)

    show_download_report(result)


def show_admin_dashboard():
    if st.session_state.user_email != ADMIN_EMAIL:
        return

    with st.expander("Admin Analytics Dashboard"):
        if st.button("Load Admin Stats"):
            try:
                response = requests.get(
                    ADMIN_STATS_URL,
                    headers=auth_headers(),
                    timeout=60
                )

                if response.status_code == 200:
                    data = response.json()
                    st.metric("Total Analyses", data.get("total_analyses", 0))

                    events = data.get("events", [])
                    if events:
                        st.dataframe(events, use_container_width=True)
                    else:
                        st.write("No analytics events found.")
                else:
                    try:
                        error_detail = response.json().get("detail", response.text)
                    except Exception:
                        error_detail = response.text

                    st.error(f"Could not load admin stats: {error_detail}")

            except Exception as e:
                st.error(f"Admin stats error: {str(e)}")


def show_main_app():
    show_sidebar()

    st.title("🤖 AI Job Application Copilot")

    st.caption(
        "Beta version: The first request may take some time if the backend is waking up."
    )

    st.info(
        "For best experience, use desktop or laptop. Mobile browser works, "
        "but PDF upload and long reports are easier on a larger screen."
    )

    st.markdown(
        """
This app helps you compare your resume with a job description and gives:

- Match percentage
- Missing skills
- ATS keyword suggestions
- Resume improvement suggestions
- RAG-based resume evidence
- Live job listings from Adzuna
- Company suggestions
- Downloadable PDF report
"""
    )

    st.divider()

    with st.form("resume_analysis_form"):
        uploaded_resume = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"]
        )

        job_description = st.text_area(
            "Paste Job Description",
            height=250,
            placeholder="Paste the full job description here..."
        )

        location = st.text_input(
            "Preferred Location",
            placeholder="Example: Krakow, London, Remote"
        )

        submitted = st.form_submit_button("Analyze Resume")

    if submitted:
        if uploaded_resume is None:
            st.warning("Please upload your resume PDF.")
            return

        if not job_description.strip():
            st.warning("Please paste a job description.")
            return

        with st.spinner("Analyzing resume. This may take some time..."):
            try:
                files = {
                    "resume": (
                        uploaded_resume.name,
                        uploaded_resume.getvalue(),
                        "application/pdf"
                    )
                }

                data = {
                    "job_description": job_description,
                    "location": location
                }

                response = requests.post(
                    API_URL,
                    files=files,
                    data=data,
                    headers=auth_headers(),
                    timeout=240
                )

                if response.status_code == 200:
                    st.session_state.analysis_result = response.json()
                    st.rerun()
                else:
                    try:
                        error_detail = response.json().get("detail", response.text)
                    except Exception:
                        error_detail = response.text

                    st.error(f"Backend error: {error_detail}")

            except requests.exceptions.Timeout:
                st.error(
                    "The request timed out. The backend may be waking up or the analysis took too long. "
                    "Please try again."
                )

            except Exception as e:
                st.error(f"Something went wrong: {str(e)}")

    if st.session_state.analysis_result:
        st.divider()
        show_analysis_result()

    st.divider()
    show_admin_dashboard()


if not st.session_state.is_logged_in:
    show_login_page()
else:
    show_main_app()