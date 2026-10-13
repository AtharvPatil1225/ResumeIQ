
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "processed" / "resume_dataset.csv"


def main():
    print("ResumeIQ - Dataset Validation")
    print("=" * 35)

    if not DATASET_PATH.exists():
        print("ERROR: Dataset file not found.")
        return

    df = pd.read_csv(
        DATASET_PATH,
        keep_default_na=False,
        dtype=str,
    )

    required_columns = [
        "resume_id",
        "graduation_year",
        "resume_text",
        "detected_skills",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        print("Missing columns:", missing_columns)
        return

    # Normalize text before checking whether it is empty.
    normalized_text = df["resume_text"].fillna("").str.strip()
    empty_mask = normalized_text.eq("")
    empty_rows = df.loc[empty_mask]

    print("Total records:", len(df))
    print("Columns:", list(df.columns))
    print("Unique resume IDs:", df["resume_id"].nunique())
    print("Duplicate resume IDs:", int(df["resume_id"].duplicated().sum()))
    print(
        "Empty resume IDs:",
        int(df["resume_id"].str.strip().eq("").sum()),
    )

    print("\nEmpty resume texts:", int(empty_mask.sum()))

    if not empty_rows.empty:
        print("Anonymous IDs with empty text:")
        print(empty_rows["resume_id"].tolist())

        for _, row in empty_rows.iterrows():
            print(
                f"Diagnostic: {row['resume_id']} has "
                f"{len(row['resume_text'])} characters "
                "before stripping whitespace."
            )
    else:
        print("All records contain extracted text.")

    print("\nRecords by graduation year:")
    print(df["graduation_year"].value_counts().sort_index().to_string())

    has_skills = df["detected_skills"].str.strip().ne("")
    print("\nRecords with detected skills:", int(has_skills.sum()))
    print("Records without detected skills:", int((~has_skills).sum()))

    print("\nDataset validation completed.")
    print("Resume contents and filenames are not displayed.")


if __name__ == "__main__":
    main()
