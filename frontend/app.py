import streamlit as st
import requests
import pandas as pd
from supabase import create_client


BACKEND_URL = st.secrets["BACKEND_URL"]
API_URL = f"{BACKEND_URL}/analyze"
REPORT_API_URL = f"{BACKEND_URL}/generate-report"
ADMIN_STATS_URL = f"{BACKEND_URL}/admin/stats"

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_ANON_KEY = st.secrets["SUPABASE_ANON_KEY"]
ADMIN_EMAIL = st.secrets["ADMIN_EMAIL"]

LINKEDIN_URL = st.secrets["LINKEDIN_URL"]
GITHUB_URL = st.secrets["GITHUB_URL"]

supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


st.set_page_config(
    page_title="AI Job Application Copilot",
    page_icon="💼",
    layout="wide"
)


def init_session():
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    if "user_email" not in st.session_state:
        st.session_state.user_email = None


def signup(email, password):
    return supabase.auth.sign_up(
        {
            "email": email,
            "password": password
        }
    )


def login(email, password):
    response = supabase.auth.sign_in_with_password(
        {
            "email": email,
            "password": password
        }
    )

    st.session_state.access_token = response.session.access_token
    st.session_state.user_email = response.user.email


def logout():
    st.session_state.access_token = None
    st.session_state.user_email = None


def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.access_token}"
    }


def render_header():
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("💼 AI Job Application Copilot")
        st.write(
            "Analyze your resume against a job description, find missing skills, "
            "generate resume improvements, and discover companies to target."
        )

    with col2:
        st.markdown(f"[LinkedIn]({LINKEDIN_URL})")
        st.markdown(f"[GitHub Repo]({GITHUB_URL})")


def render_login():
    st.subheader("Login or Create Account")

    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            try:
                login(email, password)
                st.success("Logged in successfully.")
                st.rerun()
            except Exception as e:
                st.error("Login failed. Check your email, password, or email verification.")
                st.write(str(e))

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_password")

        if st.button("Create Account"):
            try:
                signup(email, password)
                st.success(
                    "Account created. Please check your email and confirm your account before logging in."
                )
            except Exception as e:
                st.error("Signup failed.")
                st.write(str(e))


def render_admin_dashboard():
    st.divider()
    st.header("Admin Dashboard")

    if st.session_state.user_email != ADMIN_EMAIL:
        st.info("Admin dashboard is visible only to the owner.")
        return

    if st.button("Load Admin Stats"):
        try:
            response = requests.get(
                ADMIN_STATS_URL,
                headers=auth_headers(),
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])

                st.metric("Total Analyses", data.get("total_analyses", 0))

                if events:
                    df = pd.DataFrame(events)
                    st.dataframe(df)
                else:
                    st.write("No analysis events yet.")
            else:
                st.error("Could not load admin stats.")
                st.write(response.text)

        except Exception as e:
            st.error("Failed to load admin stats.")
            st.write(str(e))


