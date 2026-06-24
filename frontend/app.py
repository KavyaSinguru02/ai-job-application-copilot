import streamlit as st
import requests


API_URL = "http://127.0.0.1:8000/analyze"
REPORT_API_URL = "http://127.0.0.1:8000/generate-report"


st.set_page_config(
    page_title="AI Job Application Copilot",
    page_icon="💼",
    layout="wide"
)


st.title("💼 AI Job Application Copilot")
st.write(
    "Upload your resume and paste a job description to get match percentage, "
    "missing skills, resume suggestions, interview questions, and a learning roadmap."
)


with st.sidebar:
    st.header("How it works")
    st.write("1. Upload resume PDF")
    st.write("2. Paste job description")
    st.write("3. Click Analyze")
    st.write("4. Review match score and suggestions")

    st.divider()

    st.subheader("Future Features")
    st.write("- ATS score")
    st.write("- Embeddings matching")
    st.write("- LangGraph agents")
    st.write("- MCP tools")
    st.write("- Resume rewrite export")


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
        with st.spinner("Analyzing resume against job description..."):
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
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()

                    match_result = result.get("match_result", {})
                    feedback = result.get("feedback", "")

                    st.success("Analysis completed!")
                    try:
                        report_response = requests.post(
                            REPORT_API_URL,
                            json=result,
                            timeout=120,
                        )

                        if report_response.status_code == 200:
                            st.download_button(
                                label="Download Resume Analysis Report",
                                data=report_response.content,
                                file_name="resume_analysis_report.pdf",
                                mime="application/pdf",
                            )
                        else:
                            st.warning("Report generation failed.")

                    except Exception:
                        st.warning("Could not generate PDF report.")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Overall Match",
                            f"{match_result.get('match_percentage', 0)}%",
                        )

                    with col2:
                        st.metric(
                            "ATS Keyword Score",
                            f"{match_result.get('ats_keyword_score', 0)}%",
                        )

                    with col3:
                        st.metric(
                            "Semantic Fit Score",
                            f"{match_result.get('semantic_fit_score', 0)}%",
                        )

                    st.divider()

                    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
                        [
                            "Summary",
                            "Matched Skills",
                            "Missing Skills",
                            "AI Feedback",
                            "Optimized Resume",
                            "Raw JSON",
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
                        strengths = match_result.get("strengths", [])
                        if strengths:
                            for item in strengths:
                                st.write(f"✅ {item}")
                        else:
                            st.write("No strengths detected.")

                        st.subheader("Improvement Areas")
                        improvement_areas = match_result.get("improvement_areas", [])
                        if improvement_areas:
                            for item in improvement_areas:
                                st.write(f"⚠️ {item}")
                        else:
                            st.write("No improvement areas detected.")

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
                        st.subheader("AI Resume Feedback")
                        st.markdown(feedback)

                    with tab5:
                        st.subheader("Optimized Resume Strategy")

                        optimized = result.get("optimized_resume", {})

                        st.markdown("### Resume Headline")
                        st.write(optimized.get("optimized_resume_headline", ""))

                        st.markdown("### Professional Summary")
                        st.write(optimized.get("optimized_professional_summary", ""))

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

                        st.markdown("### Do NOT Add Unless You Truly Have Experience")
                        for keyword in optimized.get("keywords_not_to_add_without_real_experience", []):
                            st.write(f"⚠️ {keyword}")

                        st.markdown("### Target Company Types")
                        for company_type in optimized.get("target_company_types", []):
                            st.write(f"🏢 {company_type}")

                        st.markdown("### Recommended Companies")
                        st.caption(optimized.get("company_data_note", ""))

                        live_top_companies = optimized.get("live_top_companies", [])
                        recommended_companies = optimized.get("recommended_companies", [])

                        if live_top_companies:
                            st.markdown("#### Live Top Companies")
                            for company in live_top_companies:
                                st.write(
                                    f"🏢 {company.get('company_name')} — "
                                    f"{company.get('vacancy_count')} vacancies"
                                )

                        if recommended_companies:
                            st.markdown("#### AI Recommended Companies")
                            for company in recommended_companies:
                                st.markdown(
                                    f"""
                                    **{company.get("company_name", "")}**  
                                    Why suitable: {company.get("why_suitable", "")}  
                                    Role fit: {company.get("role_fit_reason", "")}  
                                    Search keywords: {", ".join(company.get("search_keywords", []))}
                                    """
                                )
                                st.divider()

                        st.markdown("### Similar Roles to Apply")
                        for role in optimized.get("similar_roles_to_apply", []):
                            st.markdown(
                                f"""
                                **{role.get("role_title", "")}**  
                                Why it matches: {role.get("why_it_matches", "")}  
                                Skills to improve: {", ".join(role.get("missing_skills_to_improve", []))}
                                """
                            )

                        st.markdown("### Job Search Keywords")
                        st.write("LinkedIn:")
                        st.write(", ".join(optimized.get("linkedin_search_keywords", [])))

                        st.write("Naukri:")
                        st.write(", ".join(optimized.get("naukri_search_keywords", [])))

                        st.write("Indeed:")
                        st.write(", ".join(optimized.get("indeed_search_keywords", [])))

                        st.markdown("### Final Resume Strategy")
                        st.write(optimized.get("final_resume_strategy", ""))

                    with tab6:
                        st.subheader("Full API Response")
                        st.json(result)

                else:
                    st.error("Backend returned an error.")
                    st.write(response.text)

            except requests.exceptions.ConnectionError:
                st.error(
                    "Could not connect to backend. Make sure FastAPI is running on port 8000."
                )

            except requests.exceptions.Timeout:
                st.error(
                    "The request took too long. Try again with a shorter resume or job description."
                )

            except Exception as e:
                st.error("Something went wrong.")
                st.write(str(e))