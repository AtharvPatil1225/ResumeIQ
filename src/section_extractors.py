"""
section_extractors.py
---------------------
Extract structured details from individual resume sections.

Technique: Rule-based extraction using regex patterns.

Each extractor takes the raw text of a single section and returns a list
of dictionaries with the structured fields it could identify.  Missing
fields are set to empty strings — never fabricated.

Functions
---------
extract_experiences(text)
    Parse internship/work entries.
extract_projects(text)
    Parse project entries.
extract_certifications(text)
    Parse certification/training entries.
extract_education(text)
    Parse education entries.
"""

import re
from skill_extractor import extract_skills


# -----------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------

def _split_entries(text):
    """Split section text into individual entries.

    Heuristic: entries are separated by blank lines, or by lines that
    start with a bullet/number/dash/project-name pattern.
    """
    # First try splitting on blank lines.
    chunks = re.split(r"\n\s*\n", text.strip())
    if len(chunks) > 1:
        return [c.strip() for c in chunks if c.strip()]

    # Fallback: split on lines that start with bullet points or dashes.
    entries = []
    current = []
    for line in text.strip().split("\n"):
        stripped = line.strip()
        # New entry if line starts with bullet/dash/number
        if re.match(r"^[\-•●►▸]\s+[A-Z]", stripped) or \
           re.match(r"^\d+[\.\)]\s+", stripped):
            if current:
                entries.append("\n".join(current).strip())
            current = [line]
        else:
            current.append(line)
    if current:
        entries.append("\n".join(current).strip())

    return entries if entries else [text.strip()]


# -----------------------------------------------------------------------
# Experience / Internship Extractor
# -----------------------------------------------------------------------

# Common date/duration patterns.
_DATE_PATTERN = re.compile(
    r"("
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"[\s,]*\d{2,4}"
    r"\s*[-–—to]+\s*"
    r"(?:(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
    r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
    r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
    r"[\s,]*\d{2,4}|Present|Current|Ongoing)"
    r")",
    re.IGNORECASE,
)

_ROLE_KEYWORDS = re.compile(
    r"\b(intern|developer|engineer|analyst|designer|associate|"
    r"trainee|assistant|coordinator|consultant|manager|lead|"
    r"specialist|administrator|architect|scientist|researcher|"
    r"fellow|apprentice)\b",
    re.IGNORECASE,
)


def extract_experiences(text):
    """Extract internship/work experience entries.

    Returns
    -------
    list[dict]
        Each dict has keys: role, company, duration, responsibilities, skills.
    """
    if not text or not text.strip():
        return []

    entries = _split_entries(text)
    results = []

    for entry in entries:
        lines = [ln.strip() for ln in entry.split("\n") if ln.strip()]
        if not lines:
            continue

        role = ""
        company = ""
        duration = ""
        responsibilities = []

        # Try to find duration.
        dur_match = _DATE_PATTERN.search(entry)
        if dur_match:
            duration = dur_match.group(0).strip()

        # First line is often "Role at Company" or "Role — Company".
        first_line = lines[0]
        # Remove duration from first line for cleaner parsing.
        first_clean = _DATE_PATTERN.sub("", first_line).strip().rstrip("|–—-,")

        # Try "Role at/@ Company" pattern.
        at_match = re.match(
            r"^(.+?)\s+(?:at|@|[-–—|,])\s+(.+)$",
            first_clean,
            re.IGNORECASE,
        )
        if at_match:
            role = at_match.group(1).strip()
            company = at_match.group(2).strip()
        elif _ROLE_KEYWORDS.search(first_clean):
            role = first_clean
            # Check if second line is the company.
            if len(lines) > 1 and not _ROLE_KEYWORDS.search(lines[1]):
                potential_company = _DATE_PATTERN.sub("", lines[1]).strip()
                if potential_company and len(potential_company) < 80:
                    company = potential_company
                    lines = lines[:1] + lines[2:]
        else:
            # Treat the whole first line as a combined role/company.
            role = first_clean

        # Remaining lines are responsibilities.
        for ln in lines[1:]:
            cleaned = re.sub(r"^[\-•●►▸]\s*", "", ln).strip()
            cleaned = _DATE_PATTERN.sub("", cleaned).strip()
            if cleaned and len(cleaned) > 5:
                responsibilities.append(cleaned)

        skills = extract_skills(entry)

        results.append({
            "role": role,
            "company": company,
            "duration": duration,
            "responsibilities": responsibilities,
            "skills": skills,
        })

    return results


# -----------------------------------------------------------------------
# Project Extractor
# -----------------------------------------------------------------------

def extract_projects(text):
    """Extract project entries.

    Returns
    -------
    list[dict]
        Each dict has keys: name, description, technologies.
    """
    if not text or not text.strip():
        return []

    entries = _split_entries(text)
    results = []

    for entry in entries:
        lines = [ln.strip() for ln in entry.split("\n") if ln.strip()]
        if not lines:
            continue

        name = ""
        description_parts = []

        # First line is typically the project name (possibly with tech in parens).
        first_line = lines[0]
        # Strip bullets.
        first_line = re.sub(r"^[\-•●►▸]\s*", "", first_line).strip()

        # Check for "Project Name (Tech1, Tech2)" pattern.
        paren_match = re.match(r"^(.+?)\s*\(([^)]+)\)\s*$", first_line)
        if paren_match:
            name = paren_match.group(1).strip()
        else:
            name = first_line

        # Remaining lines form the description.
        for ln in lines[1:]:
            cleaned = re.sub(r"^[\-•●►▸]\s*", "", ln).strip()
            if cleaned:
                description_parts.append(cleaned)

        description = " ".join(description_parts)
        technologies = extract_skills(entry)

        results.append({
            "name": name,
            "description": description,
            "technologies": technologies,
        })

    return results


