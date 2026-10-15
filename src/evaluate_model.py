from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import GroupKFold
from train_model import LABELS, TARGET_NAMES, build_model, combine_text, load_dataset


def main():
    print("ResumeIQ - Grouped Model Evaluation")
    print("=" * 38)
    df = load_dataset()
    X, y, groups = combine_text(df), df["match_label"], df["job_description"]
    n_groups = groups.nunique()
    if n_groups < 2:
        raise ValueError("At least two distinct job-description groups are required.")
    splitter = GroupKFold(n_splits=min(n_groups, 6))
    predictions = [None] * len(df)
    for train_idx, test_idx in splitter.split(X, y, groups):
        model = build_model()
        model.fit(X.iloc[train_idx], y.iloc[train_idx])
        fold_predictions = model.predict(X.iloc[test_idx])
        for index, prediction in zip(test_idx, fold_predictions):
            predictions[index] = int(prediction)
    print(f"Examples: {len(df)}; held-out job groups: {n_groups}")
    print(f"Grouped out-of-fold accuracy: {accuracy_score(y, predictions):.2%}")
    print(classification_report(y, predictions, labels=LABELS,
                                target_names=TARGET_NAMES, zero_division=0))
    print("Confusion matrix (rows=actual, columns=predicted):")
    print(confusion_matrix(y, predictions, labels=LABELS))
    print("Grouped folds prevent examples sharing a job description from crossing folds.")
    print("Synthetic-data results only; this is not real-world validation.")


if __name__ == "__main__":
    main()
