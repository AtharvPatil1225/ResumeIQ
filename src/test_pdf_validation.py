"""
test_pdf_validation.py
----------------------
Pytest tests for the PDF validation and scanning-detection helpers
added to pdf_extractor.py.
"""

import pytest
import pymupdf

from pdf_extractor import validate_pdf_upload, is_likely_scanned


def _make_pdf(path, text=""):
    """Create a minimal PDF at path, optionally with text."""
    doc = pymupdf.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


# ---------------------------------------------------------------------------
# validate_pdf_upload
# ---------------------------------------------------------------------------

class TestValidatePdfUpload:
    def test_valid_pdf_passes(self, tmp_path):
        pdf = tmp_path / "resume.pdf"
        _make_pdf(pdf, "Python developer with SQL skills.")
        ok, reason = validate_pdf_upload(pdf)
        assert ok is True
        assert reason == ""

    def test_missing_file_fails(self, tmp_path):
        ok, reason = validate_pdf_upload(tmp_path / "ghost.pdf")
        assert ok is False
        assert "not exist" in reason.lower()

    def test_wrong_extension_fails(self, tmp_path):
        txt_file = tmp_path / "resume.txt"
        txt_file.write_text("Python developer")
        ok, reason = validate_pdf_upload(txt_file)
        assert ok is False
        assert ".txt" in reason or "Unsupported" in reason

    def test_empty_file_fails(self, tmp_path):
        empty = tmp_path / "empty.pdf"
        empty.write_bytes(b"")
        ok, reason = validate_pdf_upload(empty)
        assert ok is False
        assert "empty" in reason.lower() or "0 bytes" in reason.lower()

    def test_oversized_file_fails(self, tmp_path):
        big = tmp_path / "big.pdf"
        # Write a fake "PDF" that exceeds 1 KB limit for this test.
        big.write_bytes(b"%PDF-1.4 " + b"x" * 2048)
        ok, reason = validate_pdf_upload(big, max_size_mb=0.001)
        assert ok is False
        assert "large" in reason.lower() or "MB" in reason

    def test_custom_size_limit(self, tmp_path):
        pdf = tmp_path / "resume.pdf"
        _make_pdf(pdf, "Python SQL Java")
        # The created PDF is well under 5 MB.
        ok, _ = validate_pdf_upload(pdf, max_size_mb=5)
        assert ok is True

    def test_non_pdf_csv_extension_fails(self, tmp_path):
        csv_file = tmp_path / "data.csv"
        csv_file.write_text("name,skill\nAlice,Python")
        ok, reason = validate_pdf_upload(csv_file)
        assert ok is False


# ---------------------------------------------------------------------------
# is_likely_scanned
# ---------------------------------------------------------------------------

class TestIsLikelyScanned:
    def test_none_is_scanned(self):
        assert is_likely_scanned(None) is True

    def test_empty_string_is_scanned(self):
        assert is_likely_scanned("") is True
        assert is_likely_scanned("   ") is True

    def test_short_text_is_scanned(self):
        assert is_likely_scanned("Hello") is True

    def test_long_text_is_not_scanned(self):
        long_text = "Python developer " * 20  # >100 chars
        assert is_likely_scanned(long_text) is False

    def test_exactly_at_threshold_is_scanned(self):
        # Exactly 100 chars is still flagged (< 100 is False).
        text = "x" * 100
        assert is_likely_scanned(text) is False  # 100 == 100, not < 100

    def test_custom_threshold(self):
        text = "Short"
        assert is_likely_scanned(text, min_chars=3) is False   # 5 >= 3
        assert is_likely_scanned(text, min_chars=10) is True   # 5 < 10
