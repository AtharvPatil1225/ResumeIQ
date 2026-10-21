"""
test_preprocess.py
------------------
Pytest tests for the preprocess.py text cleaning module.
Verifies that technical terms are preserved and that normal
cleaning operates correctly.
"""

import pytest
from preprocess import clean_resume_text, clean_job_description


class TestCleanResumeText:
    """Test that clean_resume_text preserves and transforms text correctly."""

    def test_returns_string_on_none(self):
        result = clean_resume_text(None)
        assert isinstance(result, str)
        assert result == ""

    def test_returns_empty_on_empty(self):
        assert clean_resume_text("") == ""
        assert clean_resume_text("   ") == ""

    def test_plain_text_unchanged(self):
        text = "Python developer with SQL experience"
        assert clean_resume_text(text) == text

    def test_preserves_cpp(self):
        text = "I know C++ and C# programming."
        result = clean_resume_text(text)
        assert "C++" in result
        assert "C#" in result

    def test_preserves_dotnet(self):
        text = "Experience with .NET framework and ASP.NET."
        result = clean_resume_text(text)
        assert ".NET" in result
        assert "ASP.NET" in result

    def test_preserves_nodejs(self):
        text = "Built REST APIs using Node.js and Express.js."
        result = clean_resume_text(text)
        assert "Node.js" in result
        assert "Express.js" in result

    def test_preserves_nextjs_nuxtjs(self):
        text = "Frontend with Next.js and Nuxt.js."
        result = clean_resume_text(text)
        assert "Next.js" in result
        assert "Nuxt.js" in result

    def test_preserves_cicd(self):
        text = "Set up CI/CD pipelines using Jenkins."
        result = clean_resume_text(text)
        assert "CI/CD" in result

    def test_preserves_rest_api(self):
        text = "Designed REST API endpoints."
        result = clean_resume_text(text)
        assert "REST API" in result

    def test_collapses_excessive_whitespace(self):
        text = "Python   developer    with   SQL"
        result = clean_resume_text(text)
        assert "  " not in result

    def test_collapses_excessive_newlines(self):
        text = "Python\n\n\n\n\nSQL"
        result = clean_resume_text(text)
        assert "\n\n\n" not in result

    def test_strips_leading_trailing_whitespace(self):
        text = "  Python developer  "
        assert clean_resume_text(text) == "Python developer"

    def test_sql_server_preserved(self):
        text = "Experience with SQL Server and MySQL."
        result = clean_resume_text(text)
        assert "SQL Server" in result
        assert "MySQL" in result

    def test_google_cloud_preserved(self):
        text = "Deployed on Google Cloud and AWS."
        result = clean_resume_text(text)
        assert "Google Cloud" in result


class TestCleanJobDescription:
    """clean_job_description delegates to clean_resume_text — smoke tests."""

    def test_basic_clean(self):
        jd = "Python, SQL, Docker, and Kubernetes experience required."
        result = clean_job_description(jd)
        assert "Python" in result
        assert "Docker" in result

    def test_preserves_technical_terms(self):
        jd = "Requires C++, .NET, and CI/CD knowledge."
        result = clean_job_description(jd)
        assert "C++" in result
        assert ".NET" in result
        assert "CI/CD" in result
