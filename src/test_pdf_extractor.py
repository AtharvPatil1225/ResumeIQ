import pymupdf

from pdf_extractor import extract_text_from_pdf, inspect_pdf_folder


def test_extract_text_from_generated_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Synthetic PDF extraction fixture")
    document.save(pdf_path)
    document.close()
    assert extract_text_from_pdf(pdf_path) == "Synthetic PDF extraction fixture"


def test_inspect_folder_reports_aggregate_counts(tmp_path):
    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Synthetic fixture")
    document.save(tmp_path / "readable.pdf")
    document.close()
    (tmp_path / "not-a-pdf.pdf").write_text("invalid", encoding="utf-8")
    result = inspect_pdf_folder(tmp_path)
    assert result == {"total": 2, "readable": 1, "empty": 0, "failed": 1}
