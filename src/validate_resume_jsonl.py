
import json
from pathlib import Path
from collections import Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = (
    PROJECT_ROOT / "data" / "processed" / "resume_dataset.jsonl"
)


def main():
    print("ResumeIQ - JSONL Dataset Validation")
    print("=" * 40)

    if not DATASET_PATH.exists():
        print("ERROR: Dataset file not found.")
        return

    records = []
    invalid_lines = 0
    empty_text_count = 0

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                invalid_lines += 1
                continue

            if not isinstance(record, dict):
                invalid_lines += 1
                continue

            records.append(record)

            if not str(record.get("resume_text", "")).strip():
                empty_text_count += 1

    required_fields = {
        "resume_id",
        "graduation_year",
        "resume_text",
        "detected_skills",
    }

    missing_fields = sum(
        1 for record in records
        if not required_fields.issubset(record.keys())
    )

    resume_ids = [
        record.get("resume_id", "")
        for record in records
    ]

    valid_ids = [
        resume_id for resume_id in resume_ids
        if isinstance(resume_id, str) and resume_id.strip()
    ]

    year_counts = Counter(
        str(record.get("graduation_year", "Unknown"))
        for record in records
    )

    skills_are_lists = sum(
        isinstance(record.get("detected_skills"), list)
        for record in records
    )

    print("Dataset file exists: Yes")
    print("Total records:", len(records))
    print("Invalid JSON lines:", invalid_lines)
    print("Records with missing fields:", missing_fields)
    print("Empty resume texts:", empty_text_count)
    print("Unique resume IDs:", len(set(valid_ids)))
    print("Empty or invalid resume IDs:", len(records) - len(valid_ids))
    print("Records with skills stored as lists:", skills_are_lists)

    print("\nRecords by graduation year:")
    for year in sorted(year_counts):
        print(f"{year}: {year_counts[year]}")

    duplicate_count = len(valid_ids) - len(set(valid_ids))
    print("\nDuplicate resume IDs:", duplicate_count)

    if (
        len(records) == 1309
        and invalid_lines == 0
        and missing_fields == 0
        and empty_text_count == 0
        and len(valid_ids) == len(records)
        and duplicate_count == 0
        and skills_are_lists == len(records)
    ):
        print("\nRESULT: Dataset validation PASSED.")
    else:
        print("\nRESULT: Please review the validation results.")

    print("Resume contents and filenames were not displayed.")


if __name__ == "__main__":
    main()
