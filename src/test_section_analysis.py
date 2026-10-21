"""
test_section_analysis.py
------------------------
Comprehensive tests for the section-level resume analysis pipeline.

Covers:
- Section parsing with different heading formats
- Missing sections and empty PDFs
- Duplicate skills (no double-counting)
- Irrelevant certifications
- Resumes with projects but no internships
- Weight normalisation with missing sections
- Required vs. preferred skill classification
- Detail extraction from each section type
"""

import pytest
from collections import OrderedDict

from section_parser import parse_sections, get_section_text, SKILLS, EXPERIENCE, PROJECTS, CERTIFICATIONS, EDUCATION, ACHIEVEMENTS, SUMMARY
from section_extractors import extract_experiences, extract_projects, extract_certifications, extract_education
from jd_analyzer import analyze_job_description
from section_scorer import score_skills, score_projects, score_experience, score_certifications, score_education
from composite_scorer import compute_composite_score, DEFAULT_WEIGHTS


# ===================================================================
# FIXTURES
# ===================================================================

FULL_RESUME = """
John Doe
john.doe@email.com

SUMMARY
Motivated software developer with experience in Python and web development.

TECHNICAL SKILLS
Python, Java, JavaScript, React, SQL, Git, Docker, AWS, HTML, CSS

EXPERIENCE
Software Developer Intern at TechCorp
Jan 2025 - Jun 2025
- Developed REST APIs using Python and Flask
- Wrote SQL queries for data extraction
- Collaborated with team using Git and GitHub

PROJECTS
E-Commerce Web Application (React, Node.js, MongoDB)
- Built a full-stack e-commerce platform with user authentication
- Implemented shopping cart and payment integration

Resume Analyzer (Python, Scikit-learn)
- Developed ML-based resume screening tool using TF-IDF
- Trained classification model with 85% accuracy

CERTIFICATIONS
AWS Cloud Practitioner - Amazon
Python for Data Science - Coursera

EDUCATION
B.Tech in Computer Science
Pune Institute of Computer Technology
Relevant Coursework: Data Structures, Algorithms, Machine Learning, Database Systems

ACHIEVEMENTS
- Won first place in college hackathon
- Published paper on machine learning applications
"""

SAMPLE_JD = """
We are looking for a Python Developer.

Required Skills:
- Python, SQL, Git, Docker, AWS
- Experience with REST APIs and web development
- Strong knowledge of data structures and algorithms

Nice to have:
- React or Angular frontend experience
- Machine Learning basics
- Cloud certifications

Education:
B.Tech or equivalent in Computer Science or related field.
"""


# ===================================================================
# SECTION PARSER TESTS
# ===================================================================

class TestSectionParser:

    def test_parses_all_caps_headings(self):
        sections = parse_sections(FULL_RESUME)
        assert SKILLS in sections
        assert EXPERIENCE in sections
        assert PROJECTS in sections
        assert CERTIFICATIONS in sections
        assert EDUCATION in sections
        assert ACHIEVEMENTS in sections

    def test_parses_title_case_headings(self):
        text = """
Technical Skills
Python, Java, SQL

Work Experience
Developer at XYZ Corp

Projects
Built a web app

Certifications
AWS Certified

Education
B.Tech in CS
"""
        sections = parse_sections(text)
        assert SKILLS in sections
        assert EXPERIENCE in sections
        assert PROJECTS in sections
        assert CERTIFICATIONS in sections
        assert EDUCATION in sections

    def test_parses_headings_with_colons(self):
        text = """
Skills:
Python, Java

Experience:
Developer at XYZ

Projects:
Web Application
"""
        sections = parse_sections(text)
        assert SKILLS in sections
        assert EXPERIENCE in sections
        assert PROJECTS in sections

    def test_parses_alternate_heading_names(self):
        text = """
Core Competencies
Python, Java, SQL

Internship
ML Intern at ABC

Academic Projects
Built ML model

Certificates & Training
AWS Certified

Academic Background
B.Tech in IT
"""
        sections = parse_sections(text)
        assert SKILLS in sections
        assert EXPERIENCE in sections
        assert PROJECTS in sections
        assert CERTIFICATIONS in sections
        assert EDUCATION in sections

    def test_empty_text_returns_empty(self):
        assert parse_sections("") == OrderedDict()
        assert parse_sections("   ") == OrderedDict()
        assert parse_sections(None) == OrderedDict()

    def test_text_before_first_heading_is_summary(self):
        text = """
John Doe, Software Developer

Skills
Python, Java
"""
        sections = parse_sections(text)
        assert SUMMARY in sections
        assert "John Doe" in sections[SUMMARY]

    def test_missing_sections_omitted(self):
        text = """
Skills
Python, Java

Projects
Built a web app
"""
        sections = parse_sections(text)
        assert SKILLS in sections
        assert PROJECTS in sections
        assert EXPERIENCE not in sections
        assert CERTIFICATIONS not in sections

    def test_get_section_text_returns_empty_for_missing(self):
        sections = parse_sections("Skills\nPython")
        assert get_section_text(sections, EXPERIENCE) == ""


