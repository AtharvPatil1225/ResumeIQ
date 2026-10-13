import pytest
from matching_engine import match_resume_to_job


resume = """
Python developer with experience in SQL, Git, GitHub,
HTML, CSS, and React. Built web applications using Python.
"""

job_description = """
Junior Python Developer required.
Skills: Python, SQL, Git, GitHub, HTML, CSS, React.
"""


def test_full_skill_match():
    result = match_resume_to_job(resume, job_description)

    assert result["skill_coverage_percentage"] == 100.0
    assert set(result["matched_skills"]) == {
        "Python", "SQL", "Git", "GitHub",
        "HTML", "CSS", "React"
    }
    assert result["missing_skills"] == []


@pytest.mark.parametrize(
    "resume_text, job_text",
    [
        ("", "Python developer required."),
        ("   ", "Python developer required."),
        ("Python developer with SQL.", ""),
        ("Python developer with SQL.", "   "),
    ],
)
def test_invalid_inputs(resume_text, job_text):
    with pytest.raises(ValueError):
        match_resume_to_job(resume_text, job_text)


def test_no_skill_overlap():
    resume_text = (
        "Experienced graphic designer specializing in illustration."
    )
    job_text = "Python developer required with SQL and React skills."

    result = match_resume_to_job(resume_text, job_text)

    assert result["matched_skills"] == []
    assert result["skill_coverage_percentage"] == 0.0
    assert set(result["missing_skills"]) == {
        "Python", "SQL", "React"
    }


def test_partial_skill_overlap():
    resume_text = (
        "Python developer with experience in application development."
    )
    job_text = "Required skills: Python, SQL, and React."

    result = match_resume_to_job(resume_text, job_text)

    assert result["matched_skills"] == ["Python"]
    assert abs(result["skill_coverage_percentage"] - 33.33) < 0.01
    assert set(result["missing_skills"]) == {"React", "SQL"}
