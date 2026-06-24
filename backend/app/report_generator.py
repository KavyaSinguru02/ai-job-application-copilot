from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def safe_text(value):
    if value is None:
        return ""
    return str(value)


def add_section_title(story, styles, title):
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
    story.append(Spacer(1, 6))


def add_bullet_list(story, styles, items):
    if not items:
        story.append(Paragraph("No data available.", styles["Normal"]))
        return

    for item in items:
        story.append(Paragraph(f"• {safe_text(item)}", styles["Normal"]))


def generate_pdf_report(result: dict) -> bytes:
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    story = []

    match_result = result.get("match_result", {})
    optimized = result.get("optimized_resume", {})
    feedback = result.get("feedback", "")

    story.append(
        Paragraph(
            "<b>AI Job Application Copilot Report</b>",
            styles["Title"]
        )
    )

    story.append(Spacer(1, 12))

    target_role = match_result.get("target_role", "Not detected")

    story.append(
        Paragraph(
            f"<b>Target Role:</b> {safe_text(target_role)}",
            styles["Normal"]
        )
    )

    story.append(Spacer(1, 12))

    score_data = [
        ["Metric", "Score"],
        ["Overall Match", f"{match_result.get('match_percentage', 0)}%"],
        ["ATS Keyword Score", f"{match_result.get('ats_keyword_score', 0)}%"],
        ["Semantic Fit Score", f"{match_result.get('semantic_fit_score', 0)}%"]
    ]

    score_table = Table(score_data, colWidths=[220, 180])

    score_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("PADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    story.append(score_table)

    add_section_title(story, styles, "Resume Summary")
    story.append(
        Paragraph(
            safe_text(match_result.get("resume_summary", "")),
            styles["Normal"]
        )
    )

    add_section_title(story, styles, "Job Summary")
    story.append(
        Paragraph(
            safe_text(match_result.get("job_summary", "")),
            styles["Normal"]
        )
    )

    add_section_title(story, styles, "Strengths")
    add_bullet_list(
        story,
        styles,
        match_result.get("strengths", [])
    )

    add_section_title(story, styles, "Improvement Areas")
    add_bullet_list(
        story,
        styles,
        match_result.get("improvement_areas", [])
    )

    add_section_title(story, styles, "Missing Skills")

    missing_skills = match_result.get("missing_skills", [])

    if missing_skills:
        for skill in missing_skills:
            skill_name = skill.get("skill", "")
            category = skill.get("category", "")
            importance = skill.get("importance", "")
            why = skill.get("why_it_matterss", skill.get("why_it_matters", ""))

            story.append(
                Paragraph(
                    f"• <b>{safe_text(skill_name)}</b> "
                    f"({safe_text(category)}, {safe_text(importance)}) - "
                    f"{safe_text(why)}",
                    styles["Normal"]
                )
            )
    else:
        story.append(Paragraph("No major missing skills found.", styles["Normal"]))

    add_section_title(story, styles, "Optimized Resume Headline")
    story.append(
        Paragraph(
            safe_text(optimized.get("optimized_resume_headline", "")),
            styles["Normal"]
        )
    )

    add_section_title(story, styles, "Optimized Professional Summary")
    story.append(
        Paragraph(
            safe_text(optimized.get("optimized_professional_summary", "")),
            styles["Normal"]
        )
    )

    add_section_title(story, styles, "Optimized Skills Section")
    add_bullet_list(
        story,
        styles,
        optimized.get("optimized_skills_section", [])
    )

    add_section_title(story, styles, "Optimized Experience Bullets")
    add_bullet_list(
        story,
        styles,
        optimized.get("optimized_experience_bullets", [])
    )

    add_section_title(story, styles, "Optimized Project Bullets")
    add_bullet_list(
        story,
        styles,
        optimized.get("optimized_project_bullets", [])
    )

    add_section_title(story, styles, "ATS Keywords to Include")
    add_bullet_list(
        story,
        styles,
        optimized.get("ats_keywords_to_include", [])
    )

    add_section_title(story, styles, "Recommended Companies")

    recommended_companies = optimized.get("recommended_companies", [])

    if recommended_companies:
        for company in recommended_companies:
            story.append(
                Paragraph(
                    f"• <b>{safe_text(company.get('company_name', ''))}</b>: "
                    f"{safe_text(company.get('why_suitable', ''))}",
                    styles["Normal"]
                )
            )
    else:
        story.append(Paragraph("No company recommendations generated.", styles["Normal"]))

    add_section_title(story, styles, "Similar Roles to Apply")

    similar_roles = optimized.get("similar_roles_to_apply", [])

    if similar_roles:
        for role in similar_roles:
            story.append(
                Paragraph(
                    f"• <b>{safe_text(role.get('role_title', ''))}</b>: "
                    f"{safe_text(role.get('why_it_matches', ''))}",
                    styles["Normal"]
                )
            )
    else:
        story.append(Paragraph("No similar roles generated.", styles["Normal"]))

    add_section_title(story, styles, "LinkedIn Search Keywords")
    linkedin_keywords = optimized.get("linkedin_search_keywords", [])
    story.append(
        Paragraph(
            ", ".join(linkedin_keywords) if linkedin_keywords else "No keywords generated.",
            styles["Normal"]
        )
    )

    add_section_title(story, styles, "Final Resume Strategy")
    story.append(
        Paragraph(
            safe_text(optimized.get("final_resume_strategy", "")),
            styles["Normal"]
        )
    )

    add_section_title(story, styles, "AI Feedback")
    story.append(
        Paragraph(
            safe_text(feedback).replace("\n", "<br/>"),
            styles["Normal"]
        )
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    return pdf