"""
composite_scorer.py
-------------------
Combine per-section scores into a single weighted overall match score.

Technique: Weighted average with configurable weights and proportional
redistribution for missing sections.

Default Weights
~~~~~~~~~~~~~~~
    Skills          35%
    Projects        25%
    Internships     20%
    Certifications  10%
    Education       10%

Weight Normalization Policy
~~~~~~~~~~~~~~~~~~~~~~~~~~~
When a resume section is missing (i.e. not detected), its weight is
redistributed **proportionally** among the remaining present sections.

Example: if "certifications" (10%) is missing, the remaining sections
have base weights summing to 90%.  Each remaining section's effective
weight becomes::

    effective_weight_i = base_weight_i / sum(base_weights_of_present)

This ensures the overall score always reflects only sections that exist
in the resume.  A resume is never penalised for the *absence* of a
section heading — only for poor content quality in sections that are
present.

Double-Counting Prevention
~~~~~~~~~~~~~~~~~~~~~~~~~~
Each skill is attributed to the *first* section where it appears when
walking sections in priority order: skills → experience → projects →
certifications → education.  If a skill appears in multiple sections,
it is counted in the first section only, unless the caller explicitly
enables multi-attribution.

Limitations
~~~~~~~~~~~
- Weights are heuristic defaults, not empirically validated.
- The system does not model how sections interact (e.g. projects that
  compensate for missing internships).
- Section detection depends on heading-matching heuristics and may miss
  unconventional resume layouts.
"""

from section_parser import (
    parse_sections,
    get_section_text,
    SKILLS,
    EXPERIENCE,
    PROJECTS,
    CERTIFICATIONS,
    EDUCATION,
    ACHIEVEMENTS,
)
from jd_analyzer import analyze_job_description
from section_scorer import (
    score_skills,
    score_projects,
    score_experience,
    score_certifications,
    score_education,
    score_achievements,
)

# Default section weights (must sum to 1.0).
DEFAULT_WEIGHTS = {
    SKILLS: 0.35,
    PROJECTS: 0.25,
    EXPERIENCE: 0.20,
    CERTIFICATIONS: 0.10,
    EDUCATION: 0.10,
}

# Section evaluation order for double-counting prevention.
_SECTION_ORDER = [SKILLS, EXPERIENCE, PROJECTS, CERTIFICATIONS, EDUCATION]


