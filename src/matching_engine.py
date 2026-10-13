
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills


def match_resume_to_job(resume_text, job_description):
    """Compare resume text and detected skills with a job description."""

    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")

    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description cannot be empty.")

    documents = [resume_text, job_description]

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)

    similarity = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    resume_skills = set(extract_skills(resume_text))
    job_skills = set(extract_skills(job_description))

    matched_skills = sorted(resume_skills & job_skills)
    missing_skills = sorted(job_skills - resume_skills)

    # Coverage is based only on skills detected by our predefined dictionary.
    skill_coverage = (
        len(matched_skills) / len(job_skills) * 100
        if job_skills else 0.0
    )

    return {
        "similarity_percentage": round(similarity * 100, 2),
        "skill_coverage_percentage": round(skill_coverage, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "job_skills_detected": sorted(job_skills),
    }
