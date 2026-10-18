"""
test_pdf_extractor.py
---------------------
Pytest tests for pdf_extractor.py.
Uses only synthetic PDFs created in-process — no real resume files required.
"""

import pytest
import pymupdf

from pdf_extractor import extract_text_from_pdf, inspect_pdf_folder


def _make_pdf(path, text=""):
    """Create a minimal PDF with optional text content."""
    doc = pymupdf.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


class TestExtractTextFromPdf:
    def test_readable_pdf_returns_text(self, tmp_path):
        pdf_path = tmp_path / "sample.pdf"
        _make_pdf(pdf_path, text="Python developer with SQL experience.")
        result = extract_text_from_pdf(pdf_path)
        assert result is not None
        assert "Python" in result

    def test_nonexistent_file_returns_none(self, tmp_path):
        result = extract_text_from_pdf(tmp_path / "missing.pdf")
        assert result is None

    def test_empty_text_pdf_returns_empty_string_or_none(self, tmp_path):
        pdf_path = tmp_path / "blank.pdf"
        _make_pdf(pdf_path, text="")
        result = extract_text_from_pdf(pdf_path)
        # A blank PDF returns None or an empty string — both are acceptable.
        assert result is None or result.strip() == ""

    def test_non_pdf_file_returns_none(self, tmp_path):
        bad_file = tmp_path / "resume.txt"
        bad_file.write_text("This is not a PDF file.")
        result = extract_text_from_pdf(bad_file)
        assert result is None


class TestInspectPdfFolder:
    def test_folder_with_readable_pdfs(self, tmp_path):
        for i in range(3):
            _make_pdf(tmp_path / f"resume_{i}.pdf", text=f"Candidate {i} Python SQL")
        stats = inspect_pdf_folder(tmp_path)
        assert stats["total"] == 3
        assert stats["readable"] == 3
        assert stats["failed"] == 0

    def test_empty_folder(self, tmp_path):
        stats = inspect_pdf_folder(tmp_path)
        assert stats["total"] == 0
        assert stats["readable"] == 0
        assert stats["empty"] == 0
        assert stats["failed"] == 0

    def test_folder_ignores_non_pdf_files(self, tmp_path):
        (tmp_path / "notes.txt").write_text("Not a PDF")
        (tmp_path / "data.csv").write_text("a,b,c")
        stats = inspect_pdf_folder(tmp_path)
        assert stats["total"] == 0
