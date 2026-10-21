"""
pdf_extractor.py
----------------
PDF text extraction and basic validation for ResumeIQ.

Functions
---------
extract_text_from_pdf(pdf_path)
    Extract raw text from a PDF file.
inspect_pdf_folder(folder_path)
    Return aggregate extraction statistics for a folder of PDFs.
validate_pdf_upload(file_path, max_size_mb=10)
    Validate that a file is a PDF within the allowed size limit.
is_likely_scanned(text, min_chars=100)
    Heuristic: return True when extracted text is too short to be useful.
"""

from pathlib import Path
import pymupdf

# Maximum allowed upload size (bytes).
MAX_PDF_SIZE_BYTES = 10 * 1024 * 1024   # 10 MB


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF without printing its contents.

    Parameters
    ----------
    pdf_path : str or Path

    Returns
    -------
    str or None
        Extracted text, an empty string for a blank PDF, or None on failure.
    """
    path = Path(pdf_path)
    if not path.is_file() or path.suffix.lower() != ".pdf":
        return None

    try:
        with pymupdf.open(path) as pdf:
            text = "\n".join(
                page.get_text() for page in pdf
            )
        return text.strip()
    except Exception:
        return None


def inspect_pdf_folder(folder_path):
    """Return aggregate PDF extraction statistics.

    Parameters
    ----------
    folder_path : str or Path

    Returns
    -------
    dict
        Keys: total, readable, empty, failed.
    """
    folder = Path(folder_path)
    pdf_files = list(folder.glob("*.pdf"))

    readable = 0
    empty = 0
    failed = 0

    for pdf_path in pdf_files:
        text = extract_text_from_pdf(pdf_path)

        if text is None:
            failed += 1
        elif text:
            readable += 1
        else:
            empty += 1

    return {
        "total": len(pdf_files),
        "readable": readable,
        "empty": empty,
        "failed": failed,
    }


def validate_pdf_upload(file_path, max_size_mb=10):
    """
    Validate that a file is a PDF within the allowed size limit.

    Parameters
    ----------
    file_path : str or Path
        Path to the uploaded file.
    max_size_mb : int or float, optional
        Maximum allowed file size in megabytes.  Default is 10.

    Returns
    -------
    tuple[bool, str]
        (True, "") if valid.
        (False, reason) if invalid, where reason is a human-readable message.
    """
    path = Path(file_path)

    if not path.exists():
        return False, "File does not exist."

    if path.suffix.lower() != ".pdf":
        return False, (
            f"Unsupported file type '{path.suffix}'. "
            "Only PDF files are accepted."
        )

    max_bytes = int(max_size_mb * 1024 * 1024)
    size = path.stat().st_size
    if size > max_bytes:
        size_mb = size / (1024 * 1024)
        return False, (
            f"File is too large ({size_mb:.1f} MB). "
            f"Maximum allowed size is {max_size_mb} MB."
        )

    if size == 0:
        return False, "File is empty (0 bytes)."

    return True, ""


def is_likely_scanned(text, min_chars=100):
    """
    Heuristic to detect PDFs that are probably scanned images.

    A PDF is considered likely scanned when the extracted text is shorter
    than min_chars characters after stripping whitespace.

    Parameters
    ----------
    text : str or None
        Extracted text from a PDF page.
    min_chars : int, optional
        Minimum character count to consider the text usable.  Default 100.

    Returns
    -------
    bool
        True if the text appears too short to be useful (likely scanned).
    """
    if not text:
        return True
    return len(text.strip()) < min_chars


if __name__ == "__main__":
    print("ResumeIQ PDF extractor is ready!")
