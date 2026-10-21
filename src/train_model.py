"""
train_model.py
--------------
Train and compare two scikit-learn pipelines on the synthetic resume-job
matching dataset:

  1. TF-IDF + Logistic Regression  (LR)
  2. TF-IDF + Linear Support Vector Machine  (LinearSVC)

The model with the higher mean stratified cross-validation accuracy is
saved as the production artifact at <project_root>/models/resume_matcher.joblib.
A confusion matrix PNG is written to <project_root>/reports/.

IMPORTANT: Results obtained on synthetic data do not establish real-world
matching accuracy.  Treat them as pipeline smoke-tests only.
"""

import joblib
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")          # non-interactive backend, safe for CI
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline


LABEL_NAMES = ["Poor match", "Partial match", "Strong match"]


def _build_pipelines():
    """Return a dict of {name: Pipeline} for each candidate model."""
    tfidf = dict(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
    )
    return {
        "Logistic Regression": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf)),
            ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
        ]),
        "Linear SVM": Pipeline([
            ("tfidf", TfidfVectorizer(**tfidf)),
            ("classifier", LinearSVC(max_iter=2000, random_state=42)),
        ]),
    }


def _save_confusion_matrix(y_true, y_pred, model_name, reports_dir):
    """Save a confusion matrix PNG to reports_dir."""
    reports_dir.mkdir(parents=True, exist_ok=True)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=LABEL_NAMES,
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, colorbar=True)
    ax.set_title(f"Confusion Matrix — {model_name}\n(synthetic data only)")
    plt.tight_layout()
    safe_name = model_name.lower().replace(" ", "_")
    out_path = reports_dir / f"confusion_matrix_{safe_name}.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path


def main():
    project_folder = Path(__file__).resolve().parent.parent
    dataset_path = (
        project_folder
        / "data"
        / "training"
        / "resume_job_pairs_expanded.csv"
    )

    print("ResumeIQ - ML Model Training")
    print("=" * 40)

    if not dataset_path.exists():
        print("Training dataset not found:", dataset_path)
        print("Run 'python src/generate_training_data.py' first.")
        return

    df = pd.read_csv(dataset_path)

    required_columns = ["resume_text", "job_description", "match_label"]
    if not all(col in df.columns for col in required_columns):
        print("CSV is missing required columns:", required_columns)
        return

    if df[required_columns].isnull().any().any():
        print("Required values are missing.")
        return

    df["resume_text"] = df["resume_text"].astype(str).str.strip()
    df["job_description"] = df["job_description"].astype(str).str.strip()

    if df["resume_text"].eq("").any() or df["job_description"].eq("").any():
        print("Empty resume text or job description found.")
        return

    df["match_label"] = pd.to_numeric(df["match_label"], errors="coerce")
    if df["match_label"].isnull().any() or not df["match_label"].isin([0, 1, 2]).all():
        print("Labels must be 0, 1, or 2.")
        return

    if df["match_label"].value_counts().min() < 2:
        print("At least two examples per label are required.")
        return

    print(f"Dataset loaded: {len(df)} examples")
    print("\nExamples per label:")
    print(df["match_label"].value_counts().sort_index())

    # Build combined feature: prefix helps the model distinguish sources.
    X = "Resume: " + df["resume_text"] + " Job: " + df["job_description"]
    y = df["match_label"].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=42, stratify=y,
    )

    pipelines = _build_pipelines()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_results = {}

    print("\n--- Cross-Validation (5-fold, stratified) ---")
    for name, pipe in pipelines.items():
        scores = cross_val_score(pipe, X_train, y_train, cv=cv, scoring="accuracy")
        cv_results[name] = scores
        print(
            f"{name:25s}  mean={scores.mean():.3f}  "
            f"std={scores.std():.3f}  scores={np.round(scores, 3)}"
        )

    # Select the best model by mean CV accuracy.
    best_name = max(cv_results, key=lambda k: cv_results[k].mean())
    print(f"\nBest model by CV: {best_name}")

    reports_dir = project_folder / "reports"
    model_dir = project_folder / "models"
    model_dir.mkdir(parents=True, exist_ok=True)

    print("\n--- Final Evaluation on Held-Out Test Set ---")
    for name, pipe in pipelines.items():
        pipe.fit(X_train, y_train)
        preds = pipe.predict(X_test)

        print(f"\n{'=' * 40}")
        print(f"Model: {name}")
        print(f"Test accuracy: {accuracy_score(y_test, preds) * 100:.2f}%")
        print("\nClassification report:")
        print(
            classification_report(
                y_test, preds,
                labels=[0, 1, 2],
                target_names=LABEL_NAMES,
                zero_division=0,
            )
        )
        print("Confusion matrix (rows=actual, columns=predicted):")
        print(confusion_matrix(y_test, preds, labels=[0, 1, 2]))

        # Save confusion matrix PNG
        png_path = _save_confusion_matrix(y_test, preds, name, reports_dir)
        print(f"Confusion matrix saved: {png_path}")

        # Save best model
        if name == best_name:
            model_path = model_dir / "resume_matcher.joblib"
            joblib.dump(pipe, model_path)
            print(f"\nBest model saved: {model_path}")

    print("\n" + "=" * 40)
    print("IMPORTANT: These results are synthetic-data experiments only.")
    print("They do not establish real-world matching accuracy.")


if __name__ == "__main__":
    main()
