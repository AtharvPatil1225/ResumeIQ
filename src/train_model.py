import joblib
import pandas as pd
from pathlib import Path
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_PATH = PROJECT_ROOT / "data" / "training" / "resume_job_pairs_expanded.csv"
MODEL_PATH = PROJECT_ROOT / "models" / "resume_matcher.joblib"
LABELS = [0, 1, 2]
TARGET_NAMES = ["Poor match", "Partial match", "Strong match"]


def build_model():
    return Pipeline([
        ("tfidf", TfidfVectorizer(lowercase=True, stop_words="english", ngram_range=(1, 2))),
        ("classifier", LogisticRegression(max_iter=1000, random_state=42)),
    ])


def load_dataset(path=DATASET_PATH):
    df = pd.read_csv(path)
    required = ["resume_text", "job_description", "match_label"]
    if any(column not in df.columns for column in required):
        raise ValueError(f"Dataset must contain columns: {', '.join(required)}")
    df = df[required].copy()
    if df.isnull().any().any():
        raise ValueError("Required dataset values cannot be empty.")
    for column in ("resume_text", "job_description"):
        df[column] = df[column].astype(str).str.strip()
        if df[column].eq("").any():
            raise ValueError(f"{column} cannot contain empty values.")
    df["match_label"] = pd.to_numeric(df["match_label"], errors="raise").astype(int)
    if not df["match_label"].isin(LABELS).all():
        raise ValueError("Labels must be 0, 1, or 2.")
    if df["match_label"].value_counts().reindex(LABELS, fill_value=0).min() < 2:
        raise ValueError("At least two examples per label are required.")
    return df


def combine_text(df):
    return "Resume: " + df["resume_text"] + " Job: " + df["job_description"]


def main():
    print("ResumeIQ - ML Model Training")
    print("=" * 35)
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Training dataset not found: {DATASET_PATH}")
    df = load_dataset()
    X, y, groups = combine_text(df), df["match_label"], df["job_description"]
    splitter = GroupShuffleSplit(n_splits=1, test_size=1 / 3, random_state=42)
    train_idx, test_idx = next(splitter.split(X, y, groups))
    model = build_model()
    model.fit(X.iloc[train_idx], y.iloc[train_idx])
    predictions = model.predict(X.iloc[test_idx])
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Examples: {len(df)}; train: {len(train_idx)}; test: {len(test_idx)}")
    print(f"Held-out job groups: {groups.iloc[test_idx].nunique()}")
    print(f"Test accuracy: {accuracy_score(y.iloc[test_idx], predictions):.2%}")
    print(classification_report(y.iloc[test_idx], predictions, labels=LABELS,
                                target_names=TARGET_NAMES, zero_division=0))
    print("Confusion matrix (rows=actual, columns=predicted):")
    print(confusion_matrix(y.iloc[test_idx], predictions, labels=LABELS))
    print(f"Model saved at: {MODEL_PATH}")
    print("Synthetic-data results only; this is not real-world validation.")


if __name__ == "__main__":
    main()
