"""
section_scorer.py
-----------------
Score individual resume sections against a job description.

Techniques used per section:
- Skills:          Dictionary match (rule-based) via skill_extractor
- Projects:        TF-IDF cosine similarity + technology overlap
- Experience:      TF-IDF cosine similarity + skill/role overlap
- Certifications:  Keyword relevance match (rule-based)
- Education:       Keyword match (rule-based)
- Achievements:    TF-IDF cosine similarity (when relevant)

Each scorer returns a dict with:
    score        : float (0–100)
    matched      : list[str]  — evidence of what matched
    missing      : list[str]  — what the JD wanted but wasn't found
    method       : str        — technique used
    details      : dict       — extra info (varies per section)
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skill_extractor import extract_skills
from section_extractors import (
    extract_experiences,
    extract_projects,
    extract_certifications,
    extract_education,
)


def _tfidf_similarity(text_a, text_b):
    """Compute TF-IDF cosine similarity between two text strings.

    Returns a float in [0, 1].  Returns 0 if either input is empty.
    """
    if not text_a or not text_a.strip() or not text_b or not text_b.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform([text_a, text_b])
        sim = cosine_similarity(matrix[0:1], matrix[1:2])[0][0]
        return float(sim)
    except ValueError:
        return 0.0


def _evidence_snippets(text, keywords, context_chars=80):
    """Extract short evidence snippets around matched keywords.

    Returns a list of strings showing where each keyword appears in the text.
    """
    snippets = []
    text_lower = text.lower()

    for kw in keywords:
        idx = text_lower.find(kw.lower())
        if idx >= 0:
            start = max(0, idx - context_chars)
            end = min(len(text), idx + len(kw) + context_chars)
            snippet = text[start:end].strip()
            if start > 0:
                snippet = "…" + snippet
            if end < len(text):
                snippet = snippet + "…"
            snippets.append(snippet)

    return snippets


# -----------------------------------------------------------------------
# Skills Scorer
# -----------------------------------------------------------------------

def score_skills(resume_skills_text, jd_analysis):
    """Score the skills section.

    Method: Dictionary matching (rule-based).

    Formula:
        score = (matched_required × 1.0 + matched_preferred × 0.5)
                / (total_required + total_preferred × 0.5) × 100

    Parameters
    ----------
    resume_skills_text : str
        Text of the skills section from the resume.
    jd_analysis : dict
        Output of jd_analyzer.analyze_job_description().

    Returns
    -------
    dict
    """
    required = set(jd_analysis.get("required_skills", []))
    preferred = set(jd_analysis.get("preferred_skills", []))
    resume_skills = set(extract_skills(resume_skills_text))

    matched_required = sorted(resume_skills & required)
    matched_preferred = sorted(resume_skills & preferred)
    missing_required = sorted(required - resume_skills)
    missing_preferred = sorted(preferred - resume_skills)

    numerator = len(matched_required) * 1.0 + len(matched_preferred) * 0.5
    denominator = len(required) * 1.0 + len(preferred) * 0.5

    score = (numerator / denominator * 100) if denominator > 0 else 0.0
    score = min(score, 100.0)

    return {
        "score": round(score, 2),
        "matched": matched_required + matched_preferred,
        "missing": missing_required + missing_preferred,
        "method": "Dictionary matching (rule-based)",
        "details": {
            "matched_required": matched_required,
            "matched_preferred": matched_preferred,
            "missing_required": missing_required,
            "missing_preferred": missing_preferred,
            "resume_skills": sorted(resume_skills),
        },
    }


# -----------------------------------------------------------------------
# Projects Scorer
# -----------------------------------------------------------------------

def score_projects(projects_text, jd_analysis, excluded_skills=None):
    """Score the projects section.

    Method: TF-IDF cosine similarity (60%) + technology overlap (40%).

    Parameters
    ----------
    projects_text : str
        Text of the projects section from the resume.
    jd_analysis : dict
        Output of jd_analyzer.analyze_job_description().

    Returns
    -------
    dict
    """
    jd_text = jd_analysis.get("raw_text", "")
    jd_skills = set(jd_analysis.get("all_skills", []))

    if not projects_text or not projects_text.strip():
        return {
            "score": 0.0,
            "matched": [],
            "missing": sorted(jd_skills),
            "method": "TF-IDF cosine similarity + technology overlap",
            "details": {"projects": [], "similarity": 0.0, "tech_overlap": 0.0},
        }

    # TF-IDF similarity between project text and JD.
    similarity = _tfidf_similarity(projects_text, jd_text)

    # Technology overlap.
    project_skills = set(extract_skills(projects_text))
    available_skills = project_skills - set(excluded_skills or [])
    tech_matched = sorted(available_skills & jd_skills)
    tech_overlap = (
        len(tech_matched) / len(jd_skills) * 100 if jd_skills else 0.0
    )

    # Combined score: 60% similarity + 40% tech overlap.
    score = 0.6 * (similarity * 100) + 0.4 * tech_overlap
    score = min(score, 100.0)

    projects = extract_projects(projects_text)
    evidence = _evidence_snippets(projects_text, tech_matched)

    return {
        "score": round(score, 2),
        "matched": tech_matched,
        "missing": sorted(jd_skills - project_skills),
        "method": "TF-IDF cosine similarity + technology overlap",
        "details": {
            "projects": projects,
            "similarity": round(similarity * 100, 2),
            "tech_overlap": round(tech_overlap, 2),
            "evidence": evidence,
        },
    }


# -----------------------------------------------------------------------
# Experience / Internship Scorer
# -----------------------------------------------------------------------

def score_experience(experience_text, jd_analysis, excluded_skills=None):
    """Score the experience/internship section.

    Method: TF-IDF cosine similarity (60%) + skill overlap (40%).

    Parameters
    ----------
    experience_text : str
        Text of the experience section from the resume.
    jd_analysis : dict
        Output of jd_analyzer.analyze_job_description().

    Returns
    -------
    dict
    """
    jd_text = jd_analysis.get("raw_text", "")
    jd_skills = set(jd_analysis.get("all_skills", []))

    if not experience_text or not experience_text.strip():
        return {
            "score": 0.0,
            "matched": [],
            "missing": sorted(jd_skills),
            "method": "TF-IDF cosine similarity + skill overlap",
            "details": {
                "experiences": [],
                "similarity": 0.0,
                "skill_overlap": 0.0,
            },
        }

    similarity = _tfidf_similarity(experience_text, jd_text)

    exp_skills = set(extract_skills(experience_text))
    available_skills = exp_skills - set(excluded_skills or [])
    skill_matched = sorted(available_skills & jd_skills)
    skill_overlap = (
        len(skill_matched) / len(jd_skills) * 100 if jd_skills else 0.0
    )

    score = 0.6 * (similarity * 100) + 0.4 * skill_overlap
    score = min(score, 100.0)

    experiences = extract_experiences(experience_text)
    evidence = _evidence_snippets(experience_text, skill_matched)

    return {
        "score": round(score, 2),
        "matched": skill_matched,
        "missing": sorted(jd_skills - exp_skills),
        "method": "TF-IDF cosine similarity + skill overlap",
        "details": {
            "experiences": experiences,
            "similarity": round(similarity * 100, 2),
            "skill_overlap": round(skill_overlap, 2),
            "evidence": evidence,
        },
    }


# -----------------------------------------------------------------------
# Certifications Scorer
# -----------------------------------------------------------------------

def score_certifications(certs_text, jd_analysis, excluded_skills=None):
    """Score the certifications section.

    Method: Keyword relevance matching (rule-based).

    NOTE: A certification does not prove practical competence.  This scorer
    only measures topic relevance to the JD.

    Parameters
    ----------
    certs_text : str
        Text of the certifications section from the resume.
    jd_analysis : dict
        Output of jd_analyzer.analyze_job_description().

    Returns
    -------
    dict
    """
    jd_skills = set(jd_analysis.get("all_skills", []))

    if not certs_text or not certs_text.strip():
        return {
            "score": 0.0,
            "matched": [],
            "missing": [],
            "method": "Keyword relevance matching (rule-based). "
                      "Certification ≠ practical competence.",
            "details": {"certifications": [], "relevant_count": 0},
        }

    certs = extract_certifications(certs_text)
    cert_skills = set(extract_skills(certs_text))
    relevant_skills = sorted((cert_skills - set(excluded_skills or [])) & jd_skills)

    # Score based on how many JD-relevant topics are covered.
    relevant_count = len(relevant_skills)
    expected = max(1, len(jd_skills))
    score = min(relevant_count / expected * 100, 100.0)

    return {
        "score": round(score, 2),
        "matched": relevant_skills,
        "missing": [],  # We don't penalise missing certs.
        "method": "Keyword relevance matching (rule-based). "
                  "Certification ≠ practical competence.",
        "details": {
            "certifications": certs,
            "relevant_count": relevant_count,
        },
    }


# -----------------------------------------------------------------------
# Education Scorer
# -----------------------------------------------------------------------

def score_education(edu_text, jd_analysis, excluded_skills=None):
    """Score the education section.

    Method: Keyword matching (rule-based).
    Formula: 0.5 × degree_relevance + 0.5 × coursework_overlap_pct.

    Parameters
    ----------
    edu_text : str
        Text of the education section from the resume.
    jd_analysis : dict
        Output of jd_analyzer.analyze_job_description().

    Returns
    -------
    dict
    """
    jd_edu_keywords = jd_analysis.get("education_keywords", [])
    jd_skills = set(jd_analysis.get("all_skills", []))

    if not edu_text or not edu_text.strip():
        return {
            "score": 0.0,
            "matched": [],
            "missing": jd_edu_keywords,
            "method": "Keyword matching (rule-based)",
            "details": {
                "education": [],
                "degree_relevance": 0.0,
                "coursework_overlap": 0.0,
            },
        }

    edu_entries = extract_education(edu_text)
    edu_lower = edu_text.lower()

    # Degree relevance: do any JD education keywords appear in edu text?
    degree_matched = []
    for kw in jd_edu_keywords:
        if kw.lower() in edu_lower:
            degree_matched.append(kw)

    degree_relevance = (
        len(degree_matched) / len(jd_edu_keywords) * 100
        if jd_edu_keywords else 50.0  # Neutral if JD doesn't specify education.
    )

    # Coursework overlap: do skills from coursework match JD skills?
    coursework_skills = set()
    for entry in edu_entries:
        for cw in entry.get("coursework", []):
            coursework_skills.update(extract_skills(cw))
    # Also check the full education text for skill mentions.
    edu_skills = set(extract_skills(edu_text))
    coursework_skills.update(edu_skills)

    cw_matched = sorted((coursework_skills - set(excluded_skills or [])) & jd_skills)
    coursework_overlap = (
        len(cw_matched) / len(jd_skills) * 100 if jd_skills else 0.0
    )

    score = 0.5 * degree_relevance + 0.5 * coursework_overlap
    score = min(score, 100.0)

    return {
        "score": round(score, 2),
        "matched": degree_matched + cw_matched,
        "missing": [kw for kw in jd_edu_keywords if kw not in degree_matched],
        "method": "Keyword matching (rule-based)",
        "details": {
            "education": edu_entries,
            "degree_relevance": round(degree_relevance, 2),
            "coursework_overlap": round(coursework_overlap, 2),
        },
    }


# -----------------------------------------------------------------------
# Achievements Scorer
# -----------------------------------------------------------------------

def score_achievements(achievements_text, jd_analysis):
    """Score the achievements section.

    Method: TF-IDF cosine similarity (relevance check only).
    Achievements contribute only when they are topically relevant to the JD.

    Parameters
    ----------
    achievements_text : str
        Text of the achievements section from the resume.
    jd_analysis : dict
        Output of jd_analyzer.analyze_job_description().

    Returns
    -------
    dict
    """
    jd_text = jd_analysis.get("raw_text", "")

    if not achievements_text or not achievements_text.strip():
        return {
            "score": 0.0,
            "matched": [],
            "missing": [],
            "method": "TF-IDF cosine similarity (relevance check)",
            "details": {"similarity": 0.0},
        }

    similarity = _tfidf_similarity(achievements_text, jd_text)
    ach_skills = set(extract_skills(achievements_text))
    jd_skills = set(jd_analysis.get("all_skills", []))
    matched = sorted(ach_skills & jd_skills)

    score = similarity * 100
    score = min(score, 100.0)

    return {
        "score": round(score, 2),
        "matched": matched,
        "missing": [],
        "method": "TF-IDF cosine similarity (relevance check)",
        "details": {"similarity": round(similarity * 100, 2)},
    }
