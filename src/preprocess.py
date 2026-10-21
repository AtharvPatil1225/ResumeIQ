"""
preprocess.py
-------------
Shared text preprocessing utilities for ResumeIQ.

Key design principle: technical terms such as C++, C#, .NET, Node.js,
SQL, and similar identifiers are preserved exactly. Standard NLP
approaches (e.g., aggressive punctuation stripping) destroy these tokens
and must be avoided.
"""

import re


_TECH_PATTERNS = [
    # Order matters — longer / more specific patterns go first.
    (r"C#", "C#"),
    (r"C\+\+", "C++"),
    (r"\.NET", ".NET"),
    (r"Node\.js", "Node.js"),
    (r"Vue\.js", "Vue.js"),
    (r"Next\.js", "Next.js"),
    (r"Nuxt\.js", "Nuxt.js"),
    (r"Express\.js", "Express.js"),
    (r"ASP\.NET", "ASP.NET"),
    (r"React Native", "React Native"),
    (r"Spring Boot", "Spring Boot"),
    (r"Ruby on Rails", "Ruby on Rails"),
    (r"Tailwind CSS", "Tailwind CSS"),
    (r"CI/CD", "CI/CD"),
    (r"REST API", "REST API"),
    (r"ELK Stack", "ELK Stack"),
    (r"Google Cloud", "Google Cloud"),
    (r"Apache Spark", "Apache Spark"),
    (r"GitHub Actions", "GitHub Actions"),
    (r"GitLab CI", "GitLab CI"),
    (r"SQL Server", "SQL Server"),
    (r"Power BI", "Power BI"),
    (r"Google Colab", "Google Colab"),
]


def _shield(text):
    """Replace technical tokens with safe placeholders."""
    for i, (pattern, _) in enumerate(_TECH_PATTERNS):
        placeholder = f"__TECH_SHIELD_{i:03d}__"
        text = re.sub(pattern, placeholder, text, flags=re.IGNORECASE)
    return text


def _unshield(text):
    """Restore placeholders to their canonical technical tokens."""
    for i, (_, canonical) in enumerate(_TECH_PATTERNS):
        placeholder = f"__TECH_SHIELD_{i:03d}__"
        text = text.replace(placeholder, canonical)
    return text


def clean_resume_text(text):
    """
    Lightly clean resume text for ML feature extraction.

    Operations performed (in order):
    1. Shield technical tokens.
    2. Collapse excessive whitespace and newlines.
    3. Remove non-printable / control characters.
    4. Restore shielded tokens.

    Parameters
    ----------
    text : str
        Raw extracted text from a resume PDF.

    Returns
    -------
    str
        Cleaned text.  Returns an empty string if input is None or empty.
    """
    if not text:
        return ""

    text = str(text)
    text = _shield(text)

    # Remove non-printable control characters (except common whitespace).
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\x80-\xFF]", " ", text)

    # Collapse multiple spaces/tabs into a single space.
    text = re.sub(r"[ \t]{2,}", " ", text)

    # Collapse more than two consecutive newlines into two.
    text = re.sub(r"\n{3,}", "\n\n", text)

    text = _unshield(text)
    return text.strip()


def clean_job_description(text):
    """
    Lightly clean a job description for ML feature extraction.

    Applies the same cleaning as clean_resume_text().

    Parameters
    ----------
    text : str
        Raw job description text pasted by the user.

    Returns
    -------
    str
        Cleaned text.
    """
    return clean_resume_text(text)
