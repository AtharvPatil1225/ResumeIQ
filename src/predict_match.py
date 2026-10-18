"""
predict_match.py
----------------
Predict whether a resume is a poor, partial, or strong match
for a given job description using the trained ML pipeline.

The model is loaded lazily on first use to prevent import-time crashes
when the trained artifact does not yet exist.
"""

import joblib
from pathlib import Path

# Resolve the model path relative to the project root.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_MODEL_PATH = _PROJECT_ROOT / "models" / "resume_matcher.joblib"

_LABELS = {
    0: "Poor Match",
    1: "Partial Match",
    2: "Strong Match",
}

_model = None


def load_model(model_path=None):
    """
    Load and return the trained scikit-learn pipeline.

    Parameters
    ----------
    model_path : str or Path, optional
        Path to the .joblib file.  Defaults to
        <project_root>/models/resume_matcher.joblib.

    Returns
    -------
    pipeline
        Loaded scikit-learn Pipeline object.

    Raises
    ------
    FileNotFoundError
        If the model file does not exist at the specified path.
    """
    global _model
    path = Path(model_path) if model_path else _DEFAULT_MODEL_PATH
    if not path.exists():
        raise FileNotFoundError(
            f"Trained model not found at: {path}\n"
            "Run 'python src/train_model.py' to generate it first."
        )
    _model = joblib.load(path)
    return _model


def predict_match(resume_text, job_description, model_path=None):
    """
    Predict the match quality between a resume and a job description.

    Parameters
    ----------
    resume_text : str
        Extracted text from the candidate's resume.
    job_description : str
        Text of the job description.
    model_path : str or Path, optional
        Override the default model file path.

    Returns
    -------
    str
        One of: "Poor Match", "Partial Match", "Strong Match".

    Raises
    ------
    FileNotFoundError
        If no trained model is available.
    ValueError
        If either input is empty.
    """
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("resume_text cannot be empty.")
    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("job_description cannot be empty.")

    global _model
    if _model is None:
        load_model(model_path)

    combined_text = f"Resume: {resume_text} Job: {job_description}"
    prediction = int(_model.predict([combined_text])[0])
    return _LABELS.get(prediction, "Unknown")


def main():
    print("===================================")
    print(" ResumeIQ - Resume Job Matcher")
    print("===================================")

    resume_text = input("\nEnter resume skills/details: ").strip()
    job_description = input("\nEnter job description: ").strip()

    if not resume_text or not job_description:
        print("\nError: Both fields are required.")
        return

    try:
        result = predict_match(resume_text, job_description)
    except FileNotFoundError as error:
        print(f"\nError: {error}")
        return

    print("\n========== MATCH RESULT ==========")
    print("Predicted category:", result)
    print("Note: Experimental model; not a hiring decision.")


if __name__ == "__main__":
    main()