def compute_composite_score(
    resume_text,
    job_description,
    weights=None,
    include_achievements=True,
):
    """Compute a weighted composite match score with per-section breakdown.

    Parameters
    ----------
    resume_text : str
        Full cleaned resume text.
    job_description : str
        Full job description text.
    weights : dict, optional
        Custom section weights.  Keys must be canonical section names.
        Values should be floats that will be normalised to sum to 1.0.
        Defaults to DEFAULT_WEIGHTS.
    include_achievements : bool
        If True and an achievements section is found, its similarity
        score is included as a bonus (unweighted additive, max +5 points)
        rather than competing with the main weighted sections.

    Returns
    -------
    dict
        Keys:
        - ``overall_score``       : float (0–100)
        - ``section_scores``      : dict mapping section name → scorer output
        - ``present_sections``    : list[str]
        - ``missing_sections``    : list[str]
        - ``effective_weights``   : dict mapping section name → float
        - ``weight_policy``       : str — explanation of weight normalisation
        - ``jd_analysis``         : dict — parsed JD
        - ``formula``             : str — the formula used
    """
    if not resume_text or not resume_text.strip():
        return _empty_result(job_description)
    if not job_description or not job_description.strip():
        return _empty_result(job_description)

    # Parse resume into sections.
    sections = parse_sections(resume_text)

    # Analyse JD.
    jd_analysis = analyze_job_description(job_description)

    # Determine which sections are present.
    base_weights = dict(weights or DEFAULT_WEIGHTS)
    present = {}
    missing = []

    for section_name in base_weights:
        text = get_section_text(sections, section_name)
        if text:
            present[section_name] = text
        else:
            missing.append(section_name)

    # Normalise weights for present sections only.
    total_present_weight = sum(
        base_weights[s] for s in present
    )
    effective_weights = {}
    if total_present_weight > 0:
        for s in present:
            effective_weights[s] = base_weights[s] / total_present_weight
    else:
        # No sections found — fall back to scoring the full resume text.
        effective_weights[SKILLS] = 1.0
        present[SKILLS] = resume_text
        if SKILLS in missing:
            missing.remove(SKILLS)

    # Score each present section.
    section_scores = {}
    claimed_skills = set()  # For double-counting prevention.

    for section_name in _SECTION_ORDER:
        if section_name not in present:
            continue

        section_text = present[section_name]

        if section_name == SKILLS:
            result = score_skills(section_text, jd_analysis)
        elif section_name == EXPERIENCE:
            result = score_experience(section_text, jd_analysis, excluded_skills=claimed_skills)
        elif section_name == PROJECTS:
            result = score_projects(section_text, jd_analysis, excluded_skills=claimed_skills)
        elif section_name == CERTIFICATIONS:
            result = score_certifications(section_text, jd_analysis, excluded_skills=claimed_skills)
        elif section_name == EDUCATION:
            result = score_education(section_text, jd_analysis, excluded_skills=claimed_skills)
        else:
            continue

        # Double-counting prevention: remove already-claimed skills from
        # this section's "matched" list (but don't alter the score — the
        # TF-IDF component is text-level, not skill-level).
        unique_matched = list(result.get("matched", []))
        claimed_skills.update(unique_matched)
        result["unique_matched"] = unique_matched

        section_scores[section_name] = result

    # Compute weighted overall score.
    overall = 0.0
    for section_name, weight in effective_weights.items():
        if section_name in section_scores:
            overall += weight * section_scores[section_name]["score"]

    # Optional achievements bonus.
    achievements_text = get_section_text(sections, ACHIEVEMENTS)
    if include_achievements and achievements_text:
        ach_result = score_achievements(achievements_text, jd_analysis)
        section_scores[ACHIEVEMENTS] = ach_result
        # Add up to 5 bonus points based on relevance.
        bonus = min(ach_result["score"] * 0.05, 5.0)
        overall = min(overall + bonus, 100.0)

    overall = min(overall, 100.0)

    # Build formula string.
    formula_parts = []
    for s, w in effective_weights.items():
        if s in section_scores:
            formula_parts.append(
                f"{w:.0%} × {s}({section_scores[s]['score']:.1f})"
            )
    formula = " + ".join(formula_parts)
    if include_achievements and ACHIEVEMENTS in section_scores:
        formula += f" + bonus({min(section_scores[ACHIEVEMENTS]['score'] * 0.05, 5.0):.1f})"

    weight_policy = (
        "Missing sections are excluded and their weights are redistributed "
        "proportionally among present sections. "
        f"Missing: {missing if missing else 'none'}. "
        f"Present weights normalised from base sum "
        f"{total_present_weight:.2f} to 1.0."
    )

    return {
        "overall_score": round(overall, 2),
        "section_scores": section_scores,
        "present_sections": list(present.keys()),
        "missing_sections": missing,
        "effective_weights": effective_weights,
        "weight_policy": weight_policy,
        "jd_analysis": jd_analysis,
        "formula": formula,
    }


def _empty_result(job_description):
    """Return a zero-score result for empty inputs."""
    return {
        "overall_score": 0.0,
        "section_scores": {},
        "present_sections": [],
        "missing_sections": list(DEFAULT_WEIGHTS.keys()),
        "effective_weights": {},
        "weight_policy": "No resume text provided.",
        "jd_analysis": analyze_job_description(job_description or ""),
        "formula": "N/A (empty input)",
    }
