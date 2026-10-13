
import json
from collections import Counter
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = (
    PROJECT_ROOT / "data" / "processed" / "resume_dataset.jsonl"
)


def main():
    years = ["2026", "2027", "2028"]

    year_skills = {year: Counter() for year in years}
    year_resume_counts = Counter()
    all_skills = Counter()

    print("ResumeIQ - Dataset Skill Analysis")
    print("=" * 40)

    if not DATASET_PATH.exists():
        print("ERROR: JSONL dataset not found.")
        return

    total_records = 0

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            year = str(record["graduation_year"])
            skills = record["detected_skills"]

            total_records += 1

            if year not in year_skills:
                continue

            year_resume_counts[year] += 1

            # Count each skill only once per resume.
            unique_skills = set(skills)
            year_skills[year].update(unique_skills)
            all_skills.update(unique_skills)

    for year in years:
        resume_count = year_resume_counts[year]

        print(f"\nYear: {year}")
        print(f"Readable resumes: {resume_count}")

        print("Top 5 skills:")
        if year_skills[year]:
            for skill, count in year_skills[year].most_common(5):
                percentage = count / resume_count * 100
                print(
                    f"  {skill}: {count} resumes "
                    f"({percentage:.1f}%)"
                )
        else:
            print("  No recognized skills found.")

    total_readable = sum(year_resume_counts.values())

    print("\n" + "=" * 40)
    print("OVERALL SUMMARY")
    print("Total dataset records:", total_records)
    print("Readable resumes analyzed:", total_readable)

    print("\nTop 10 skills across all years:")
    for skill, count in all_skills.most_common(10):
        percentage = (
            count / total_readable * 100
            if total_readable else 0
        )
        print(
            f"  {skill}: {count} resumes "
            f"({percentage:.1f}%)"
        )

    print("\nAnalysis completed using the validated JSONL dataset.")
    print("Resume contents and filenames were not displayed.")


if __name__ == "__main__":
    main()
