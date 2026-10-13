import joblib
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


def main():
    project_folder = Path(__file__).resolve().parent.parent
    dataset_path = (
        project_folder
        / "data"
        / "training"
        / "resume_job_pairs_expanded.csv"
    )

    print("ResumeIQ - ML Model Training")
    print("=" * 35)

    if not dataset_path.exists():
        print("Training dataset not found:", dataset_path)
        return

    df = pd.read_csv(dataset_path)

    required_columns = [
        "resume_text",
        "job_description",
        "match_label",
    ]

    if not all(column in df.columns for column in required_columns):
        print("CSV is missing required columns.")
        return

    if df[required_columns].isnull().any().any():
        print("Required values are missing.")
        return

    df["resume_text"] = df["resume_text"].astype(str).str.strip()
    df["job_description"] = (
        df["job_description"].astype(str).str.strip()
    )

    if (
        df["resume_text"].eq("").any()
        or df["job_description"].eq("").any()
    ):
        print("Empty resume text or job description found.")
        return

    df["match_label"] = pd.to_numeric(
        df["match_label"], errors="coerce"
    )

    if (
        df["match_label"].isnull().any()
        or not df["match_label"].isin([0, 1, 2]).all()
    ):
        print("Labels must be 0, 1, or 2.")
        return

    if df["match_label"].value_counts().min() < 2:
        print("At least two examples per label are required.")
        return

    print("Dataset loaded successfully.")
    print("Total examples:", len(df))
    print("\nExamples per label:")
    print(df["match_label"].value_counts().sort_index())

    # Combine the resume and job description into one text input.
    X = (
        "Resume: " + df["resume_text"]
        + " Job: " + df["job_description"]
    )
    y = df["match_label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42,
        stratify=y,
    )

    model = Pipeline([
        (
            "tfidf",
            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
            ),
        ),
        (
            "classifier",
            LogisticRegression(
                max_iter=1000,
                random_state=42,
            ),
        ),
    ])

    model.fit(X_train, y_train)
    # Save the trained model
    model_dir = Path("models")
    model_dir.mkdir(parents=True, exist_ok=True)

    model_path = model_dir / "resume_matcher.joblib"
    joblib.dump(model, model_path)

    print(f"\nModel saved successfully at: {model_path}")
    predictions = model.predict(X_test)

    print("\nModel training completed!")
    print("Training examples:", len(X_train))
    print("Testing examples:", len(X_test))

    print(
        "\nTest accuracy:",
        round(accuracy_score(y_test, predictions) * 100, 2),
        "%",
    )

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1, 2],
            target_names=["Poor match", "Partial match", "Strong match"],
            zero_division=0,
        )
    )

    print("Confusion matrix (rows = actual, columns = predicted):")
    print(confusion_matrix(y_test, predictions, labels=[0, 1, 2]))

    print("\nIMPORTANT:")
    print("These are synthetic-data experiment results only.")
    print("They do not establish real-world matching accuracy.")
    print("The trained model is saved at models/resume_matcher.joblib.")


if __name__ == "__main__":
    main()