def render_app():
    with st.sidebar:
        st.write(f"Logged in as: {st.session_state.user_email}")

        if st.button("Logout"):
            logout()
            st.rerun()

        st.divider()

        st.header("Privacy Notice")
        st.write(
            "We store your email and basic analysis stats. "
            "We do not store your resume text in this MVP."
        )

    resume_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )

    job_description = st.text_area(
        "Paste Job Description",
        height=300,
        placeholder="Paste the full job description here..."
    )

    location = st.text_input(
        "Preferred Job Location",
        placeholder="Example: Krakow, Poland / Remote / London / Hyderabad"
    )

    analyze_button = st.button("Analyze Resume", type="primary")

    if analyze_button:
        if resume_file is None:
            st.error("Please upload your resume PDF.")

        elif not job_description.strip():
            st.error("Please paste a job description.")

        else:
            with st.spinner("Analyzing your resume..."):
                files = {
                    "resume": (
                        resume_file.name,
                        resume_file.getvalue(),
                        "application/pdf"
                    )
                }

                data = {
                    "job_description": job_description,
                    "location": location
                }

                try:
                    response = requests.post(
                        API_URL,
                        files=files,
                        data=data,
                        headers=auth_headers(),
                        timeout=180
                    )

                    if response.status_code != 200:
                        st.error("Backend returned an error.")
                        st.write(response.text)
                        return

                    result = response.json()

                    match_result = result.get("match_result", {})
                    feedback = result.get("feedback", "")
                    optimized = result.get("optimized_resume", {})

                    st.success("Analysis completed!")

                    try:
                        report_response = requests.post(
                            REPORT_API_URL,
                            json=result,
                            headers=auth_headers(),
                            timeout=120
                        )

                        if report_response.status_code == 200:
                            st.download_button(
                                label="Download Resume Analysis Report",
                                data=report_response.content,
                                file_name="resume_analysis_report.pdf",
                                mime="application/pdf"
                            )
                        else:
                            st.warning("Report generation failed.")

                    except Exception:
                        st.warning("Could not generate PDF report.")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Overall Match",
                            f"{match_result.get('match_percentage', 0)}%"
                        )

                    with col2:
                        st.metric(
                            "ATS Keyword Score",
                            f"{match_result.get('ats_keyword_score', 0)}%"
                        )

                    with col3:
                        st.metric(
                            "Semantic Fit Score",
                            f"{match_result.get('semantic_fit_score', 0)}%"
                        )

                    tab1, tab2, tab3, tab4, tab5, tab6,tab7 = st.tabs(
                        [
                            "Summary",
                            "Matched Skills",
                            "Missing Skills",
                            "RAG Evidence",
                            "AI Feedback",
                            "Optimized Resume",
                            "Raw JSON"
                        ]
                    )

                    with tab1:
                        st.subheader("Target Role")
                        st.write(match_result.get("target_role", "Not detected"))

                        st.subheader("Resume Summary")
                        st.write(match_result.get("resume_summary", ""))

                        st.subheader("Job Summary")
                        st.write(match_result.get("job_summary", ""))

                        st.subheader("Strengths")
                        for item in match_result.get("strengths", []):
                            st.write(f"✅ {item}")

                        st.subheader("Improvement Areas")
                        for item in match_result.get("improvement_areas", []):
                            st.write(f"⚠️ {item}")

                    with tab2:
                        st.subheader("Matched Skills")

                        matched_skills = match_result.get("matched_skills", [])

                        if matched_skills:
                            for skill in matched_skills:
                                st.markdown(
                                    f"""
**Job Skill:** {skill.get("job_skill", "")}  
**Resume Skill:** {skill.get("resume_skill", "")}  
**Match Type:** {skill.get("match_type", "")}  
**Explanation:** {skill.get("explanation", "")}
"""
                                )
                                st.divider()
                        else:
                            st.write("No matched skills found.")

                    with tab3:
                        st.subheader("Missing Skills")

                        missing_skills = match_result.get("missing_skills", [])

                        if missing_skills:
                            for skill in missing_skills:
                                st.markdown(
                                    f"""
**Skill:** {skill.get("skill", "")}  
**Category:** {skill.get("category", "")}  
**Importance:** {skill.get("importance", "")}  
**Why it matters:** {skill.get("why_it_matters", "")}  
**Resume edit suggestion:** {skill.get("resume_edit_suggestion", "")}
"""
                                )
                                st.divider()
                        else:
                            st.write("No major missing skills found.")
                    with tab4:
                        st.subheader("RAG Evidence")

                        st.write(
                            "These are the resume sections that are semantically closest to the job description."
                        )

                        st.metric(
                            "Vector Semantic Score",
                            f"{match_result.get('vector_semantic_score', 0)}%"
                        )

                        rag_evidence = match_result.get("rag_evidence", [])

                        if rag_evidence:
                            for item in rag_evidence:
                                st.markdown(
                                    f"""
**Similarity Score:** {item.get("similarity_score", "")}

**Job Requirement:**
{item.get("job_requirement", "")}

**Matching Resume Evidence:**
{item.get("matching_resume_evidence", "")}
"""
                                )
                                st.divider()
                        else:
                            st.write("No RAG evidence found.")
                    with tab5:
                        st.subheader("AI Resume Feedback")
                        st.markdown(feedback)

                    with tab6:
                        st.subheader("Optimized Resume Strategy")

                        st.caption(
                            optimized.get(
                                "company_data_note",
                                "Company suggestions are AI-generated strategic recommendations."
                            )
                        )

                        st.markdown("### Resume Headline")
                        st.write(
                            optimized.get(
                                "optimized_resume_headline",
                                "No headline generated."
                            )
                        )

                        st.markdown("### Professional Summary")
                        st.write(
                            optimized.get(
                                "optimized_professional_summary",
                                "No summary generated."
                            )
                        )

                        st.markdown("### Optimized Skills Section")
                        for skill in optimized.get("optimized_skills_section", []):
                            st.write(f"✅ {skill}")

                        st.markdown("### Optimized Experience Bullets")
                        for bullet in optimized.get("optimized_experience_bullets", []):
                            st.write(f"- {bullet}")

                        st.markdown("### Optimized Project Bullets")
                        for bullet in optimized.get("optimized_project_bullets", []):
                            st.write(f"- {bullet}")

                        st.markdown("### ATS Keywords to Include")
                        for keyword in optimized.get("ats_keywords_to_include", []):
                            st.write(f"🔑 {keyword}")

                        st.markdown("### Recommended Companies")
                        for company in optimized.get("recommended_companies", []):
                            st.markdown(
                                f"""
**{company.get("company_name", "")}**  

**Why suitable:** {company.get("why_suitable", "")}  

**Role fit:** {company.get("role_fit_reason", "")}  

**Search keywords:** {", ".join(company.get("search_keywords", []))}
"""
                            )
                            st.divider()

                        st.markdown("### Similar Roles to Apply")
                        for role in optimized.get("similar_roles_to_apply", []):
                            st.markdown(
                                f"""
**{role.get("role_title", "")}**  

**Why it matches:** {role.get("why_it_matches", "")}  

**Skills to improve:** {", ".join(role.get("skills_to_improve", []))}
"""
                            )
                            st.divider()

                        st.markdown("### LinkedIn Search Keywords")
                        st.write(
                            ", ".join(
                                optimized.get("linkedin_search_keywords", [])
                            )
                        )

                        st.markdown("### Final Resume Strategy")
                        st.write(
                            optimized.get(
                                "final_resume_strategy",
                                "No final strategy generated."
                            )
                        )

                    with tab7:
                        st.subheader("Full API Response")
                        st.json(result)

                except requests.exceptions.ConnectionError:
                    st.error(
                        "Could not connect to backend. Make sure FastAPI is running on port 8000."
                    )

                except requests.exceptions.Timeout:
                    st.error(
                        "The request took too long. Try with a shorter resume or job description."
                    )

                except Exception as e:
                    st.error("Something went wrong.")
                    st.write(str(e))

    render_admin_dashboard()


init_session()
render_header()

if st.session_state.access_token is None:
    render_login()
else:
    render_app()