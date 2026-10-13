
from pathlib import Path
import pymupdf


def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF without printing its contents."""

    try:
        with pymupdf.open(pdf_path) as pdf:
            text = "\n".join(
                page.get_text() for page in pdf
            )

        return text.strip()

    except Exception:
        return None


def inspect_pdf_folder(folder_path):
    """Return aggregate PDF extraction statistics."""

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


if __name__ == "__main__":
    print("ResumeIQ PDF extractor is ready!")
