def calculate_match_score(resume_text, job_description):
    resume_words = set(resume_text.lower().split())
    jd_words = set(job_description.lower().split())

    common_words = resume_words.intersection(jd_words)

    if len(jd_words) == 0:
        score = 0
    else:
        score = round((len(common_words) / len(jd_words)) * 100, 2)

    missing_words = list(jd_words - resume_words)

    return {
        "match_percentage": score,
        "matched_keywords": list(common_words)[:30],
        "missing_keywords": missing_words[:30]
    }