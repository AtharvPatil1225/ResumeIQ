"""
section_parser.py
-----------------
Detect and segment resume text into canonical sections.

Technique: Rule-based regex heading detection.

The parser recognises common heading variations (ALL CAPS, Title Case,
with/without colons or dashes) and maps each to one of these canonical
section names:

    skills, experience, projects, certifications, education, achievements

Any text that appears before the first detected heading is assigned to
the ``"summary"`` section.

Usage
-----
>>> sections = parse_sections(resume_text)
>>> sections["skills"]
'Python, Java, SQL, React ...'
"""

import re
from collections import OrderedDict

# -----------------------------------------------------------------------
# Canonical section names
# -----------------------------------------------------------------------
SKILLS = "skills"
EXPERIENCE = "experience"
PROJECTS = "projects"
CERTIFICATIONS = "certifications"
EDUCATION = "education"
ACHIEVEMENTS = "achievements"
SUMMARY = "summary"

ALL_SECTIONS = [
    SKILLS, EXPERIENCE, PROJECTS, CERTIFICATIONS,
    EDUCATION, ACHIEVEMENTS,
]

# -----------------------------------------------------------------------
# Heading → canonical name mapping
# -----------------------------------------------------------------------
# Each tuple is (list-of-heading-keywords, canonical_name).
# Keywords are matched case-insensitively.  The longest match wins
# when multiple patterns could match the same line.
_HEADING_MAP = [
    # Skills
    (
        [
            "technical skills", "core competencies", "key skills",
            "skills & technologies", "skills and technologies",
            "skills & tools", "skills and tools", "technologies",
            "tech stack", "competencies", "proficiencies",
            "areas of expertise", "tools & technologies",
            "tools and technologies", "programming skills",
            "skills",
        ],
        SKILLS,
    ),
    # Experience / Internships
    (
        [
            "professional experience", "work experience",
            "internship experience", "internships & experience",
            "internships and experience", "industry experience",
            "employment history", "career history",
            "relevant experience", "internships",
            "internship", "experience", "work history",
        ],
        EXPERIENCE,
    ),
    # Projects
    (
        [
            "academic projects", "personal projects", "key projects",
            "academic & personal projects",
            "academic and personal projects",
            "notable projects", "selected projects",
            "side projects", "project work",
            "major projects", "mini projects",
            "projects",
        ],
        PROJECTS,
    ),
    # Certifications / Training
    (
        [
            "certifications & training", "certifications and training",
            "certificates & training", "certificates and training",
            "professional certifications", "professional training",
            "licenses & certifications", "licenses and certifications",
            "certifications", "certificates", "training",
            "courses & certifications", "courses and certifications",
            "online courses", "moocs",
        ],
        CERTIFICATIONS,
    ),
    # Education
    (
        [
            "education & relevant coursework",
            "education and relevant coursework",
            "academic background", "educational background",
            "academic qualifications", "educational qualifications",
            "relevant coursework", "coursework",
            "education",
        ],
        EDUCATION,
    ),
    # Achievements
    (
        [
            "honors & awards", "honors and awards",
            "awards & achievements", "awards and achievements",
            "key achievements", "accomplishments",
            "achievements", "awards", "honors",
            "extracurricular activities",
            "co-curricular activities",
        ],
        ACHIEVEMENTS,
    ),
]

# Pre-compile: sort keywords longest-first so greedy match works.
_SORTED_KEYWORDS = []
for keywords, canon in _HEADING_MAP:
    for kw in sorted(keywords, key=len, reverse=True):
        _SORTED_KEYWORDS.append((kw.lower(), canon))


def _is_heading_line(line):
    """Return the canonical section name if *line* looks like a heading.

    A line is considered a heading when:
    - After stripping punctuation/decoration it matches a known keyword.
    - It is relatively short (≤ 80 chars after stripping).
    - It is typically ALL CAPS, Title Case, or followed by a colon/dash.

    Returns
    -------
    str or None
        Canonical section name, or None if the line is not a heading.
    """
    stripped = line.strip()
    if not stripped or len(stripped) > 80:
        return None

    # Remove common decorators: dashes, underscores, colons, pipes,
    # equals signs, asterisks, hashes, bullets.
    cleaned = re.sub(r"^[\s\-_=*#|►▸•●:]+", "", stripped)
    cleaned = re.sub(r"[\s\-_=*#|►▸•●:]+$", "", cleaned)
    cleaned = cleaned.strip()

    if not cleaned:
        return None

    lower = cleaned.lower()

    for kw, canon in _SORTED_KEYWORDS:
        if lower == kw:
            return canon
        # Allow a trailing colon or dash that wasn't fully stripped.
        if lower in (f"{kw}:", f"{kw} -", f"{kw} –", f"{kw} —"):
            return canon

    return None


def parse_sections(text):
    """Split resume text into canonical sections.

    Parameters
    ----------
    text : str
        Full resume text (cleaned or raw).

    Returns
    -------
    OrderedDict[str, str]
        Mapping of canonical section names to their text content.
        Sections with no detected content are omitted.
        Text before the first heading is stored under ``"summary"``.
    """
    if not text or not text.strip():
        return OrderedDict()

    lines = text.split("\n")
    sections = OrderedDict()
    current_section = SUMMARY
    current_lines = []

    for line in lines:
        heading = _is_heading_line(line)
        if heading is not None:
            # Save previous section.
            content = "\n".join(current_lines).strip()
            if content:
                sections[current_section] = content
            current_section = heading
            current_lines = []
        else:
            current_lines.append(line)

    # Save the last section.
    content = "\n".join(current_lines).strip()
    if content:
        sections[current_section] = content

    return sections


def get_section_text(sections, canon_name):
    """Safely retrieve text for a canonical section.

    Returns an empty string if the section was not found.
    """
    return sections.get(canon_name, "")