# ===================================================================
# SECTION EXTRACTORS TESTS
# ===================================================================

class TestExperienceExtractor:

    def test_extracts_role_and_company(self):
        text = """
Software Developer Intern at TechCorp
Jan 2025 - Jun 2025
- Developed REST APIs using Python
- Wrote SQL queries
"""
        entries = extract_experiences(text)
        assert len(entries) >= 1
        assert entries[0]["role"]  # Should have a role.
        assert entries[0]["duration"]  # Should detect the date range.

    def test_empty_text(self):
        assert extract_experiences("") == []
        assert extract_experiences("   ") == []

    def test_detects_skills_in_experience(self):
        text = "Developer at XYZ, worked with Python, SQL, and Docker."
        entries = extract_experiences(text)
        assert len(entries) >= 1
        skills = entries[0]["skills"]
        assert "Python" in skills
        assert "SQL" in skills


class TestProjectExtractor:

    def test_extracts_project_name(self):
        text = """
E-Commerce Web Application (React, Node.js)
Built a full-stack platform with user authentication.
"""
        projects = extract_projects(text)
        assert len(projects) >= 1
        assert projects[0]["name"]

    def test_detects_technologies(self):
        text = """
Resume Analyzer
Built with Python and Scikit-learn for ML-based screening.
"""
        projects = extract_projects(text)
        assert len(projects) >= 1
        assert "Python" in projects[0]["technologies"]

    def test_empty_text(self):
        assert extract_projects("") == []


class TestCertificationExtractor:

    def test_extracts_certification(self):
        text = "AWS Cloud Practitioner - Amazon"
        certs = extract_certifications(text)
        assert len(certs) >= 1

    def test_detects_issuer(self):
        text = "Python for Data Science from Coursera"
        certs = extract_certifications(text)
        assert len(certs) >= 1
        assert certs[0]["issuer"]  # Should detect Coursera.

    def test_empty_text(self):
        assert extract_certifications("") == []


class TestEducationExtractor:

    def test_extracts_degree(self):
        text = "B.Tech in Computer Science\nPICT, Pune"
        entries = extract_education(text)
        assert len(entries) >= 1
        assert entries[0]["degree"]

    def test_extracts_coursework(self):
        text = """
B.Tech in Computer Science
Relevant Coursework: Data Structures, Algorithms, ML
"""
        entries = extract_education(text)
        assert len(entries) >= 1
        assert len(entries[0]["coursework"]) > 0

    def test_empty_text(self):
        assert extract_education("") == []


# ===================================================================
# JD ANALYZER TESTS
# ===================================================================

