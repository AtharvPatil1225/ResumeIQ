
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
        project_folder / "data" / "training" / "resume_job_pairs.csv"
    )

    df = pd.read_csv(dataset_path)
    df["combined_text"] = (
        df["resume_text"].str.strip()
        + " "
        + df["job_description"].str.strip()
    )

    X = df["combined_text"]
    y = df["match_label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=1 / 3,
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
        ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
    ])

    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    print("ResumeIQ - Model Evaluation")
    print("=" * 35)
    print(f"Test examples: {len(y_test)}")
    print(f"Accuracy: {accuracy_score(y_test, predictions):.2f}")

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1, 2],
            target_names=["Weak match", "Partial match", "Strong match"],
            zero_division=0,
        )
    )

    print("Confusion matrix:")
    print(confusion_matrix(y_test, predictions, labels=[0, 1, 2]))

    print("\nReminder: these results are not real-world performance metrics.")


if __name__ == "__main__":
    main()
