"""
jd_analyzer.py
--------------
Analyse a job description to extract structured requirements.

Technique: Rule-based parsing + existing skill_extractor dictionary.

The module distinguishes between *required* and *preferred* (nice-to-have)
skills based on contextual keywords in the job description text.

Functions
---------
analyze_job_description(text)
    Return a structured dict of JD requirements.
"""

import re
from skill_extractor import extract_skills

# -----------------------------------------------------------------------
# Context keywords that signal "preferred / nice-to-have"
# -----------------------------------------------------------------------
_PREFERRED_SIGNALS = re.compile(
    r"\b("
    r"nice\s+to\s+have|preferred|bonus|desirable|ideally|"
    r"good\s+to\s+have|plus|optional|advantageous|"
    r"not\s+required\s+but|familiarity\s+with|"
    r"exposure\s+to|awareness\s+of|"
    r"added\s+advantage|additional\s+skills?"
    r")\b",
    re.IGNORECASE,
)

# Keywords that signal "required / must-have"
_REQUIRED_SIGNALS = re.compile(
    r"\b("
    r"required|must\s+have|mandatory|essential|"
    r"minimum\s+requirements?|key\s+requirements?|"
    r"qualifications?\s+required|"
    r"you\s+(?:should|must|will\s+need)|"
    r"we\s+(?:require|need|expect)|"
    r"strong\s+(?:knowledge|experience|understanding|skills?)"
    r")\b",
    re.IGNORECASE,
)


def _classify_paragraph(paragraph):
    """Classify a paragraph as 'required' or 'preferred'.

    Returns 'preferred' if preferred-signal keywords dominate, otherwise
    'required' (the default assumption for job descriptions).
    """
    pref_count = len(_PREFERRED_SIGNALS.findall(paragraph))
    req_count = len(_REQUIRED_SIGNALS.findall(paragraph))

    if pref_count > req_count:
        return "preferred"
    return "required"


def _split_into_paragraphs(text):
    """Split JD text into logical paragraphs / sections."""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in paragraphs if p.strip()]


def analyze_job_description(text):
    """Parse a job description into structured requirements.

    Parameters
    ----------
    text : str
        Raw job description text.

    Returns
    -------
    dict
        Keys:
        - ``required_skills``  : list[str]  — skills the JD requires.
        - ``preferred_skills`` : list[str]  — nice-to-have skills.
        - ``all_skills``       : list[str]  — union of required + preferred.
        - ``responsibilities`` : list[str]  — key responsibility phrases.
        - ``education_keywords``: list[str] — education-related terms found.
        - ``experience_keywords``: list[str]— experience-related terms found.
        - ``raw_text``         : str        — the original JD text.
    """
    if not text or not text.strip():
        return {
            "required_skills": [],
            "preferred_skills": [],
            "all_skills": [],
            "responsibilities": [],
            "education_keywords": [],
            "experience_keywords": [],
            "raw_text": "",
        }

    all_skills = extract_skills(text)
    paragraphs = _split_into_paragraphs(text)

    required_skills = set()
    preferred_skills = set()

    # Required and preferred lists are often adjacent without a blank line,
    # so keep category state while walking the description line by line.
    classification = "required"
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        preferred_signals = len(_PREFERRED_SIGNALS.findall(stripped))
        required_signals = len(_REQUIRED_SIGNALS.findall(stripped))
        if preferred_signals > required_signals:
            classification = "preferred"
        elif required_signals > preferred_signals:
            classification = "required"

        line_skills = set(extract_skills(stripped))
        if classification == "preferred":
            preferred_skills.update(line_skills)
        else:
            required_skills.update(line_skills)

    # Preserve paragraph parsing for a single-line prose JD.
    for para in paragraphs:
        para_skills = set(extract_skills(para))
        unassigned = para_skills - required_skills - preferred_skills
        if _classify_paragraph(para) == "preferred":
            preferred_skills.update(unassigned)
        else:
            required_skills.update(unassigned)

    # Skills found in both required and preferred default to required.
    overlap = required_skills & preferred_skills
    preferred_skills -= overlap

    # Skills not in any paragraph context default to required.
    unclassified = set(all_skills) - required_skills - preferred_skills
    required_skills.update(unclassified)

    # Extract responsibilities (lines that look like bullet items).
    responsibilities = []
    for line in text.split("\n"):
        stripped = line.strip()
        # Bullet or numbered list items.
        if re.match(r"^[\-•●►▸]\s+.{10,}", stripped) or \
           re.match(r"^\d+[\.\)]\s+.{10,}", stripped):
            cleaned = re.sub(r"^[\-•●►▸\d\.\)]\s*", "", stripped).strip()
            responsibilities.append(cleaned)

    # Extract education keywords.
    education_keywords = _extract_education_keywords(text)

    # Extract experience keywords.
    experience_keywords = _extract_experience_keywords(text)

    return {
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
        "all_skills": sorted(set(all_skills)),
        "responsibilities": responsibilities,
        "education_keywords": education_keywords,
        "experience_keywords": experience_keywords,
        "raw_text": text,
    }


def _extract_education_keywords(text):
    """Find education-related requirements in the JD."""
    keywords = []
    education_patterns = [
        r"(?:B\.?Tech|B\.?E\.?|B\.?Sc|B\.?S\.?|Bachelor(?:'?s)?)\s*"
        r"(?:in\s+[\w\s&,]+)?",
        r"(?:M\.?Tech|M\.?E\.?|M\.?Sc|M\.?S\.?|Master(?:'?s)?)\s*"
        r"(?:in\s+[\w\s&,]+)?",
        r"(?:Ph\.?D|Doctorate)",
        r"(?:Computer\s+Science|Information\s+Technology|"
        r"Software\s+Engineering|Data\s+Science|"
        r"Electrical\s+Engineering|Electronics)",
    ]

    for pattern in education_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend([m.strip() for m in matches if m.strip()])

    return list(set(keywords))


def _extract_experience_keywords(text):
    """Find experience-level requirements in the JD."""
    keywords = []
    patterns = [
        r"(\d+\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp))",
        r"(entry[\s-]?level|mid[\s-]?level|senior|junior|"
        r"fresher|experienced|lead)",
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        keywords.extend([m.strip() for m in matches if m.strip()])

    return list(set(keywords))