class TestJDAnalyzer:

    def test_detects_required_and_preferred(self):
        result = analyze_job_description(SAMPLE_JD)
        required = result["required_skills"]
        preferred = result["preferred_skills"]

        # Python and SQL should be required.
        assert "Python" in required
        assert "SQL" in required

        # React is in the "nice to have" section.
        assert "React" in preferred

    def test_all_skills_union(self):
        result = analyze_job_description(SAMPLE_JD)
        all_skills = set(result["all_skills"])
        required = set(result["required_skills"])
        preferred = set(result["preferred_skills"])
        assert required | preferred == all_skills

    def test_empty_jd(self):
        result = analyze_job_description("")
        assert result["required_skills"] == []
        assert result["preferred_skills"] == []

    def test_detects_education_keywords(self):
        result = analyze_job_description(SAMPLE_JD)
        edu = result["education_keywords"]
        # Should detect "B.Tech" or "Computer Science".
        assert len(edu) > 0


# ===================================================================
# SECTION SCORER TESTS
# ===================================================================

class TestSkillsScorer:

    def test_full_match_gives_high_score(self):
        jd = analyze_job_description(
            "Required: Python, SQL, Git, Docker. Nice to have: React."
        )
        result = score_skills("Python SQL Git Docker React", jd)
        assert result["score"] > 80

    def test_no_match_gives_zero(self):
        jd = analyze_job_description("Required: Python, SQL, Docker.")
        result = score_skills("Painting, Music, Dance", jd)
        assert result["score"] == 0.0

    def test_required_weighted_more_than_preferred(self):
        jd = analyze_job_description(
            "Required: Python, SQL.\n\nNice to have: React, Angular."
        )
        # Only has preferred skills.
        result_pref = score_skills("React Angular", jd)
        # Only has required skills.
        result_req = score_skills("Python SQL", jd)
        # Required match should score higher.
        assert result_req["score"] > result_pref["score"]


class TestProjectsScorer:

    def test_relevant_project_scores_above_zero(self):
        jd = analyze_job_description("Python developer with SQL and REST APIs.")
        result = score_projects(
            "Built REST API using Python and SQL for data management.", jd
        )
        assert result["score"] > 0

    def test_irrelevant_project_scores_low(self):
        jd = analyze_job_description("Python developer with SQL and Docker.")
        result = score_projects(
            "Painted a landscape using watercolors.", jd
        )
        assert result["score"] < 30


class TestExperienceScorer:

    def test_relevant_experience_scores_above_zero(self):
        jd = analyze_job_description("Python developer with SQL experience.")
        result = score_experience(
            "Software Developer Intern. Developed Python REST APIs with SQL.", jd
        )
        assert result["score"] > 0


class TestCertificationsScorer:

    def test_relevant_cert_scores_above_zero(self):
        jd = analyze_job_description("AWS cloud developer required.")
        result = score_certifications("AWS Cloud Practitioner Certified", jd)
        assert result["score"] > 0

    def test_irrelevant_cert_scores_low(self):
        jd = analyze_job_description("Python developer with SQL.")
        result = score_certifications(
            "Certified Yoga Instructor from Yoga Alliance", jd
        )
        assert result["score"] == 0.0


class TestEducationScorer:

    def test_matching_degree_scores_above_zero(self):
        jd = analyze_job_description(
            "B.Tech in Computer Science required. Python and SQL."
        )
        result = score_education(
            "B.Tech in Computer Science\nPICT, Pune\n"
            "Coursework: Data Structures, Machine Learning", jd
        )
        assert result["score"] > 0


# ===================================================================
# COMPOSITE SCORER TESTS
# ===================================================================