# -----------------------------------------------------------------------
# Certification Extractor
# -----------------------------------------------------------------------

_ISSUER_KEYWORDS = re.compile(
    r"\b(by|from|issued by|offered by|awarded by|provided by|"
    r"coursera|udemy|edx|udacity|google|microsoft|aws|amazon|"
    r"ibm|oracle|cisco|meta|linkedin|nptel|isaca|comptia|"
    r"pmi|scrum\.org|ec-council|red hat|vmware|salesforce)\b",
    re.IGNORECASE,
)


def extract_certifications(text):
    """Extract certification/training entries.

    Returns
    -------
    list[dict]
        Each dict has keys: title, issuer.
    """
    if not text or not text.strip():
        return []

    entries = _split_entries(text)
    results = []

    for entry in entries:
        lines = [ln.strip() for ln in entry.split("\n") if ln.strip()]
        if not lines:
            continue

        # Try splitting lines further by bullets within a single chunk.
        expanded = []
        for ln in lines:
            sub_items = re.split(r"\s*[•●►▸]\s*", ln)
            for item in sub_items:
                item = item.strip()
                if item:
                    expanded.append(item)

        if not expanded:
            continue

        for item in expanded:
            item = re.sub(r"^[\-•●►▸\d\.\)]\s*", "", item).strip()
            if not item or len(item) < 3:
                continue

            title = item
            issuer = ""

            # Try "Title — Issuer" or "Title | Issuer" or "Title, Issuer".
            for sep in [" — ", " – ", " - ", " | ", ", "]:
                if sep in item:
                    parts = item.split(sep, 1)
                    if len(parts) == 2:
                        p1, p2 = parts[0].strip(), parts[1].strip()
                        if _ISSUER_KEYWORDS.search(p2):
                            title = p1
                            issuer = p2
                            break

            # Try "Title by/from Issuer" pattern.
            if not issuer:
                by_match = re.search(
                    r"(.+?)\s+(?:by|from|issued by|offered by)\s+(.+)",
                    item,
                    re.IGNORECASE,
                )
                if by_match:
                    title = by_match.group(1).strip()
                    issuer = by_match.group(2).strip()

            results.append({
                "title": title,
                "issuer": issuer,
            })

    return results


# -----------------------------------------------------------------------
# Education Extractor
# -----------------------------------------------------------------------

_DEGREE_PATTERN = re.compile(
    r"\b(B\.?Tech|B\.?E\.?|B\.?Sc|B\.?S\.?|B\.?A\.?|B\.?Com|BCA|BBA|"
    r"M\.?Tech|M\.?E\.?|M\.?Sc|M\.?S\.?|M\.?A\.?|M\.?Com|MCA|MBA|"
    r"Ph\.?D|Diploma|HSC|SSC|12th|10th|"
    r"Bachelor(?:'?s)?|Master(?:'?s)?|Doctorate)\b",
    re.IGNORECASE,
)


def extract_education(text):
    """Extract education entries.

    Returns
    -------
    list[dict]
        Each dict has keys: degree, institution, coursework.
    """
    if not text or not text.strip():
        return []

    entries = _split_entries(text)
    results = []

    for entry in entries:
        lines = [ln.strip() for ln in entry.split("\n") if ln.strip()]
        if not lines:
            continue

        degree = ""
        institution = ""
        coursework = []

        full_text = " ".join(lines)

        # Try to find a degree.
        deg_match = _DEGREE_PATTERN.search(full_text)
        if deg_match:
            # Extend to capture "B.Tech in Computer Science" etc.
            after_deg = full_text[deg_match.start():]
            in_match = re.match(
                r"([\w.\s']+?(?:\s+(?:in|of)\s+[\w\s&,]+)?)",
                after_deg,
            )
            if in_match:
                degree = in_match.group(1).strip()
            else:
                degree = deg_match.group(0)

        # First line often contains institution name.
        first_line = lines[0]
        if not _DEGREE_PATTERN.search(first_line):
            institution = first_line
        elif len(lines) > 1:
            # The second line might be the institution.
            second = lines[1]
            if not _DEGREE_PATTERN.search(second):
                institution = second

        # Look for coursework keywords.
        for ln in lines:
            lower = ln.lower()
            if "coursework" in lower or "courses" in lower or "subjects" in lower:
                # Extract the part after the keyword.
                cw_match = re.search(
                    r"(?:coursework|courses|subjects)\s*[:\-–—]\s*(.+)",
                    ln,
                    re.IGNORECASE,
                )
                if cw_match:
                    items = re.split(r"[,;|]", cw_match.group(1))
                    coursework.extend([c.strip() for c in items if c.strip()])

        results.append({
            "degree": degree,
            "institution": institution,
            "coursework": coursework,
        })

    return results
