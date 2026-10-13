
import json
from pathlib import Path

from matching_engine import match_resume_to_job

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = (
    PROJECT_ROOT / "data" / "processed" / "resume_dataset.jsonl"
)


def load_resumes():
    """Load validated resume records from the JSONL dataset."""
    resumes = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line in file:
            record = json.loads(line)
            resumes.append(record)

    return resumes


def main():
    print("\nResumeIQ - Resume Analyzer & Job Matcher")
    print("=" * 45)

    if not DATASET_PATH.exists():
        print("ERROR: Validated resume dataset not found.")
        return

    try:
        resumes = load_resumes()
    except (OSError, json.JSONDecodeError) as error:
        print(f"Unable to load the dataset: {error}")
        return

    if not resumes:
        print("No resumes available in the dataset.")
        return

    print(f"\nTotal available resumes: {len(resumes)}")
    print("\nChoose a resume year:")
    print("1. 2026")
    print("2. 2027")
    print("3. 2028")

    year_options = {
        "1": "2026",
        "2": "2027",
        "3": "2028",
    }

    choice = input("\nEnter your choice (1-3): ").strip()

    if choice not in year_options:
        print("Invalid choice. Please run the program again.")
        return

    selected_year = year_options[choice]

    year_resumes = [
        resume for resume in resumes
        if str(resume.get("graduation_year")) == selected_year
    ]

    if not year_resumes:
        print("No resumes found for the selected year.")
        return

    print(
        f"\nResumes available for {selected_year}: "
        f"{len(year_resumes)}"
    )

    print("\nSelect a resume by number.")
    print("Resume IDs, filenames, and contents are hidden.")

    for index, _ in enumerate(year_resumes, start=1):
        print(f"{index}. Resume {index}")

    try:
        resume_number = int(
            input("\nEnter resume number: ").strip()
        )

        if not 1 <= resume_number <= len(year_resumes):
            print("Invalid resume number.")
            return

    except ValueError:
        print("Please enter a valid number.")
        return

    selected_resume = year_resumes[resume_number - 1]
    resume_text = selected_resume.get("resume_text", "")

    if not isinstance(resume_text, str) or not resume_text.strip():
        print("The selected resume has no usable extracted text.")
        return

    print("\nResume loaded successfully.")

    print("\nPaste the job description below.")
    print("Type END on a new line when finished.")

    job_lines = []

    while True:
        try:
            line = input()
        except EOFError:
            print("\nInput ended before the job description was completed.")
            return

        if line.strip().upper() == "END":
            break

        job_lines.append(line)

    job_description = "\n".join(job_lines).strip()

    if not job_description:
        print("The job description cannot be empty.")
        return

    try:
        result = match_resume_to_job(
            resume_text,
            job_description
        )
    except ValueError as error:
        print(f"Could not compare the texts: {error}")
        return

    print("\n" + "=" * 45)
    print("RESUMEIQ - MATCHING RESULTS")
    print("=" * 45)

    print(
        f"Text similarity: "
        f"{result['similarity_percentage']}%"
    )

    print(
        f"Detected job-skill coverage: "
        f"{result['skill_coverage_percentage']}%"
    )

    print("\nSkills detected in job description:")
    if result["job_skills_detected"]:
        for skill in result["job_skills_detected"]:
            print(f"- {skill}")
    else:
        print("- No listed skills detected.")

    print("\nMatched skills:")
    if result["matched_skills"]:
        for skill in result["matched_skills"]:
            print(f"- {skill}")
    else:
        print("- No listed matching skills detected.")

    print("\nPotential skill gaps:")
    if result["missing_skills"]:
        for skill in result["missing_skills"]:
            print(f"- {skill}")
    else:
        print("- No missing listed skills detected.")

    print("\nNote: Similarity is not a hiring probability.")
    print("Skill results depend on the predefined skill list.")


if __name__ == "__main__":
    main()
