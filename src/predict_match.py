
import joblib
from pathlib import Path

# Load the saved ML model
MODEL_PATH = Path("models/resume_matcher.joblib")

model = joblib.load(MODEL_PATH)

# Match labels
LABELS = {
    0: "Poor Match",
    1: "Partial Match",
    2: "Strong Match"
}


def predict_match(resume_text, job_description):
    # Combine resume and job description
    combined_text = (
        f"Resume: {resume_text} "
        f"Job: {job_description}"
    )

    # Predict match category
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

    result = predict_match(resume_text, job_description)

    print("\n========== MATCH RESULT ==========")
    print("Predicted category:", result)
    print("Note: Experimental model; not a hiring decision.")


if __name__ == "__main__":
    main()
