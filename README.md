# ResumeIQ

ResumeIQ is an experimental resume analysis and job matching project. It includes PDF text extraction, dictionary-based skill detection, TF-IDF text similarity, and a TF-IDF plus Logistic Regression classifier.

## Setup

Use Python 3.10 or newer. From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
```

## Synthetic ML experiment

The classifier scripts expect `data/training/resume_job_pairs_expanded.csv` with `resume_text`, `job_description`, and `match_label` columns. Labels are 0 (poor), 1 (partial), and 2 (strong). Generate the bundled synthetic dataset with:

```powershell
python src/generate_training_data.py
python src/train_model.py
python src/evaluate_model.py
```

Training saves `models/resume_matcher.joblib`, which is ignored by Git. Evaluation groups examples by job description so examples sharing the same role description do not cross folds. This is only a proxy against leakage: the small synthetic dataset has six roles, templated examples, and labels assigned by construction. Its scores do not establish performance on real resumes or jobs and must not be treated as hiring evidence.

Run the interactive classifier with `python src/predict_match.py`. The separate matching engine reports lexical similarity and coverage of a predefined skill dictionary; these are not probabilities.

## Resume data and privacy

Raw resumes, extracted datasets, local models, and environment files are excluded by `.gitignore`. Do not commit resumes, extracted resume text, credentials, or other personal data. The PDF test creates a synthetic fixture in a temporary directory and does not scan local resume folders.

## CI

Jenkins installs the dependencies from `requirements.txt` and runs the pytest suite. Ensure the Windows agent has Python available on PATH.
