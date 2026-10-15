import joblib
from pathlib import Path

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "resume_matcher.joblib"
LABELS = {0: "Poor Match", 1: "Partial Match", 2: "Strong Match"}


def predict_match(resume_text, job_description, model=None):
    if not isinstance(resume_text, str) or not resume_text.strip():
        raise ValueError("Resume text cannot be empty.")
    if not isinstance(job_description, str) or not job_description.strip():
        raise ValueError("Job description cannot be empty.")
    if model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Trained model not found: {MODEL_PATH}. Run src/train_model.py first.")
        model = joblib.load(MODEL_PATH)
    combined_text = f"Resume: {resume_text} Job: {job_description}"
    prediction = int(model.predict([combined_text])[0])
    return LABELS[prediction]


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
    except (FileNotFoundError, ValueError) as error:
        print(f"\nError: {error}")
        return
    print("\n========== MATCH RESULT ==========")
    print("Predicted category:", result)
    print("Note: Experimental model; not a hiring decision.")


if __name__ == "__main__":
    main()