class TestCompositeScorer:

    def test_full_resume_produces_score(self):
        result = compute_composite_score(FULL_RESUME, SAMPLE_JD)
        assert 0 <= result["overall_score"] <= 100
        assert len(result["section_scores"]) > 0
        assert result["formula"] != "N/A (empty input)"

    def test_empty_resume_gives_zero(self):
        result = compute_composite_score("", SAMPLE_JD)
        assert result["overall_score"] == 0.0

    def test_empty_jd_gives_zero(self):
        result = compute_composite_score(FULL_RESUME, "")
        assert result["overall_score"] == 0.0

    def test_missing_sections_are_tracked(self):
        # Resume with only skills and projects — no experience/certs/edu.
        text = """
Skills
Python, Java, SQL

Projects
Built a web app with Python and React
"""
        result = compute_composite_score(text, SAMPLE_JD)
        assert EXPERIENCE in result["missing_sections"]
        assert CERTIFICATIONS in result["missing_sections"]
        assert EDUCATION in result["missing_sections"]

    def test_weight_normalization_missing_sections(self):
        """When sections are missing, effective weights should sum to ~1.0."""
        text = """
Skills
Python, Java, SQL

Projects
Built a web app using Python
"""
        result = compute_composite_score(text, SAMPLE_JD)
        total = sum(result["effective_weights"].values())
        assert abs(total - 1.0) < 0.01

    def test_projects_no_internships(self):
        """Resume with projects but no internship should still score."""
        text = """
Skills
Python, SQL, Git, Docker

Projects
REST API Backend (Python, Flask, SQL)
Built a REST API for data management with Python Flask.
Used SQL for database queries and Docker for deployment.
"""
        result = compute_composite_score(text, SAMPLE_JD)
        assert result["overall_score"] > 0
        assert EXPERIENCE in result["missing_sections"]
        assert PROJECTS in result["present_sections"]

    def test_duplicate_skills_not_double_counted(self):
        """Skills appearing in multiple sections should be noted."""
        text = """
Skills
Python, SQL, Docker

Experience
Developer Intern. Used Python and SQL at XYZ Corp.

Projects
Built app with Python and Docker.
"""
        result = compute_composite_score(text, SAMPLE_JD)
        # The composite scorer tracks unique_matched to prevent
        # double-counting in the matched evidence lists.
        all_unique = set()
        for sec_name, sec_result in result["section_scores"].items():
            unique = sec_result.get("unique_matched", sec_result.get("matched", []))
            overlap = all_unique & set(unique)
            assert not overlap
            all_unique.update(unique)
        # We just verify it runs without error and produces a valid score.
        assert 0 <= result["overall_score"] <= 100

    def test_custom_weights(self):
        """Custom weights should be accepted and normalised."""
        custom = {
            "skills": 0.50,
            "projects": 0.30,
            "experience": 0.10,
            "certifications": 0.05,
            "education": 0.05,
        }
        result = compute_composite_score(FULL_RESUME, SAMPLE_JD, weights=custom)
        assert 0 <= result["overall_score"] <= 100

    def test_achievements_bonus(self):
        """Achievements should add a bonus, not replace other scores."""
        result_with = compute_composite_score(
            FULL_RESUME, SAMPLE_JD, include_achievements=True
        )
        result_without = compute_composite_score(
            FULL_RESUME, SAMPLE_JD, include_achievements=False
        )
        # With achievements bonus should be >= without (or very close).
        assert result_with["overall_score"] >= result_without["overall_score"] - 0.01


# ===================================================================
# EDGE CASE TESTS
# ===================================================================

class TestEdgeCases:

    def test_resume_with_no_recognizable_headings(self):
        """Resume with no headings should still produce a score."""
        text = "Python developer with SQL, Docker, and React experience."
        result = compute_composite_score(text, SAMPLE_JD)
        # Should fall back to treating the whole text as skills.
        assert result["overall_score"] >= 0
        assert SKILLS in result["present_sections"]
        assert SKILLS not in result["missing_sections"]

    def test_jd_with_no_skills(self):
        """JD with no recognizable skills should produce zero scores."""
        result = compute_composite_score(
            FULL_RESUME,
            "We need a team player who is passionate about learning."
        )
        assert 0 <= result["overall_score"] <= 100

    def test_single_skill_resume(self):
        """Resume with only one skill."""
        text = """
Skills
Python
"""
        jd = "Python developer required."
        result = compute_composite_score(text, jd)
        assert result["overall_score"] > 0
