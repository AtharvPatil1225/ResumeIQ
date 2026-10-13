
import json
import sys
from pathlib import Path

import pymupdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESUME_ROOT = PROJECT_ROOT / "data" / "raw_resumes"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "resume_dataset.jsonl"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from skill_extractor import extract_skills


def extract_text_safely(pdf_path):
    """Extract text from a PDF, returning None on processing failure."""
    try:
        with pymupdf.open(pdf_path) as pdf:
            text = "\n".join(page.get_text("text") for page in pdf)
        return text.strip()
    except Exception:
        return None


def build_dataset():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    readable = 0
    empty = 0
    failed = 0

    with OUTPUT_FILE.open("w", encoding="utf-8") as output:
        for year in ["2026", "2027", "2028"]:
            pdf_files = sorted((RESUME_ROOT / year).glob("*.pdf"))
            year_readable = 0

            for pdf_path in pdf_files:
                total += 1
                text = extract_text_safely(pdf_path)

                if text is None:
                    failed += 1
                    continue

                if not text:
                    empty += 1
                    continue

                record = {
                    "resume_id": f"RESUME_{total:04d}",
                    "graduation_year": year,
                    "resume_text": text,
                    "detected_skills": extract_skills(text),
                }

                output.write(
                    json.dumps(record, ensure_ascii=False) + "\n"
                )

                readable += 1
                year_readable += 1

            print(
                f"Year {year}: {len(pdf_files)} PDFs, "
                f"{year_readable} readable"
            )

    print("\nDataset building completed.")
    print("Total PDFs scanned:", total)
    print("Readable resumes saved:", readable)
    print("PDFs without extractable text:", empty)
    print("PDF processing failures:", failed)
    print("Output saved to:", OUTPUT_FILE)


if __name__ == "__main__":
    build_dataset()
